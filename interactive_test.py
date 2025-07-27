#!/usr/bin/env python3
"""
Interactive test script for LiteLLM MCP server.

This script allows you to interactively test completion requests with different models.
"""

import asyncio
from server_litellm.server import _handle_completion, _handle_list_models

# Supported models for this MCP server
SUPPORTED_MODELS = [
    "gpt-4o",
    "anthropic.claude-3-7-sonnet-20250219-v1:0"
]

async def get_available_models():
    """Get and display available models."""
    try:
        result = await _handle_list_models()
        return result[0].text
    except Exception as e:
        return f"Error getting models: {e}"

async def test_completion(model, prompt, temperature=0.7, max_tokens=1000):
    """Test a completion request."""
    arguments = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        result = await _handle_completion(arguments)
        return f"✅ Success!\nResponse: {result[0].text}"
    except Exception as e:
        return f"❌ Error: {e}"

async def interactive_mode():
    """Run interactive testing mode."""
    print("🤖 LiteLLM MCP Server - Interactive Test Mode")
    print("=" * 50)
    
    # Show available models
    print("\n📋 Available Models:")
    models_text = await get_available_models()
    print(models_text)
    
    print(f"\n🎯 Supported models for testing: {', '.join(SUPPORTED_MODELS)}")
    
    while True:
        print("\n" + "=" * 50)
        print("Choose an option:")
        print("1. Test completion with a model")
        print("2. Show available models again")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Model selection
            print(f"\nAvailable models (1-{len(SUPPORTED_MODELS)}):")
            for i, model in enumerate(SUPPORTED_MODELS, 1):
                print(f"{i}. {model}")
            
            try:
                model_choice = int(input(f"\nSelect model (1-{len(SUPPORTED_MODELS)}): ")) - 1
                if 0 <= model_choice < len(SUPPORTED_MODELS):
                    selected_model = SUPPORTED_MODELS[model_choice]
                else:
                    print("❌ Invalid model selection")
                    continue
            except ValueError:
                print("❌ Please enter a valid number")
                continue
            
            # Get prompt
            prompt = input("\nEnter your prompt: ").strip()
            if not prompt:
                print("❌ Prompt cannot be empty")
                continue
            
            # Get parameters
            try:
                temperature = float(input("Temperature (0.0-2.0, default 0.7): ") or "0.7")
                max_tokens = int(input("Max tokens (default 1000): ") or "1000")
            except ValueError:
                print("❌ Invalid parameter values, using defaults")
                temperature = 0.7
                max_tokens = 1000
            
            # Test completion
            print(f"\n🚀 Testing with model: {selected_model}")
            print(f"📝 Prompt: {prompt}")
            print(f"🌡️  Temperature: {temperature}")
            print(f"🔢 Max tokens: {max_tokens}")
            print("-" * 50)
            
            result = await test_completion(selected_model, prompt, temperature, max_tokens)
            print(result)
            
        elif choice == "2":
            print("\n📋 Available Models:")
            models_text = await get_available_models()
            print(models_text)
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

async def quick_test():
    """Run a quick test with predefined parameters."""
    print("⚡ Quick Test Mode")
    print("=" * 30)
    
    # Test with both supported models
    test_prompts = [
        "What is the capital of France?",
        "Write a haiku about programming",
        "Explain quantum computing in simple terms"
    ]
    
    for model in SUPPORTED_MODELS:
        print(f"\n🤖 Testing {model}:")
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i}: {prompt} ---")
            result = await test_completion(model, prompt, 0.7, 200)
            print(result)
            print("-" * 40)

async def model_comparison():
    """Compare both models with the same prompts."""
    print("🔄 Model Comparison Mode")
    print("=" * 30)
    
    comparison_prompts = [
        "What is artificial intelligence?",
        "Write a short story about a robot",
        "Explain the benefits of renewable energy"
    ]
    
    for prompt in comparison_prompts:
        print(f"\n📝 Prompt: {prompt}")
        print("-" * 40)
        
        for model in SUPPORTED_MODELS:
            print(f"\n🤖 {model}:")
            result = await test_completion(model, prompt, 0.5, 150)
            print(result)
        
        print("\n" + "=" * 50)

async def main():
    """Main function."""
    print("Welcome to LiteLLM MCP Server Testing!")
    print("=" * 40)
    print(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
    
    while True:
        print("\nChoose test mode:")
        print("1. Interactive mode (custom prompts)")
        print("2. Quick test (predefined prompts)")
        print("3. Model comparison")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            await interactive_mode()
        elif choice == "2":
            await quick_test()
        elif choice == "3":
            await model_comparison()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    asyncio.run(main()) 