#!/usr/bin/env python3
"""
LiteLLM MCP Server Client Example

This script demonstrates how to interact with the LiteLLM MCP server
using the internal functions directly, since the server uses stdio transport.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, List, Optional, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server_litellm.server import _handle_completion, _handle_list_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for interacting with the LiteLLM MCP server.
    
    This client uses the internal MCP server functions directly
    since the server uses stdio transport rather than HTTP.
    """
    
    def __init__(self):
        """Initialize the MCP client."""
        self.supported_models = [
            "anthropic.claude-3-7-sonnet-20250219-v1:0",
            "gpt-4o"
        ]
        logger.info("MCP Client initialized")
    
    async def list_models(self) -> str:
        """
        List available models supported by the MCP server.
        
        Returns:
            str: Formatted string listing available models
        """
        try:
            logger.info("Listing available models...")
            result = await _handle_list_models()
            return result[0].text
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise
    
    async def complete(
        self,
        prompt: str,
        model: str = "anthropic.claude-3-7-sonnet-20250219-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Send a completion request to the MCP server.
        
        Args:
            prompt (str): The input prompt
            model (str): The model to use (defaults to Claude)
            temperature (float): Controls randomness (0.0 to 2.0)
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        try:
            logger.info(f"Sending completion request to {model}")
            
            result = await _handle_completion({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            })
            
            return result[0].text
            
        except Exception as e:
            logger.error(f"Error during completion: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic.claude-3-7-sonnet-20250219-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Send a chat request with conversation history.
        
        Args:
            messages (List[Dict[str, str]]): List of message objects with 'role' and 'content'
            model (str): The model to use
            temperature (float): Controls randomness
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        try:
            logger.info(f"Sending chat request to {model} with {len(messages)} messages")
            
            result = await _handle_completion({
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            })
            
            return result[0].text
            
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            raise


async def example_usage():
    """
    Example usage of the MCP client.
    """
    client = MCPClient()
    
    try:
        # 1. List available models
        print("🔍 Available Models:")
        print("-" * 40)
        models_info = await client.list_models()
        print(models_info)
        print()
        
        # 2. Test Claude (default model)
        print("🤖 Testing Claude:")
        print("-" * 40)
        claude_response = await client.complete(
            "Explain the concept of machine learning in simple terms.",
            model="anthropic.claude-3-7-sonnet-20250219-v1:0",
            temperature=0.3,
            max_tokens=200
        )
        print(f"Claude: {claude_response}")
        print()
        
        # 3. Test GPT-4o
        print("🤖 Testing GPT-4o:")
        print("-" * 40)
        gpt_response = await client.complete(
            "Write a short Python function to calculate fibonacci numbers.",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=200
        )
        print(f"GPT-4o: {gpt_response}")
        print()
        
        # 4. Test conversation with history
        print("💬 Testing Conversation with History:")
        print("-" * 40)
        conversation = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
            {"role": "user", "content": "What is the population of Paris?"}
        ]
        
        chat_response = await client.chat(
            conversation,
            model="anthropic.claude-3-7-sonnet-20250219-v1:0",
            temperature=0.7,
            max_tokens=150
        )
        print(f"Claude: {chat_response}")
        
    except Exception as e:
        logger.error(f"Error in example usage: {e}")
        raise


async def interactive_chat():
    """
    Interactive chat session using the MCP client.
    """
    client = MCPClient()
    conversation_history = []
    
    print("💬 Interactive Chat Session")
    print("Type 'quit' to exit, 'clear' to clear history, 'models' to list models")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                conversation_history = []
                print("🗑️  Conversation history cleared")
                continue
            elif user_input.lower() == 'models':
                models_info = await client.list_models()
                print(f"📋 {models_info}")
                continue
            elif not user_input:
                continue
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            print("🤖 Thinking...")
            
            # Get response
            response = await client.chat(
                conversation_history,
                model="anthropic.claude-3-7-sonnet-20250219-v1:0",
                temperature=0.7,
                max_tokens=500
            )
            
            # Add assistant response to history
            conversation_history.append({"role": "assistant", "content": response})
            
            print(f"🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """
    Main function with command line interface.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="LiteLLM MCP Server Client")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start interactive chat session")
    parser.add_argument("--prompt", "-p", type=str,
                       help="Send a single prompt")
    parser.add_argument("--model", "-m", type=str, 
                       default="anthropic.claude-3-7-sonnet-20250219-v1:0",
                       help="Model to use (default: Claude)")
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_chat())
    elif args.prompt:
        async def single_prompt():
            client = MCPClient()
            response = await client.complete(args.prompt, model=args.model)
            print(f"🤖 Response: {response}")
        
        asyncio.run(single_prompt())
    else:
        # Run example usage
        asyncio.run(example_usage())


if __name__ == "__main__":
    main()