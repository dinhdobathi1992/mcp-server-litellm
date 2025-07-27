#!/bin/bash
# Manual test script for MCP server startup
# Run this to test the server manually and debug issues

set -e

echo "🧪 Manual MCP Server Test Script"
echo "================================"

# Check if we're in the right directory
if [ ! -d "/opt/mcp-server-litellm" ]; then
    echo "❌ Please run this script from /opt/mcp-server-litellm"
    exit 1
fi

cd /opt/mcp-server-litellm

# Activate virtual environment
source venv/bin/activate

echo "🔍 System Information:"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"
echo "Working directory: $(pwd)"
echo ""

echo "🔍 Directory Structure:"
ls -la
echo ""
ls -la src/
echo ""
ls -la src/server_litellm/
echo ""

echo "🧪 Testing Python imports step by step..."

echo "1. Testing basic Python import..."
if python -c "print('Basic Python import: OK')"; then
    echo "✅ Basic Python import: OK"
else
    echo "❌ Basic Python import: FAILED"
    exit 1
fi

echo "2. Testing sys.path manipulation..."
if python -c "import sys; sys.path.append('src'); print('sys.path manipulation: OK')"; then
    echo "✅ sys.path manipulation: OK"
else
    echo "❌ sys.path manipulation: FAILED"
    exit 1
fi

echo "3. Testing server_litellm module import..."
if python -c "import sys; sys.path.append('src'); import server_litellm; print('server_litellm import: OK')"; then
    echo "✅ server_litellm import: OK"
else
    echo "❌ server_litellm import: FAILED"
    exit 1
fi

echo "4. Testing server_litellm.server import..."
if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('server_litellm.server import: OK')"; then
    echo "✅ server_litellm.server import: OK"
else
    echo "❌ server_litellm.server import: FAILED"
    exit 1
fi

echo "5. Testing run_server function import..."
if python -c "import sys; sys.path.append('src'); from server_litellm.server import run_server; print('run_server import: OK')"; then
    echo "✅ run_server import: OK"
else
    echo "❌ run_server import: FAILED"
    exit 1
fi

echo "6. Testing MCP compatibility layer..."
if python -c "from mcp_compat.server import Server; print('MCP compatibility layer: OK')"; then
    echo "✅ MCP compatibility layer: OK"
else
    echo "❌ MCP compatibility layer: FAILED"
    exit 1
fi

echo ""
echo "🧪 Testing server startup (5 second timeout)..."

# Create a simple test script
cat > /tmp/test_server_start.py <<'EOF'
#!/usr/bin/env python3
import sys
import os
import asyncio
import signal
import time

# Add the src directory to Python path
src_path = os.path.join('/opt/mcp-server-litellm', 'src')
sys.path.insert(0, src_path)

# Import the server
from server_litellm.server import run_server

# Set up signal handler for graceful shutdown
def signal_handler(signum, frame):
    print("Received signal, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run the server with timeout
async def main():
    try:
        print("Starting MCP server...")
        await asyncio.wait_for(run_server(), timeout=5.0)
    except asyncio.TimeoutError:
        print("Server started successfully (timeout reached)")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Test the server startup
if timeout 10 python /tmp/test_server_start.py; then
    echo "✅ Server startup test: OK"
else
    echo "❌ Server startup test: FAILED"
    echo ""
    echo "🔧 Debugging information:"
    echo "1. Check if all dependencies are installed:"
    echo "   pip list | grep -E '(litellm|pydantic|httpx|anyio)'"
    echo ""
    echo "2. Check if the server module has the correct structure:"
    echo "   python -c \"import sys; sys.path.append('src'); import server_litellm; print(dir(server_litellm))\""
    echo ""
    echo "3. Check if run_server function exists:"
    echo "   python -c \"import sys; sys.path.append('src'); from server_litellm.server import run_server; print('run_server function exists')\""
fi

echo ""
echo "🧪 Testing systemd service configuration..."

echo "Current systemd service configuration:"
sudo systemctl cat mcp-server-litellm
echo ""

echo "Systemd service status:"
sudo systemctl status mcp-server-litellm --no-pager
echo ""

echo "Recent systemd logs:"
sudo journalctl -u mcp-server-litellm --no-pager -n 10
echo ""

echo "🎯 Manual test completed!"
echo "========================"
echo ""
echo "📋 If all tests passed, the server should work manually."
echo "🔧 If systemd still fails, try running the server manually:"
echo "   cd /opt/mcp-server-litellm"
echo "   source venv/bin/activate"
echo "   python -c \"import sys; sys.path.append('src'); from server_litellm.server import run_server; import asyncio; asyncio.run(run_server())\""
echo ""
echo "ℹ️  This will help identify if the issue is with systemd or the server itself." 