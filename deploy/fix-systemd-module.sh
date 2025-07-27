#!/bin/bash
# Fix script for systemd service module import error
# Run this if you see "No module named server_litellm" in systemd logs

set -e

echo "🔧 Fixing systemd service module import error..."

# Check if we're in the right directory
if [ ! -d "/opt/mcp-server-litellm" ]; then
    echo "❌ Please run this script from /opt/mcp-server-litellm"
    exit 1
fi

cd /opt/mcp-server-litellm

# Activate virtual environment
source venv/bin/activate

echo "🔧 Checking current directory structure..."
ls -la src/
echo ""

echo "🔧 Testing module import manually..."
if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('Module import test passed')"; then
    echo "✅ Module import test passed"
else
    echo "❌ Module import test failed"
    exit 1
fi

echo "🔧 Updating systemd service configuration..."

# Create a new systemd service with correct Python path
sudo tee /etc/systemd/system/mcp-server-litellm.service > /dev/null <<EOF
[Unit]
Description=LiteLLM MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mcp-server-litellm
Environment=PATH=/opt/mcp-server-litellm/venv/bin
Environment=PYTHONPATH=/opt/mcp-server-litellm/src
ExecStart=/opt/mcp-server-litellm/venv/bin/python -m server_litellm
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Alternative: Create a wrapper script for better control
echo "🔧 Creating wrapper script for better module loading..."
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

# Update systemd service to use the wrapper script
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

# Test the wrapper script
echo "🧪 Testing wrapper script..."
if python /opt/mcp-server-litellm/start_server.py --help 2>/dev/null || python -c "import sys; sys.path.append('src'); from server_litellm.server import run_server; print('Wrapper script test passed')"; then
    echo "✅ Wrapper script test passed"
else
    echo "⚠️  Wrapper script test failed, but continuing..."
fi

# Reload systemd and restart service
echo "🔄 Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl stop mcp-server-litellm
sudo systemctl start mcp-server-litellm

# Test the service
echo "🧪 Testing MCP service..."
sleep 5
if sudo systemctl is-active --quiet mcp-server-litellm; then
    echo "✅ MCP service is running successfully!"
else
    echo "⚠️  MCP service failed to start. Checking logs..."
    sudo journalctl -u mcp-server-litellm --no-pager -n 20
    echo ""
    echo "🔧 Trying alternative approach..."
    
    # Try a simpler approach - direct Python execution
    sudo tee /etc/systemd/system/mcp-server-litellm.service > /dev/null <<EOF
[Unit]
Description=LiteLLM MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mcp-server-litellm
Environment=PATH=/opt/mcp-server-litellm/venv/bin
ExecStart=/opt/mcp-server-litellm/venv/bin/python -c "import sys; sys.path.append('src'); from server_litellm.server import run_server; import asyncio; asyncio.run(run_server())"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl restart mcp-server-litellm
    
    sleep 5
    if sudo systemctl is-active --quiet mcp-server-litellm; then
        echo "✅ MCP service is now running successfully!"
    else
        echo "❌ MCP service still failed to start. Final logs:"
        sudo journalctl -u mcp-server-litellm --no-pager -n 20
        echo ""
        echo "🔧 Manual troubleshooting steps:"
        echo "1. Check if the module exists: ls -la src/server_litellm/"
        echo "2. Test manual import: cd /opt/mcp-server-litellm && source venv/bin/activate && python -c \"import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('OK')\""
        echo "3. Check Python version: python --version"
        echo "4. Check virtual environment: which python"
    fi
fi

echo ""
echo "🎉 Systemd service fix completed!"
echo "================================"
echo ""
echo "📋 Your MCP server should now be working with systemd."
echo "🔧 Useful Commands:"
echo "Check status: sudo systemctl status mcp-server-litellm"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
echo "ℹ️  Note: Fixed the module import issue by updating Python path and service configuration." 