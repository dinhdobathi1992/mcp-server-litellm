# src/server_litellm/server.py
import os
import logging
import httpx
import asyncio
import argparse
from typing import List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.types import Tool, TextContent
from litellm import completion
from dotenv import load_dotenv

# Load environment variables from .env file or system
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("litellm-server")

# Log environment variable status for debugging
logger.info("Environment variable status:")
logger.info(f"LITELLM_PROXY_URL: {'SET' if os.environ.get('LITELLM_PROXY_URL') else 'NOT SET'}")
logger.info(f"LITELLM_API_KEY: {'SET' if os.environ.get('LITELLM_API_KEY') else 'NOT SET'}")
logger.info(f"OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")

# Initialize the server
app = Server("litellm-server")

# Configuration for LiteLLM proxy
LITELLM_PROXY_URL = os.environ.get("LITELLM_PROXY_URL", "http://localhost:4000")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Optional if using proxy
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY")  # Optional for proxy authentication

# Performance optimization: Create a reusable HTTP client with connection pooling
try:
    # Try to enable HTTP/2 for better performance
    HTTP_CLIENT = httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=30.0),  # Increased timeout for Claude
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        http2=True  # Enable HTTP/2 for better performance
    )
    logger.info("HTTP/2 support enabled for better performance")
except ImportError:
    # Fallback to HTTP/1.1 if HTTP/2 is not available
    HTTP_CLIENT = httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=30.0),  # Increased timeout for Claude
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        http2=False
    )
    logger.info("HTTP/2 not available, using HTTP/1.1")

# Set up LiteLLM configuration for proxy
if LITELLM_PROXY_URL:
    os.environ["OPENAI_API_BASE"] = f"{LITELLM_PROXY_URL}/v1"
    # Force all models to go through the proxy
    os.environ["LITELLM_API_BASE"] = f"{LITELLM_PROXY_URL}/v1"
    logger.info(f"Using LiteLLM proxy at: {LITELLM_PROXY_URL}")

# Supported models - Claude first as default
SUPPORTED_MODELS = [
    "anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude first as default
    "gpt-4o"
]

def validate_model(model: str) -> bool:
    """Validate if the model is supported."""
    return model in SUPPORTED_MODELS

@app.list_tools()
async def list_tools() -> List[Tool]:
    """
    List available tools for LiteLLM server.
    """
    return [
        Tool(
            name="complete",
            description="Send a completion request to a specified LLM model through LiteLLM proxy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "The LLM model to use. Claude is the default. Supported models: anthropic.claude-3-7-sonnet-20250219-v1:0, gpt-4o",
                        "enum": SUPPORTED_MODELS,
                        "default": "anthropic.claude-3-7-sonnet-20250219-v1:0"
                    },
                    "messages": {
                        "type": "array",
                        "description": "An array of conversation messages, each with 'role' and 'content'.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "description": "The role in the conversation (e.g., 'user', 'assistant')."},
                                "content": {"type": "string", "description": "The content of the message."}
                            },
                            "required": ["role", "content"]
                        }
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Controls randomness in the response (0.0 to 2.0).",
                        "default": 0.7
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum number of tokens to generate.",
                        "default": 1000
                    },
                    "stream": {
                        "type": "boolean",
                        "description": "Enable streaming for faster initial response.",
                        "default": False
                    }
                },
                "required": ["model", "messages"]
            }
        ),
        Tool(
            name="list_models",
            description="List available models supported by this MCP server.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """
    Handle tool calls for the LiteLLM server.
    """
    if name == "complete":
        return await _handle_completion(arguments)
    elif name == "list_models":
        return await _handle_list_models()
    else:
        raise RuntimeError(f"Unknown tool: {name}")

async def _handle_completion(arguments: dict) -> List[TextContent]:
    """
    Handle completion requests with enhanced error handling and logging.
    """
    try:
        model = arguments.get("model", "anthropic.claude-3-7-sonnet-20250219-v1:0")  # Default to Claude
        messages = arguments.get("messages", [])
        temperature = arguments.get("temperature", 0.7)
        max_tokens = arguments.get("max_tokens", 1000)
        stream = arguments.get("stream", False)

        # Validate model
        if not validate_model(model):
            raise RuntimeError(f"Unsupported model: {model}. Supported models: {', '.join(SUPPORTED_MODELS)}")

        # Validate messages
        if not messages or not isinstance(messages, list):
            raise RuntimeError("Messages must be a non-empty list")

        logger.info(f"Model: {model}, Messages count: {len(messages)}, Temperature: {temperature}, Stream: {stream}")

        # For Claude models, use direct proxy call for better performance
        if model == "anthropic.claude-3-7-sonnet-20250219-v1:0":
            response = await _call_proxy_direct(model, messages, temperature, max_tokens, stream)
        else:
            # For other models, use LiteLLM completion
            completion_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
            
            # Add API key if available
            if LITELLM_API_KEY:
                completion_params["api_key"] = LITELLM_API_KEY
            
            response = completion(**completion_params)

        # Extract the response text
        choices = response.get("choices", [])
        if not choices:
            raise RuntimeError("No choices returned from the model")
        
        text = choices[0].get("message", {}).get("content", "Error: No response content.")
        
        # Log usage information if available
        usage = response.get("usage", {})
        if usage:
            logger.info(f"Usage - Tokens: {usage.get('total_tokens', 'unknown')}")

        # Return the response in MCP format
        return [TextContent(type="text", text=text)]

    except Exception as e:
        logger.error(f"Error during LiteLLM completion: {e}")
        raise RuntimeError(f"LLM API error: {e}")

async def _call_proxy_direct(model: str, messages: List[dict], temperature: float, max_tokens: int, stream: bool = False) -> dict:
    """
    Call the LiteLLM proxy directly for Claude models with performance optimizations.
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LITELLM_API_KEY}"
    }
    
    try:
        logger.info(f"Calling proxy at: {LITELLM_PROXY_URL}/v1/chat/completions")
        logger.info(f"Model: {model}")
        logger.info(f"Request timeout: 120s")
        logger.info(f"Payload size: {len(str(payload))} characters")
        
        # Use the reusable HTTP client for better performance
        response = await HTTP_CLIENT.post(
            f"{LITELLM_PROXY_URL}/v1/chat/completions",
            json=payload,
            headers=headers
        )
        
        logger.info(f"Proxy response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Successfully received response from {model}")
            return result
        else:
            logger.error(f"Proxy returned error status: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            raise RuntimeError(f"Proxy error: {response.status_code} - {response.text}")
            
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error calling proxy: {e}")
        logger.error(f"Request may have been too complex for {model}")
        raise RuntimeError(f"Proxy timeout error: {e}")
    except httpx.ConnectError as e:
        logger.error(f"Connection error calling proxy: {e}")
        raise RuntimeError(f"Proxy connection error: {e}")
    except Exception as e:
        logger.error(f"Error calling proxy directly: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise RuntimeError(f"Proxy call error: {e}")

async def _handle_list_models() -> List[TextContent]:
    """
    Handle model listing requests.
    """
    try:
        models_text = "Available models in this MCP server:\n" + "\n".join(f"- {model}" for model in SUPPORTED_MODELS)
        models_text += "\n\nNote: Only these two models are supported for security and performance reasons."
        
        return [TextContent(type="text", text=models_text)]
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise RuntimeError(f"Error listing models: {e}")

async def run_server_stdio():
    """
    Run the LiteLLM MCP server with stdio transport.
    """
    logger.info("Starting LiteLLM MCP server with stdio transport...")
    logger.info(f"Proxy URL: {LITELLM_PROXY_URL}")
    logger.info(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        # Clean up the HTTP client when the server shuts down
        await HTTP_CLIENT.aclose()

async def run_server_http(host: str = "localhost", port: int = 8001):
    """
    Run the LiteLLM MCP server with HTTP transport.
    """
    logger.info(f"Starting LiteLLM MCP server with HTTP transport on {host}:{port}...")
    logger.info(f"Proxy URL: {LITELLM_PROXY_URL}")
    logger.info(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
    
    try:
        # Create HTTP transport
        transport = StreamableHTTPServerTransport(
            mcp_session_id="litellm-server-session",
            is_json_response_enabled=True
        )
        
        # Create a simple ASGI app
        async def asgi_app(scope, receive, send):
            if scope["type"] == "http":
                await transport.handle_request(scope, receive, send)
            else:
                await send({
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [(b"content-type", b"text/plain")]
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Only HTTP requests are supported"
                })
        
        # Start the server
        import uvicorn
        config = uvicorn.Config(
            asgi_app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    finally:
        # Clean up the HTTP client when the server shuts down
        await HTTP_CLIENT.aclose()

def main():
    """
    Main entry point for the server.
    """
    parser = argparse.ArgumentParser(description="LiteLLM MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio",
                       help="Transport type: stdio or http (default: stdio)")
    parser.add_argument("--host", default="localhost", help="Host for HTTP server (default: localhost)")
    parser.add_argument("--port", type=int, default=8001, help="Port for HTTP server (default: 8001)")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        asyncio.run(run_server_stdio())
    elif args.transport == "http":
        asyncio.run(run_server_http(args.host, args.port))
    else:
        logger.error(f"Unsupported transport: {args.transport}")
        exit(1)

if __name__ == "__main__":
    main()
