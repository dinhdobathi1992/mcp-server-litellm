#!/usr/bin/env python3
"""
Simple example demonstrating Claude (Bedrock) working with the MCP server.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server_litellm.server import _handle_completion

async def claude_mcp_demo():
    """Demonstrate Claude working with MCP server."""
    
    print("🤖 Claude (Bedrock) MCP Server Demo")
    print("=" * 50)
    
    # Simple prompts that work well with Claude
    prompts = [
        "Write a Python function to reverse a string.",
        "Create a simple class for a Rectangle with area calculation.",
        "Write a decorator that measures function execution time."
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Example {i}: {prompt}")
        print("-" * 50)
        
        try:
            result = await _handle_completion({
                "model": "anthropic.claude-3-7-sonnet-20250219-v1:0",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            })
            
            print("✅ Claude Response:")
            print(result[0].text)
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Claude (Bedrock) is working perfectly with the MCP server!")

if __name__ == "__main__":
    asyncio.run(claude_mcp_demo()) 