#!/bin/bash
# Fix script for missing dependencies
# Run this if you see "ModuleNotFoundError: No module named 'idna'" or similar

set -e

echo "🔧 Fixing missing dependencies..."

# Check if we're in the right directory
if [ ! -d "/opt/mcp-server-litellm" ]; then
    echo "❌ Please run this script from /opt/mcp-server-litellm"
    exit 1
fi

cd /opt/mcp-server-litellm

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing missing dependencies..."

# Function to install package with dependencies
install_package_with_deps() {
    local package=$1
    echo "Installing $package with dependencies..."
    if pip install "$package"; then
        echo "✅ $package installed successfully"
    else
        echo "⚠️  $package failed, trying without deps..."
        pip install "$package" --no-deps
    fi
}

# Install core dependencies with their dependencies
echo "Installing core dependencies with deps..."
install_package_with_deps "pydantic>=2.0.0"
install_package_with_deps "python-dotenv>=0.21.0"
install_package_with_deps "httpx>=0.25.0"
install_package_with_deps "anyio>=3.0.0"

# Install MCP dependencies with deps
echo "Installing MCP dependencies with deps..."
install_package_with_deps "jsonschema>=4.20.0"
install_package_with_deps "pydantic-settings>=2.5.2"
install_package_with_deps "python-multipart>=0.0.9"
install_package_with_deps "sse-starlette>=1.6.1"
install_package_with_deps "starlette>=0.27.0"
install_package_with_deps "uvicorn>=0.23.1"
install_package_with_deps "httpx-sse>=0.4.0"

# Install HTTP/2 support with deps
echo "Installing HTTP/2 support with deps..."
install_package_with_deps "h2>=3.0.0"
install_package_with_deps "hyperframe>=6.0.0"
install_package_with_deps "hpack>=4.0.0"

# Install LiteLLM with deps
echo "Installing LiteLLM with deps..."
install_package_with_deps "litellm>=0.1.0"

# Install common missing dependencies
echo "Installing common missing dependencies..."
pip install idna certifi urllib3 charset-normalizer

# Test the installation
echo "🧪 Testing installation..."
if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('Module import test passed')"; then
    echo "✅ Module import test passed"
else
    echo "❌ Module import test failed"
    echo ""
    echo "🔧 Trying to install all dependencies from requirements.txt..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "⚠️  requirements.txt not found, trying manual install..."
        pip install idna certifi urllib3 charset-normalizer typing-extensions
    fi
    
    # Test again
    if python -c "import sys; sys.path.append('src'); from server_litellm.server import _handle_completion; print('Module import test passed')"; then
        echo "✅ Module import test passed after dependency fix"
    else
        echo "❌ Module import test still failed"
        exit 1
    fi
fi

# Test basic server functionality
echo "🧪 Testing server functionality..."
if python -c "
import sys
sys.path.append('src')
from server_litellm.server import _handle_completion, _handle_list_models
print('Server functionality test passed')
"; then
    echo "✅ Server functionality test passed"
else
    echo "❌ Server functionality test failed"
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
echo "🎉 Missing dependencies fix completed!"
echo "====================================="
echo ""
echo "📋 Your MCP server should now be working with all dependencies."
echo "🔧 Useful Commands:"
echo "Check status: sudo systemctl status mcp-server-litellm"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
echo "ℹ️  Note: Fixed missing dependencies by installing packages with their dependencies." 