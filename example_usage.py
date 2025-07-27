#!/usr/bin/env python3
"""
Example usage of the LiteLLM MCP server with LiteLLM proxy.

This script demonstrates how to use the MCP server to interact with models
through your LiteLLM proxy.
"""

import asyncio
import json
from server_litellm.server import _handle_completion, _handle_list_models

# Supported models for this MCP server
SUPPORTED_MODELS = [
    "gpt-4o",
    "anthropic.claude-3-7-sonnet-20250219-v1:0"
]

async def test_completion():
    """Test the completion functionality."""
    print("Testing completion with LiteLLM proxy...")
    
    # Example completion request using a supported model
    arguments = {
        "model": "gpt-4o",  # Using one of the supported models
        "messages": [
            {"role": "user", "content": "Hello! Can you tell me a short joke?"}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        result = await _handle_completion(arguments)
        print("Response:", result[0].text)
    except Exception as e:
        print(f"Error: {e}")

async def test_list_models():
    """Test the model listing functionality."""
    print("\nTesting model listing...")
    
    try:
        result = await _handle_list_models()
        print(result[0].text)
    except Exception as e:
        print(f"Error: {e}")

async def test_both_models():
    """Test both supported models."""
    print("\nTesting both supported models...")
    
    test_prompt = "What is the meaning of life?"
    
    for model in SUPPORTED_MODELS:
        print(f"\n--- Testing {model} ---")
        arguments = {
            "model": model,
            "messages": [
                {"role": "user", "content": test_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        try:
            result = await _handle_completion(arguments)
            print(f"Response: {result[0].text}")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main test function."""
    print("LiteLLM MCP Server Test")
    print("=" * 40)
    print(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
    
    # Test model listing first
    await test_list_models()
    
    # Test completion with gpt-4o
    await test_completion()
    
    # Test both models
    await test_both_models()

if __name__ == "__main__":
    asyncio.run(main()) 