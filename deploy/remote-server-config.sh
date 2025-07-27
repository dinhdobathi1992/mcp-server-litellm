#!/bin/bash
# Remote server configuration for LiteLLM MCP Server
# Run this on your Ubuntu ARM64 server

set -e

echo "🔧 Configuring remote server for MCP connections..."

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "📍 Server IP: $SERVER_IP"

# Create SSH tunnel configuration
echo "🔐 Setting up SSH tunnel configuration..."

# Create a dedicated user for MCP (optional but recommended)
sudo useradd -m -s /bin/bash mcp-user
echo "mcp-user:$(openssl rand -base64 32)" | sudo chpasswd

# Add SSH key for secure access (replace with your public key)
echo "🔑 Setting up SSH key authentication..."
sudo mkdir -p /home/mcp-user/.ssh
sudo chmod 700 /home/mcp-user/.ssh

# You'll need to add your public key here
echo "Please add your SSH public key to /home/mcp-user/.ssh/authorized_keys"
echo "Example: ssh-copy-id -i ~/.ssh/id_rsa.pub mcp-user@$SERVER_IP"

# Configure SSH for better performance
echo "⚡ Optimizing SSH for MCP connections..."
sudo tee -a /etc/ssh/sshd_config > /dev/null <<EOF

# MCP Server optimizations
ClientAliveInterval 60
ClientAliveCountMax 3
TCPKeepAlive yes
Compression yes
EOF

# Restart SSH service
sudo systemctl restart sshd

# Create MCP connection script
echo "📝 Creating MCP connection helper..."
sudo tee /opt/mcp-server-litellm/connect-mcp.sh > /dev/null <<EOF
#!/bin/bash
# MCP Connection Helper Script
echo "🔗 MCP Server Connection Information"
echo "======================================"
echo "Server IP: $SERVER_IP"
echo "SSH User: mcp-user"
echo "MCP Port: 8000 (if exposed)"
echo ""
echo "To connect from Cursor:"
echo "1. Use SSH tunnel: ssh -L 8000:localhost:8000 mcp-user@$SERVER_IP"
echo "2. Or use direct connection if firewall allows"
echo ""
echo "MCP Server Status:"
sudo systemctl status mcp-server-litellm --no-pager -l
EOF

sudo chmod +x /opt/mcp-server-litellm/connect-mcp.sh

# Create monitoring script
echo "📊 Creating monitoring script..."
sudo tee /opt/mcp-server-litellm/monitor.sh > /dev/null <<EOF
#!/bin/bash
# MCP Server Monitoring Script
echo "📈 MCP Server Status Monitor"
echo "============================="
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

sudo chmod +x /opt/mcp-server-litellm/monitor.sh

echo "✅ Remote server configuration complete!"
echo ""
echo "📋 Connection Information:"
echo "Server IP: $SERVER_IP"
echo "SSH User: mcp-user"
echo "MCP Service: mcp-server-litellm"
echo ""
echo "🔧 Useful commands:"
echo "- Check status: /opt/mcp-server-litellm/connect-mcp.sh"
echo "- Monitor: /opt/mcp-server-litellm/monitor.sh"
echo "- View logs: sudo journalctl -u mcp-server-litellm -f"
echo "- Restart: sudo systemctl restart mcp-server-litellm" 