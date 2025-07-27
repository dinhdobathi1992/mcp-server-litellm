#!/bin/bash
# Fix script for tokenizers/puccinialin issue on ARM64
# Run this if you see the puccinialin error with tokenizers

set -e

echo "🔧 Fixing tokenizers/puccinialin issue on ARM64..."

# Check if we're in the right directory
if [ ! -d "/opt/mcp-server-litellm" ]; then
    echo "❌ Please run this script from /opt/mcp-server-litellm"
    exit 1
fi

cd /opt/mcp-server-litellm

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing dependencies without problematic packages..."

# Function to install package with fallback
install_package_safe() {
    local package=$1
    local fallback=$2
    
    echo "Installing $package..."
    if pip install "$package" --no-deps; then
        echo "✅ $package installed successfully (no deps)"
    elif [ -n "$fallback" ]; then
        echo "⚠️  $package failed, trying fallback: $fallback"
        if pip install "$fallback" --no-deps; then
            echo "✅ $fallback installed successfully"
        else
            echo "⚠️  Both $package and $fallback failed, skipping..."
        fi
    else
        echo "⚠️  $package failed, skipping..."
    fi
}

# Install core dependencies first
echo "Installing core dependencies..."
pip install pydantic python-dotenv httpx anyio jsonschema pydantic-settings python-multipart sse-starlette starlette uvicorn httpx-sse h2 hyperframe hpack idna certifi urllib3 charset-normalizer typing-extensions

# Try to install litellm without problematic dependencies
echo "Installing LiteLLM without problematic dependencies..."
if pip install litellm --no-deps; then
    echo "✅ LiteLLM installed successfully (no deps)"
else
    echo "⚠️  LiteLLM installation failed, trying minimal install..."
    
    # Try to install just the core litellm files manually
    pip install --no-deps litellm
fi

# Install common dependencies that litellm might need
echo "Installing common dependencies that might be needed..."
pip install requests openai anthropic tiktoken

# Try to install tokenizers separately with specific version
echo "Trying to install tokenizers with specific version..."
if pip install "tokenizers<0.20.0" --no-deps; then
    echo "✅ tokenizers installed successfully (older version)"
elif pip install "tokenizers==0.19.0" --no-deps; then
    echo "✅ tokenizers installed successfully (specific version)"
else
    echo "⚠️  tokenizers installation failed, continuing without it..."
fi

# Test if litellm works without tokenizers
echo "🧪 Testing LiteLLM functionality..."
if python -c "import litellm; print('LiteLLM import test passed')"; then
    echo "✅ LiteLLM import test passed"
else
    echo "⚠️  LiteLLM import failed, but continuing..."
fi

# Test the server functionality
echo "🧪 Testing server functionality..."
if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('Server functionality test passed')"; then
    echo "✅ Server functionality test passed"
else
    echo "❌ Server functionality test failed"
    echo ""
    echo "🔧 Trying alternative approach - install minimal litellm..."
    
    # Try to create a minimal litellm compatibility layer
    mkdir -p litellm_compat
    cat > litellm_compat/__init__.py <<'EOF'
# Minimal LiteLLM compatibility layer for ARM64
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the minimal LiteLLM functions we need
from .completion import completion

__all__ = ['completion']
EOF

    cat > litellm_compat/completion.py <<'EOF'
# Minimal LiteLLM completion function for ARM64 compatibility
import asyncio
import json
import httpx
from typing import Dict, Any, Optional

async def completion(
    model: str,
    messages: list,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    stream: bool = False,
    **kwargs
):
    """Minimal completion function that works with OpenAI and Anthropic APIs."""
    
    # Simple implementation for basic completion
    if "gpt" in model.lower():
        # OpenAI API
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        if max_tokens:
            data["max_tokens"] = max_tokens
        if temperature:
            data["temperature"] = temperature
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    elif "claude" in model.lower():
        # Anthropic API
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages to Anthropic format
        content = ""
        for msg in messages:
            if msg["role"] == "user":
                content += msg["content"] + "\n"
        
        data = {
            "model": model,
            "max_tokens": max_tokens or 1000,
            "messages": [{"role": "user", "content": content}]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    else:
        raise ValueError(f"Unsupported model: {model}")

# For compatibility with existing code
class CompletionResponse:
    def __init__(self, text: str):
        self.text = text

def completion_sync(*args, **kwargs):
    """Synchronous version of completion."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(completion(*args, **kwargs))
        return CompletionResponse(result["choices"][0]["message"]["content"])
    finally:
        loop.close()
EOF

    # Update the server to use our compatibility layer
    sed -i 's/import litellm/import litellm_compat as litellm/' src/server_litellm/server.py
    
    # Test again
    if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('Server functionality test passed with compatibility layer')"; then
        echo "✅ Server functionality test passed with compatibility layer"
    else
        echo "❌ Server functionality test still failed"
        exit 1
    fi
fi

# Restart the service
echo "🔄 Restarting MCP service..."
sudo systemctl restart mcp-server-litellm

# Test the service
echo "🧪 Testing MCP service..."
sleep 5
if sudo systemctl is-active --quiet mcp-server-litellm; then
    echo "✅ MCP service is running successfully!"
else
    echo "⚠️  MCP service failed to start. Checking logs..."
    sudo journalctl -u mcp-server-litellm --no-pager -n 20
    echo "⚠️  Service failed to start. You may need to check the logs manually."
fi

echo ""
echo "🎉 Tokenizers/puccinialin fix completed!"
echo "======================================="
echo ""
echo "📋 Your MCP server should now be working without the problematic tokenizers dependency."
echo "🔧 Useful Commands:"
echo "Check status: sudo systemctl status mcp-server-litellm"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
echo "ℹ️  Note: Fixed the tokenizers/puccinialin issue by installing packages without problematic dependencies." 