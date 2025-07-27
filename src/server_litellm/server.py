# src/server_litellm/server.py
import os
import logging
import httpx
from typing import List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from litellm import completion
from dotenv import load_dotenv

# Load environment variables from .env file or system
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("litellm-server")

# Initialize the server
app = Server("litellm-server")

# Configuration for LiteLLM proxy
LITELLM_PROXY_URL = os.environ.get("LITELLM_PROXY_URL", "http://localhost:4000")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Optional if using proxy
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY")  # Optional for proxy authentication

# Set up LiteLLM configuration for proxy
if LITELLM_PROXY_URL:
    os.environ["OPENAI_API_BASE"] = f"{LITELLM_PROXY_URL}/v1"
    # Force all models to go through the proxy
    os.environ["LITELLM_API_BASE"] = f"{LITELLM_PROXY_URL}/v1"
    logger.info(f"Using LiteLLM proxy at: {LITELLM_PROXY_URL}")

# Supported models - both should go through the LiteLLM proxy
SUPPORTED_MODELS = [
    "gpt-4o",
    "anthropic.claude-3-7-sonnet-20250219-v1:0"  # This matches your proxy model_name exactly
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
                        "description": "The LLM model to use. Supported models: gpt-4o, anthropic.claude-3-7-sonnet-20250219-v1:0",
                        "enum": SUPPORTED_MODELS
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
                    }
                },
                "required": ["model", "messages"]
            }
        ),
        Tool(
            name="list_models",
            description="List available models from the LiteLLM proxy.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
        raise ValueError(f"Unknown tool: {name}")

async def _handle_completion(arguments: dict) -> List[TextContent]:
    """
    Handle completion requests.
    """
    try:
        # Extract and validate arguments
        model = arguments.get("model")
        messages = arguments.get("messages", [])
        temperature = arguments.get("temperature", 0.7)
        max_tokens = arguments.get("max_tokens", 1000)

        if not model:
            raise ValueError("Model parameter is required")

        # Validate that the model is supported
        if not validate_model(model):
            raise ValueError(f"Model '{model}' is not supported. Supported models: {', '.join(SUPPORTED_MODELS)}")

        if not isinstance(messages, list):
            raise ValueError("The 'messages' argument must be a list of objects with 'role' and 'content' fields.")

        # Ensure all messages have 'role' and 'content'
        for message in messages:
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                raise ValueError(f"Each message must have 'role' and 'content'. Invalid message: {message}")

        # Log the input arguments for debugging
        logger.info(f"Model: {model}, Messages count: {len(messages)}, Temperature: {temperature}")

        # Prepare completion parameters
        completion_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Add API key if available - ensure it's set in environment for LiteLLM
        if LITELLM_API_KEY:
            completion_params["api_key"] = LITELLM_API_KEY
            # Also set in environment to ensure LiteLLM picks it up
            os.environ["OPENAI_API_KEY"] = LITELLM_API_KEY
        elif OPENAI_API_KEY:
            completion_params["api_key"] = OPENAI_API_KEY

        # Call completion - use direct proxy call for Claude models to avoid Bedrock routing
        if model.startswith("anthropic.claude"):
            response = await _call_proxy_direct(model, messages, temperature, max_tokens)
        else:
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

async def _call_proxy_direct(model: str, messages: List[dict], temperature: float, max_tokens: int) -> dict:
    """
    Call the LiteLLM proxy directly for Claude models to avoid Bedrock routing.
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LITELLM_API_KEY}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LITELLM_PROXY_URL}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise RuntimeError(f"Proxy error: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Error calling proxy directly: {e}")
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

async def run_server():
    """
    Run the LiteLLM MCP server.
    """
    logger.info("Starting LiteLLM MCP server...")
    logger.info(f"Proxy URL: {LITELLM_PROXY_URL}")
    logger.info(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def main():
    """
    Main entry point for the server.
    """
    import asyncio
    asyncio.run(run_server())
