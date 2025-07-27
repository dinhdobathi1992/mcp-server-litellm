#!/bin/bash
# Robust installation script for LiteLLM MCP server on Ubuntu ARM64
# This script handles MCP package installation issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Robust LiteLLM MCP Server Installation${NC}"
echo "=============================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
print_status "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget build-essential python3-dev

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /opt/mcp-server-litellm
sudo chown $USER:$USER /opt/mcp-server-litellm
cd /opt/mcp-server-litellm

# Clone the repository
print_status "Cloning repository..."
git clone https://github.com/dinhdobathi1992/mcp-server-litellm.git .

# Create virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
print_status "Installing core dependencies..."
pip install pydantic>=2.0.0 python-dotenv>=0.21.0 httpx>=0.25.0 anyio>=3.0.0

# Try to install MCP package from different sources
print_status "Installing MCP package..."
MCP_INSTALLED=false

# Method 1: Try PyPI
print_warning "Trying to install MCP from PyPI..."
if pip install mcp>=1.0.0; then
    print_status "MCP installed successfully from PyPI"
    MCP_INSTALLED=true
else
    print_warning "PyPI installation failed, trying GitHub..."
    
    # Method 2: Try GitHub
    if pip install git+https://github.com/modelcontextprotocol/python-sdk.git; then
        print_status "MCP installed successfully from GitHub"
        MCP_INSTALLED=true
    else
        print_warning "GitHub installation failed, trying alternative method..."
        
        # Method 3: Install dependencies manually and try again
        pip install jsonschema>=4.20.0 pydantic-settings>=2.5.2 python-multipart>=0.0.9 sse-starlette>=1.6.1 starlette>=0.27.0 uvicorn>=0.23.1 httpx-sse>=0.4.0
        
        if pip install mcp>=1.0.0; then
            print_status "MCP installed successfully after installing dependencies"
            MCP_INSTALLED=true
        fi
    fi
fi

if [ "$MCP_INSTALLED" = false ]; then
    print_error "Failed to install MCP package. Please check your Python version and try manually."
    print_warning "You can try: pip install git+https://github.com/modelcontextprotocol/python-sdk.git"
    exit 1
fi

# Install remaining dependencies
print_status "Installing remaining dependencies..."
pip install litellm>=0.1.0

# Install HTTP/2 support
print_status "Installing HTTP/2 support..."
pip install h2>=3.0.0 hyperframe>=6.1.0 hpack>=4.1.0

# Test the installation
print_status "Testing installation..."
if python -c "import mcp; print('MCP import successful')"; then
    print_status "MCP package test passed"
else
    print_error "MCP package test failed"
    exit 1
fi

# Create environment file
print_status "Setting up environment configuration..."
cp env.example .env
print_warning "Please edit /opt/mcp-server-litellm/.env with your API keys and settings"

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/mcp-server-litellm.service > /dev/null <<EOF
[Unit]
Description=LiteLLM MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mcp-server-litellm
Environment=PATH=/opt/mcp-server-litellm/venv/bin
ExecStart=/opt/mcp-server-litellm/venv/bin/python -m server_litellm
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
print_status "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable mcp-server-litellm
sudo systemctl start mcp-server-litellm

# Create firewall rules
print_status "Setting up firewall rules..."
sudo ufw allow 8000/tcp
sudo ufw reload

# Test the service
print_status "Testing MCP service..."
sleep 5
if sudo systemctl is-active --quiet mcp-server-litellm; then
    print_status "MCP service is running successfully!"
else
    print_error "MCP service failed to start. Check logs with: sudo journalctl -u mcp-server-litellm -f"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Robust installation complete!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Edit /opt/mcp-server-litellm/.env with your API keys"
echo "2. Restart the service: sudo systemctl restart mcp-server-litellm"
echo "3. Check status: sudo systemctl status mcp-server-litellm"
echo "4. View logs: sudo journalctl -u mcp-server-litellm -f"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "Check status: sudo systemctl status mcp-server-litellm"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
print_status "Installation completed successfully!" 