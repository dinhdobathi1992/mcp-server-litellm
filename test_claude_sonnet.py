#!/usr/bin/env python3
"""
Test script for Anthropic Claude 3.7 Sonnet model via MCP LiteLLM server.

This script runs a comprehensive suite of tests against the Claude 3.7 Sonnet model
through the MCP LiteLLM server, demonstrating various capabilities including:
- Simple text completions
- Multi-turn conversations
- Creative writing tasks
- Code generation
- Analytical reasoning
- Parameter sensitivity
- Error handling

Usage:
    python test_claude_sonnet.py

Requirements:
    - litellm
    - httpx
    - asyncio
    - json
    - typing
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
import sys

# Import the MCP server functions
from server_litellm.server import _handle_completion, _handle_list_models

# Configuration
MODEL_NAME = "anthropic.claude-3-7-sonnet-20250219-v1:0"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Test result tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


async def call_claude(
    prompt: str,
    system: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS
) -> Dict[str, Any]:
    """
    Make an async call to the Claude model through the MCP LiteLLM server.
    
    Args:
        prompt: The user prompt to send
        system: Optional system message
        messages: Optional conversation history
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        
    Returns:
        The model response as a dictionary
    """
    try:
        if messages:
            # Use provided conversation history
            payload = messages
        else:
            # Create a new conversation
            payload = []
            if system:
                payload.append({"role": "system", "content": system})
            payload.append({"role": "user", "content": prompt})
            
        arguments = {
            "model": MODEL_NAME,
            "messages": payload,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        result = await _handle_completion(arguments)
        return {"choices": [{"message": {"content": result[0].text}}]}
        
    except Exception as e:
        print(f"{Colors.RED}Error calling Claude: {str(e)}{Colors.END}")
        return {"error": str(e)}


def log_test_result(name: str, passed: bool, prompt: str, response: str, error: Optional[str] = None):
    """Log test results and update the test_results dictionary."""
    status = f"{Colors.GREEN}PASSED{Colors.END}" if passed else f"{Colors.RED}FAILED{Colors.END}"
    test_results["passed" if passed else "failed"] += 1
    
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "prompt": prompt,
        "response": response,
        "error": error
    })
    
    print(f"\n{Colors.BOLD}{name}: {status}{Colors.END}")
    print(f"{Colors.BLUE}Prompt:{Colors.END} {prompt[:100]}...")
    if passed:
        print(f"{Colors.GREEN}Response:{Colors.END} {response[:200]}...")
    else:
        print(f"{Colors.RED}Response:{Colors.END} {response[:200]}...")
        if error:
            print(f"{Colors.RED}Error:{Colors.END} {error}")
    print("-" * 80)


async def test_simple_completion():
    """Test a simple completion prompt."""
    prompt = "Explain the concept of quantum entanglement in simple terms."
    
    response = await call_claude(prompt)
    
    if "error" in response:
        log_test_result("Simple Completion", False, prompt, "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    passed = len(content) > 100 and "quantum" in content.lower()
    
    log_test_result("Simple Completion", passed, prompt, content)


async def test_conversation():
    """Test a multi-turn conversation."""
    system = "You are a helpful assistant who specializes in astronomy."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "What's the largest planet in our solar system?"},
    ]
    
    response = await call_claude("", messages=messages)
    
    if "error" in response:
        log_test_result("Conversation - Turn 1", False, messages[-1]["content"], "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    passed_turn1 = "jupiter" in content.lower()
    
    log_test_result("Conversation - Turn 1", passed_turn1, messages[-1]["content"], content)
    
    # Add the assistant's response and a follow-up question
    messages.append({"role": "assistant", "content": content})
    messages.append({"role": "user", "content": "How does its size compare to Earth?"})
    
    response2 = await call_claude("", messages=messages)
    
    if "error" in response2:
        log_test_result("Conversation - Turn 2", False, messages[-1]["content"], "", response2["error"])
        return
    
    content2 = response2["choices"][0]["message"]["content"]
    passed_turn2 = len(content2) > 50 and ("times" in content2.lower() or "larger" in content2.lower())
    
    log_test_result("Conversation - Turn 2", passed_turn2, messages[-1]["content"], content2)


async def test_creative_writing():
    """Test creative writing capabilities."""
    prompt = "Write a short, vivid poem about the northern lights."
    
    response = await call_claude(prompt)
    
    if "error" in response:
        log_test_result("Creative Writing", False, prompt, "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    
    # Check if the response has poetic elements
    passed = (
        len(content) > 100 and 
        len(content.split("\n")) > 3 and
        ("light" in content.lower() or "sky" in content.lower() or "green" in content.lower())
    )
    
    log_test_result("Creative Writing", passed, prompt, content)


async def test_code_generation():
    """Test code generation capabilities."""
    prompt = """
    Write a Python function that:
    1. Takes a list of integers as input
    2. Returns a new list containing only the prime numbers from the input list
    3. Include docstrings and comments
    """
    
    response = await call_claude(prompt)
    
    if "error" in response:
        log_test_result("Code Generation", False, prompt, "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    
    # Check if the response has code elements
    code_indicators = ["def", "return", "for", "if", "prime"]
    has_code_elements = all(indicator in content.lower() for indicator in code_indicators)
    has_code_block = "```python" in content or "```" in content
    
    passed = has_code_elements and has_code_block
    
    log_test_result("Code Generation", passed, prompt, content)


async def test_analytical_reasoning():
    """Test analytical reasoning capabilities."""
    prompt = """
    Solve this logic puzzle:
    Alice is taller than Bob. Bob is taller than Charlie.
    Dave is shorter than Charlie. Who is the tallest?
    """
    
    response = await call_claude(prompt)
    
    if "error" in response:
        log_test_result("Analytical Reasoning", False, prompt, "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    passed = "alice" in content.lower() and len(content) > 50
    
    log_test_result("Analytical Reasoning", passed, prompt, content)


async def test_parameter_handling():
    """Test parameter handling with different settings."""
    prompt = "Write exactly 5 words about AI."
    
    # Test with low temperature for more focused response
    response = await call_claude(prompt, temperature=0.1)
    
    if "error" in response:
        log_test_result("Parameter Handling", False, prompt, "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    words = content.split()
    passed = 4 <= len(words) <= 6  # Allow slight flexibility
    
    log_test_result("Parameter Handling", passed, prompt, content)


async def test_error_handling():
    """Test error handling with problematic inputs."""
    prompt = "Colorless green ideas sleep furiously. Explain what this means."
    
    response = await call_claude(prompt)
    
    if "error" in response:
        log_test_result("Error Handling", False, prompt, "", response["error"])
        return
    
    content = response["choices"][0]["message"]["content"]
    passed = len(content) > 50  # Should provide some meaningful response
    
    log_test_result("Error Handling", passed, prompt, content)


async def test_model_listing():
    """Test listing available models."""
    try:
        result = await _handle_list_models()
        models_text = result[0].text
        print(f"\n{Colors.BOLD}Available Models:{Colors.END}")
        print(models_text)
        
        # Check if Claude model is in the list
        passed = MODEL_NAME in models_text
        log_test_result("Model Listing", passed, "List available models", models_text)
        
    except Exception as e:
        log_test_result("Model Listing", False, "List available models", "", str(e))


async def main():
    """Run all tests."""
    print(f"{Colors.BOLD}{Colors.UNDERLINE}Claude 3.7 Sonnet MCP Server Test Suite{Colors.END}")
    print(f"{Colors.BLUE}Testing model: {MODEL_NAME}{Colors.END}")
    print(f"{Colors.BLUE}Temperature: {TEMPERATURE}{Colors.END}")
    print(f"{Colors.BLUE}Max tokens: {MAX_TOKENS}{Colors.END}")
    print("=" * 80)
    
    # Run all tests
    await test_model_listing()
    await test_simple_completion()
    await test_conversation()
    await test_creative_writing()
    await test_code_generation()
    await test_analytical_reasoning()
    await test_parameter_handling()
    await test_error_handling()
    
    # Print summary
    print(f"\n{Colors.BOLD}Test Summary:{Colors.END}")
    print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.END}")
    
    total_tests = test_results['passed'] + test_results['failed']
    if total_tests > 0:
        success_rate = (test_results['passed'] / total_tests) * 100
        print(f"{Colors.BLUE}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    # Print detailed results
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.END}")
    for test in test_results['tests']:
        status = f"{Colors.GREEN}✓{Colors.END}" if test['passed'] else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {test['name']}")


if __name__ == "__main__":
    asyncio.run(main()) 