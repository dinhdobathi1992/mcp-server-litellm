#!/bin/bash
# Simple installation script for LiteLLM MCP server on Ubuntu ARM64
# This script avoids pyproject.toml issues by using requirements.txt

set -e

echo "🚀 Simple LiteLLM MCP Server Installation"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget build-essential python3-dev

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/mcp-server-litellm
sudo chown $USER:$USER /opt/mcp-server-litellm
cd /opt/mcp-server-litellm

# Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/dinhdobathi1992/mcp-server-litellm.git .

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies using requirements.txt
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
echo "⚙️ Setting up environment configuration..."
cp env.example .env
echo "Please edit /opt/mcp-server-litellm/.env with your API keys and settings"

# Create systemd service
echo "🔧 Creating systemd service..."
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
echo "🚀 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable mcp-server-litellm
sudo systemctl start mcp-server-litellm

# Create firewall rules
echo "🔥 Setting up firewall rules..."
sudo ufw allow 8000/tcp
sudo ufw reload

echo "✅ Simple installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/mcp-server-litellm/.env with your API keys"
echo "2. Restart the service: sudo systemctl restart mcp-server-litellm"
echo "3. Check status: sudo systemctl status mcp-server-litellm"
echo "4. View logs: sudo journalctl -u mcp-server-litellm -f"
echo ""
echo "🌐 The MCP server is now running and ready to accept connections!" 