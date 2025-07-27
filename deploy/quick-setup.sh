#!/bin/bash
# Quick setup script for deploying MCP server on Ubuntu ARM64
# This script automates the entire deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP=""
MCP_USER="mcp-user"
APP_DIR="/opt/mcp-server-litellm"
REPO_URL="https://github.com/dinhdobathi1992/mcp-server-litellm.git"

echo -e "${BLUE}🚀 LiteLLM MCP Server Quick Setup${NC}"
echo "=================================="

# Get server IP if not provided
if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo -e "${YELLOW}📍 Detected server IP: $SERVER_IP${NC}"
fi

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
print_status "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget build-essential python3-dev

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR
cd $APP_DIR

# Clone repository
print_status "Cloning repository..."
if [ -d ".git" ]; then
    print_warning "Repository already exists, pulling latest changes..."
    git pull
else
    git clone $REPO_URL .
fi

# Create virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip

# Try installing with editable install first, fallback to requirements.txt
if ! pip install -e .; then
    print_warning "Editable install failed, trying with requirements.txt..."
    pip install -r requirements.txt
fi

# Create environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp env.example .env
    print_warning "Please edit $APP_DIR/.env with your API keys"
fi

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/mcp-server-litellm.service > /dev/null <<EOF
[Unit]
Description=LiteLLM MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python -m server_litellm
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create MCP user
print_status "Creating MCP user..."
if ! id "$MCP_USER" &>/dev/null; then
    sudo useradd -m -s /bin/bash $MCP_USER
    echo "$MCP_USER:$(openssl rand -base64 32)" | sudo chpasswd
    print_warning "Created user $MCP_USER with random password"
    print_warning "Please set up SSH key authentication for $MCP_USER"
fi

# Set up SSH for MCP user
print_status "Setting up SSH configuration..."
sudo mkdir -p /home/$MCP_USER/.ssh
sudo chmod 700 /home/$MCP_USER/.ssh
sudo chown $MCP_USER:$MCP_USER /home/$MCP_USER/.ssh

# Optimize SSH for MCP connections
if ! grep -q "MCP Server optimizations" /etc/ssh/sshd_config; then
    sudo tee -a /etc/ssh/sshd_config > /dev/null <<EOF

# MCP Server optimizations
ClientAliveInterval 60
ClientAliveCountMax 3
TCPKeepAlive yes
Compression yes
EOF
    sudo systemctl restart sshd
fi

# Create helper scripts
print_status "Creating helper scripts..."

# Connection helper
sudo tee $APP_DIR/connect-mcp.sh > /dev/null <<EOF
#!/bin/bash
echo "🔗 MCP Server Connection Information"
echo "===================================="
echo "Server IP: $SERVER_IP"
echo "SSH User: $MCP_USER"
echo "App Directory: $APP_DIR"
echo ""
echo "To connect from Cursor:"
echo "1. Use SSH tunnel: ssh -L 8000:localhost:8000 $MCP_USER@$SERVER_IP"
echo "2. Or use direct connection if firewall allows"
echo ""
echo "MCP Server Status:"
sudo systemctl status mcp-server-litellm --no-pager -l
EOF

# Monitor script
sudo tee $APP_DIR/monitor.sh > /dev/null <<EOF
#!/bin/bash
echo "📈 MCP Server Status Monitor"
echo "============================"
echo "Service Status:"
sudo systemctl status mcp-server-litellm --no-pager -l
echo ""
echo "Recent Logs:"
sudo journalctl -u mcp-server-litellm --no-pager -l -n 20
echo ""
echo "Resource Usage:"
ps aux | grep mcp-server-litellm | grep -v grep
echo ""
echo "Network Connections:"
netstat -tlnp | grep :8000 || echo "No connections on port 8000"
EOF

# Performance monitor
sudo tee $APP_DIR/performance-monitor.sh > /dev/null <<'EOF'
#!/bin/bash
echo "=== MCP Server Performance Monitor ==="
echo "Date: $(date)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
echo "Active Connections: $(netstat -an | grep :8000 | wc -l)"
echo "MCP Service Status: $(systemctl is-active mcp-server-litellm)"
EOF

sudo chmod +x $APP_DIR/*.sh

# Enable and start service
print_status "Enabling and starting MCP service..."
sudo systemctl daemon-reload
sudo systemctl enable mcp-server-litellm
sudo systemctl start mcp-server-litellm

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 8000/tcp
sudo ufw --force enable

# Test the service
print_status "Testing MCP service..."
sleep 5
if sudo systemctl is-active --quiet mcp-server-litellm; then
    print_status "MCP service is running successfully!"
else
    print_error "MCP service failed to start. Check logs with: sudo journalctl -u mcp-server-litellm -f"
    exit 1
fi

# Create Cursor configuration template
print_status "Creating Cursor configuration template..."
cat > $APP_DIR/cursor-config-template.json <<EOF
{
  "mcpServers": {
    "litellm-remote": {
      "command": "ssh",
      "args": [
        "-L", "8000:localhost:8000",
        "-o", "Compression=yes",
        "-o", "ServerAliveInterval=60",
        "-o", "ServerAliveCountMax=3",
        "$MCP_USER@$SERVER_IP",
        "cd $APP_DIR && source venv/bin/activate && python -m server_litellm"
      ],
      "env": {
        "LITELLM_PROXY_URL": "https://litellm.shared-services.adb.adi.tech",
        "LITELLM_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
EOF

# Final output
echo ""
echo -e "${GREEN}🎉 MCP Server Setup Complete!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}📋 Server Information:${NC}"
echo "Server IP: $SERVER_IP"
echo "SSH User: $MCP_USER"
echo "App Directory: $APP_DIR"
echo "Service: mcp-server-litellm"
echo ""
echo -e "${BLUE}🔧 Next Steps:${NC}"
echo "1. Edit $APP_DIR/.env with your API keys"
echo "2. Set up SSH key authentication: ssh-copy-id -i ~/.ssh/id_rsa.pub $MCP_USER@$SERVER_IP"
echo "3. Copy cursor-config-template.json to your local machine"
echo "4. Update the configuration with your server IP and API key"
echo "5. Restart Cursor to use the remote MCP server"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "Check status: $APP_DIR/connect-mcp.sh"
echo "Monitor: $APP_DIR/monitor.sh"
echo "Performance: $APP_DIR/performance-monitor.sh"
echo "View logs: sudo journalctl -u mcp-server-litellm -f"
echo "Restart: sudo systemctl restart mcp-server-litellm"
echo ""
echo -e "${YELLOW}⚠️  Security Note:${NC}"
echo "Please set up SSH key authentication and disable password login for better security."
echo ""
print_status "Setup completed successfully!" 