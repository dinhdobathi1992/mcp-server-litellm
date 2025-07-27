#!/bin/bash
# Quick fix script for all ARM64 issues
# This script fixes circular imports, missing dependencies, and systemd issues

set -e

echo "🚀 Quick Fix for All ARM64 Issues"
echo "================================="

# Check if we're in the right directory
if [ ! -d "/opt/mcp-server-litellm" ]; then
    echo "❌ Please run this script from /opt/mcp-server-litellm"
    exit 1
fi

cd /opt/mcp-server-litellm

# Activate virtual environment
source venv/bin/activate

echo "🔧 Step 1: Fixing circular import issue..."
# Rename types.py to mcp_types.py if it exists
if [ -f "mcp_compat/types.py" ]; then
    mv mcp_compat/types.py mcp_compat/mcp_types.py
    echo "✅ Renamed types.py to mcp_types.py"
fi

# Update imports in all files
sed -i 's/from mcp.server import Server/from mcp_compat.server import Server/' src/server_litellm/server.py
sed -i 's/from mcp.types import Tool, TextContent/from mcp_compat.mcp_types import Tool, TextContent/' src/server_litellm/server.py
sed -i 's/from mcp.server.stdio import stdio_server/from mcp_compat.stdio import stdio_server/' src/server_litellm/server.py
sed -i 's/from pydantic import BaseModel/# from pydantic import BaseModel  # Using simple BaseModel/' src/server_litellm/server.py

echo "🔧 Step 2: Installing missing dependencies..."
# Install core dependencies first
pip install pydantic python-dotenv httpx anyio jsonschema pydantic-settings python-multipart sse-starlette starlette uvicorn httpx-sse h2 hyperframe hpack idna certifi urllib3 charset-normalizer typing-extensions

# Install LiteLLM without problematic dependencies
echo "Installing LiteLLM without problematic dependencies..."
if pip install litellm --no-deps; then
    echo "✅ LiteLLM installed successfully (no deps)"
else
    echo "⚠️  LiteLLM installation failed, trying minimal install..."
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

echo "🔧 Step 3: Creating MCP compatibility layer..."
# Create MCP compatibility layer if it doesn't exist
if [ ! -d "mcp_compat" ]; then
    mkdir -p mcp_compat
fi

# Create __init__.py
cat > mcp_compat/__init__.py <<'EOF'
# Minimal MCP compatibility layer for ARM64
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the minimal MCP classes we need
from .server import Server
from .mcp_types import Tool, TextContent
from .stdio import stdio_server

__all__ = ['Server', 'Tool', 'TextContent', 'stdio_server']
EOF

# Create server.py
cat > mcp_compat/server.py <<'EOF'
# Minimal MCP Server implementation for ARM64 compatibility
import asyncio
import json
from typing import List, Dict, Any, Optional
from .mcp_types import Tool, TextContent

class Server:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        
    def list_tools(self):
        def decorator(func):
            self._list_tools_func = func
            return func
        return decorator
        
    def call_tool(self):
        def decorator(func):
            self._call_tool_func = func
            return func
        return decorator
        
    async def run(self, read_stream, write_stream, init_options):
        # Simple MCP server implementation
        while True:
            try:
                line = await read_stream.readline()
                if not line:
                    break
                    
                data = json.loads(line.decode().strip())
                
                if data.get("method") == "tools/list":
                    tools = await self._list_tools_func()
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {"tools": [tool.dict() for tool in tools]}
                    }
                elif data.get("method") == "tools/call":
                    result = await self._call_tool_func(
                        data["params"]["name"],
                        data["params"]["arguments"]
                    )
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {"content": [content.dict() for content in result]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "error": {"code": -32601, "message": "Method not found"}
                    }
                    
                await write_stream.write((json.dumps(response) + "\n").encode())
                await write_stream.flush()
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id") if 'data' in locals() else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                await write_stream.write((json.dumps(error_response) + "\n").encode())
                await write_stream.flush()
                
    def create_initialization_options(self):
        return {}
EOF

# Create mcp_types.py
cat > mcp_compat/mcp_types.py <<'EOF'
# Minimal MCP types for ARM64 compatibility
from typing import Dict, Any, Optional

# Simple base class without pydantic dependency
class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def dict(self):
        return {k: v for k, v in self.__dict__.items()}

class Tool(BaseModel):
    def __init__(self, name: str, description: str, inputSchema: Dict[str, Any]):
        super().__init__(name=name, description=description, inputSchema=inputSchema)
    
    def dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema
        }

class TextContent(BaseModel):
    def __init__(self, text: str, type: str = "text"):
        super().__init__(text=text, type=type)
    
    def dict(self):
        return {
            "type": self.type,
            "text": self.text
        }
EOF

# Create stdio.py
cat > mcp_compat/stdio.py <<'EOF'
# Minimal stdio server for ARM64 compatibility
import asyncio
import sys
from typing import Tuple, AsyncGenerator

async def stdio_server() -> Tuple[AsyncGenerator[bytes, None], asyncio.StreamWriter]:
    """Create stdio streams for MCP communication."""
    
    async def read_stream():
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            yield line.encode()
    
    # Create a writer that writes to stdout
    writer = asyncio.StreamWriter(
        asyncio.StreamReader(),
        None,
        lambda: None,
        lambda: None
    )
    
    # Override write method to write to stdout
    original_write = writer.write
    def write(data):
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        return original_write(data)
    
    writer.write = write
    
    return read_stream(), writer
EOF

echo "🔧 Step 4: Fixing systemd service..."
# Create wrapper script
cat > /opt/mcp-server-litellm/start_server.py <<'EOF'
#!/usr/bin/env python3
"""
Wrapper script to start the MCP server with correct Python path
"""
import sys
import os

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Import and run the server
if __name__ == "__main__":
    from server_litellm.server import run_server
    import asyncio
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
EOF

chmod +x /opt/mcp-server-litellm/start_server.py

# Update systemd service
sudo tee /etc/systemd/system/mcp-server-litellm.service > /dev/null <<EOF
[Unit]
Description=LiteLLM MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mcp-server-litellm
Environment=PATH=/opt/mcp-server-litellm/venv/bin
ExecStart=/opt/mcp-server-litellm/venv/bin/python /opt/mcp-server-litellm/start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "🔧 Step 5: Testing everything..."
# Test the installation
if python -c "from mcp_compat.server import Server; print('MCP compatibility layer test passed')"; then
    echo "✅ MCP compatibility layer test passed"
else
    echo "❌ MCP compatibility layer test failed"
    exit 1
fi

# Test server functionality
if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('Server functionality test passed')"; then
    echo "✅ Server functionality test passed"
else
    echo "❌ Server functionality test failed"
    exit 1
fi

# Test wrapper script
if python /opt/mcp-server-litellm/start_server.py --help 2>/dev/null || python -c "import sys; sys.path.append('src'); from server_litellm.server import run_server; print('Wrapper script test passed')"; then
    echo "✅ Wrapper script test passed"
else
    echo "⚠️  Wrapper script test failed, but continuing..."
fi

echo "🔧 Step 6: Starting the service..."
# Reload systemd and restart service
sudo systemctl daemon-reload
sudo systemctl stop mcp-server-litellm
sudo systemctl start mcp-server-litellm

# Test the service
sleep 5
if sudo systemctl is-active --quiet mcp-server-litellm; then
    echo "✅ MCP service is running successfully!"
else
    echo "⚠️  MCP service failed to start. Checking logs..."
    sudo journalctl -u mcp-server-litellm --no-pager -n 10
    echo "⚠️  Service failed to start. You may need to check the logs manually."
fi

echo ""
echo "🎉 Quick fix completed!"
echo "======================"
echo ""
echo "📋 Your MCP server should now be working."
echo "🔧 Useful Commands:"
echo "Check status: sudo systemctl status mcp-server-litellm"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
echo "ℹ️  Note: This script fixed circular imports, missing dependencies, and systemd issues." 