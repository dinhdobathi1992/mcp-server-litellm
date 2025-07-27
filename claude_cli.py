#!/usr/bin/env python3
"""
Simple CLI tool to use Claude (Bedrock) interactively.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server_litellm.server import _handle_completion

# Default Claude model
DEFAULT_CLAUDE_MODEL = "anthropic.claude-3-7-sonnet-20250219-v1:0"

async def claude_chat():
    """Interactive chat with Claude."""
    print("🤖 Claude (Bedrock) Chat Interface")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'help' for usage information")
    print("-" * 50)
    
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\n📖 Help:")
                print("- Just type your message and press Enter")
                print("- Type 'quit', 'exit', or 'q' to end")
                print("- Type 'clear' to clear conversation history")
                print("- Type 'history' to see conversation history")
                continue
            elif user_input.lower() == 'clear':
                conversation_history = []
                print("🗑️  Conversation history cleared")
                continue
            elif user_input.lower() == 'history':
                if conversation_history:
                    print("\n📜 Conversation History:")
                    for i, msg in enumerate(conversation_history, 1):
                        role = "👤 You" if msg["role"] == "user" else "🤖 Claude"
                        print(f"{i}. {role}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                else:
                    print("📜 No conversation history yet")
                continue
            elif not user_input:
                continue
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            print("\n🤖 Claude is thinking...")
            
            # Get response from Claude
            result = await _handle_completion({
                "model": DEFAULT_CLAUDE_MODEL,
                "messages": conversation_history,
                "temperature": 0.7,
                "max_tokens": 1000
            })
            
            claude_response = result[0].text
            
            # Add Claude's response to history
            conversation_history.append({"role": "assistant", "content": claude_response})
            
            print(f"🤖 Claude: {claude_response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit")

async def claude_single(prompt: str):
    """Single prompt to Claude."""
    try:
        print(f"🤖 Claude (Bedrock) - Single Query")
        print("=" * 50)
        print(f"👤 Prompt: {prompt}")
        print("-" * 50)
        
        result = await _handle_completion({
            "model": DEFAULT_CLAUDE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        })
        
        print(f"🤖 Claude: {result[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single prompt mode
        prompt = " ".join(sys.argv[1:])
        asyncio.run(claude_single(prompt))
    else:
        # Interactive mode
        asyncio.run(claude_chat())

if __name__ == "__main__":
    main() 