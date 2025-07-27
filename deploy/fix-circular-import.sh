#!/bin/bash
# Fix script for circular import error on ARM64
# Run this if you see the circular import error with types.py

set -e

echo "🔧 Fixing circular import error on ARM64..."

# Check if we're in the right directory
if [ ! -d "/opt/mcp-server-litellm" ]; then
    echo "❌ Please run this script from /opt/mcp-server-litellm"
    exit 1
fi

cd /opt/mcp-server-litellm

# Activate virtual environment
source venv/bin/activate

echo "🔧 Fixing circular import by renaming types.py..."

# Rename types.py to mcp_types.py to avoid conflict with Python's built-in types module
if [ -f "mcp_compat/types.py" ]; then
    mv mcp_compat/types.py mcp_compat/mcp_types.py
    echo "✅ Renamed types.py to mcp_types.py"
fi

# Update the __init__.py file to import from mcp_types
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

# Update the server.py file to import from mcp_types
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

# Create the mcp_types.py file with the correct content
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

# Update the stdio.py file (no changes needed, but ensure it exists)
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

# Update the server.py to use our compatibility layer
echo "🔧 Updating server imports..."
sed -i 's/from mcp.server import Server/from mcp_compat.server import Server/' src/server_litellm/server.py
sed -i 's/from mcp.types import Tool, TextContent/from mcp_compat.mcp_types import Tool, TextContent/' src/server_litellm/server.py
sed -i 's/from mcp.server.stdio import stdio_server/from mcp_compat.stdio import stdio_server/' src/server_litellm/server.py
sed -i 's/from pydantic import BaseModel/# from pydantic import BaseModel  # Using simple BaseModel/' src/server_litellm/server.py

# Test the installation
echo "🧪 Testing installation..."
if python -c "from mcp_compat.server import Server; print('MCP compatibility layer test passed')"; then
    echo "✅ MCP compatibility layer test passed"
else
    echo "❌ MCP compatibility layer test failed"
    exit 1
fi

# Test basic server functionality
echo "🧪 Testing server functionality..."
if python -c "
from mcp_compat.server import Server
from mcp_compat.mcp_types import Tool, TextContent
server = Server('test')
print('Server creation test passed')
"; then
    echo "✅ Server functionality test passed"
else
    echo "❌ Server functionality test failed"
    exit 1
fi

# Test the actual server module
echo "🧪 Testing server module..."
if python -c "
import sys
sys.path.append('src')
from server_litellm.server import _handle_completion, _handle_list_models
print('Server module test passed')
"; then
    echo "✅ Server module test passed"
else
    echo "❌ Server module test failed"
    exit 1
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
echo "🎉 Circular import fix completed!"
echo "================================"
echo ""
echo "📋 Your MCP server should now be working without circular import errors."
echo "🔧 Useful Commands:"
echo "Check status: sudo systemctl status mcp-server-litellm"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
echo "ℹ️  Note: Fixed the circular import by renaming types.py to mcp_types.py" 