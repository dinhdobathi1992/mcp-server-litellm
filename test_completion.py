#!/usr/bin/env python3
"""
Comprehensive test script for LiteLLM MCP server completion requests.

This script demonstrates how to test different models and completion scenarios.
"""

import asyncio
import json
from server_litellm.server import _handle_completion, _handle_list_models

# Supported models for testing
SUPPORTED_MODELS = [
    "gpt-4o",
    "anthropic.claude-3-7-sonnet-20250219-v1:0"
]

async def test_simple_completion():
    """Test a simple completion request."""
    print("=" * 50)
    print("TEST 1: Simple Completion")
    print("=" * 50)
    
    arguments = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "What is 2 + 2?"}
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    try:
        result = await _handle_completion(arguments)
        print(f"✅ Success! Response: {result[0].text}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_conversation():
    """Test a multi-turn conversation."""
    print("\n" + "=" * 50)
    print("TEST 2: Multi-turn Conversation")
    print("=" * 50)
    
    arguments = {
        "model": "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "messages": [
            {"role": "user", "content": "Hi! My name is Alice."},
            {"role": "assistant", "content": "Hello Alice! Nice to meet you. How can I help you today?"},
            {"role": "user", "content": "Can you help me write a short poem about coding?"}
        ],
        "temperature": 0.8,
        "max_tokens": 200
    }
    
    try:
        result = await _handle_completion(arguments)
        print(f"✅ Success! Response: {result[0].text}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_different_models():
    """Test different available models."""
    print("\n" + "=" * 50)
    print("TEST 3: Different Models")
    print("=" * 50)
    
    # Get available models first
    try:
        models_result = await _handle_list_models()
        models_text = models_result[0].text
        print("Available models:")
        print(models_text)
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return
    
    # Test with supported models
    for model in SUPPORTED_MODELS:
        print(f"\n--- Testing {model} ---")
        arguments = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Say 'Hello from [model_name]' in a creative way."}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            result = await _handle_completion(arguments)
            print(f"✅ {model}: {result[0].text}")
        except Exception as e:
            print(f"❌ {model}: {e}")

async def test_parameters():
    """Test different temperature and max_tokens parameters."""
    print("\n" + "=" * 50)
    print("TEST 4: Different Parameters")
    print("=" * 50)
    
    base_messages = [{"role": "user", "content": "Write a one-sentence story about a robot."}]
    
    # Test different temperatures
    temperatures = [0.1, 0.5, 1.0]
    for temp in temperatures:
        print(f"\n--- Temperature: {temp} ---")
        arguments = {
            "model": "gpt-4o",
            "messages": base_messages,
            "temperature": temp,
            "max_tokens": 50
        }
        
        try:
            result = await _handle_completion(arguments)
            print(f"✅ Response: {result[0].text}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\n" + "=" * 50)
    print("TEST 5: Error Handling")
    print("=" * 50)
    
    # Test with unsupported model
    print("--- Unsupported Model ---")
    arguments = {
        "model": "gpt-3.5-turbo",  # This should be rejected
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        result = await _handle_completion(arguments)
        print(f"✅ Unexpected success: {result[0].text}")
    except Exception as e:
        print(f"✅ Expected error: {e}")
    
    # Test with invalid messages format
    print("\n--- Invalid Messages Format ---")
    arguments = {
        "model": "gpt-4o",
        "messages": "This is not a list",
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        result = await _handle_completion(arguments)
        print(f"✅ Unexpected success: {result[0].text}")
    except Exception as e:
        print(f"✅ Expected error: {e}")

async def test_model_comparison():
    """Test both models with the same prompt to compare responses."""
    print("\n" + "=" * 50)
    print("TEST 6: Model Comparison")
    print("=" * 50)
    
    test_prompt = "Explain quantum computing in one sentence."
    
    for model in SUPPORTED_MODELS:
        print(f"\n--- {model} ---")
        arguments = {
            "model": model,
            "messages": [{"role": "user", "content": test_prompt}],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        try:
            result = await _handle_completion(arguments)
            print(f"Response: {result[0].text}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all tests."""
    print("🚀 LiteLLM MCP Server - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Testing with supported models: {', '.join(SUPPORTED_MODELS)}")
    
    # Run all tests
    await test_simple_completion()
    await test_conversation()
    await test_different_models()
    await test_parameters()
    await test_error_handling()
    await test_model_comparison()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 