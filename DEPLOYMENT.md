# MCP Server Deployment Guide

This guide explains how to deploy the LiteLLM MCP server on an Ubuntu ARM64 server and connect to it from Cursor.

## 🚀 Server Deployment (Ubuntu ARM64)

### Step 1: Prepare Your Ubuntu Server

1. **SSH into your Ubuntu server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Run the installation script:**
   ```bash
   # Download the installation script
   curl -O https://raw.githubusercontent.com/dinhdobathi1992/mcp-server-litellm/main/deploy/install.sh
   chmod +x install.sh
   ./install.sh
   ```

3. **Configure the server:**
   ```bash
   # Download the configuration script
   curl -O https://raw.githubusercontent.com/dinhdobathi1992/mcp-server-litellm/main/deploy/remote-server-config.sh
   chmod +x remote-server-config.sh
   ./remote-server-config.sh
   ```

### Step 2: Configure Environment Variables

1. **Edit the environment file:**
   ```bash
   sudo nano /opt/mcp-server-litellm/.env
   ```

2. **Update with your API keys:**
   ```bash
   # LiteLLM Proxy Configuration
   LITELLM_PROXY_URL=https://litellm.shared-services.adb.adi.tech
   LITELLM_API_KEY=your_actual_api_key_here
   
   # Performance Settings
   HTTP_TIMEOUT=30.0
   HTTP_CONNECT_TIMEOUT=10.0
   HTTP_MAX_KEEPALIVE_CONNECTIONS=20
   HTTP_MAX_CONNECTIONS=100
   HTTP_ENABLE_HTTP2=true
   ```

3. **Restart the service:**
   ```bash
   sudo systemctl restart mcp-server-litellm
   ```

### Step 3: Set Up SSH Key Authentication

1. **On your local machine, generate SSH key (if not exists):**
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

2. **Copy your public key to the server:**
   ```bash
   ssh-copy-id -i ~/.ssh/id_rsa.pub mcp-user@your-server-ip
   ```

3. **Test SSH connection:**
   ```bash
   ssh mcp-user@your-server-ip
   ```

## 🔗 Cursor Configuration

### Step 1: Update Cursor MCP Configuration

1. **Copy the remote configuration:**
   ```bash
   cp cursor-mcp-config-remote.json ~/.cursor/mcp-config.json
   ```

2. **Edit the configuration file:**
   ```bash
   nano ~/.cursor/mcp-config.json
   ```

3. **Replace `YOUR_SERVER_IP` with your actual server IP:**
   ```json
   {
     "mcpServers": {
       "litellm-remote": {
         "command": "ssh",
         "args": [
           "-L", "8000:localhost:8000",
           "-o", "Compression=yes",
           "-o", "ServerAliveInterval=60",
           "-o", "ServerAliveCountMax=3",
           "mcp-user@192.168.1.100",  // Replace with your server IP
           "cd /opt/mcp-server-litellm && source venv/bin/activate && python -m server_litellm"
         ],
         "env": {
           "LITELLM_PROXY_URL": "https://litellm.shared-services.adb.adi.tech",
           "LITELLM_API_KEY": "your_actual_api_key_here"
         }
       }
     }
   }
   ```

### Step 2: Restart Cursor

1. **Close Cursor completely**
2. **Reopen Cursor**
3. **Check MCP connection in Cursor settings**

## 🔧 Connection Methods

### Method 1: SSH Tunnel (Recommended)
- **Pros:** Secure, works through firewalls
- **Cons:** Slightly more complex setup
- **Use:** The `litellm-remote` configuration

### Method 2: Direct Connection
- **Pros:** Simpler, potentially faster
- **Cons:** Requires firewall configuration
- **Use:** The `litellm-remote-direct` configuration

## 📊 Monitoring and Maintenance

### Check Server Status
```bash
# On the server
sudo systemctl status mcp-server-litellm
/opt/mcp-server-litellm/monitor.sh
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u mcp-server-litellm -f

# Recent logs
sudo journalctl -u mcp-server-litellm --no-pager -l -n 50
```

### Restart Service
```bash
sudo systemctl restart mcp-server-litellm
```

### Update the Server
```bash
cd /opt/mcp-server-litellm
git pull
source venv/bin/activate
pip install -e .
sudo systemctl restart mcp-server-litellm
```

## 🛠️ Troubleshooting

### Common Issues

1. **SSH Connection Fails**
   ```bash
   # Test SSH connection
   ssh -v mcp-user@your-server-ip
   
   # Check SSH service
   sudo systemctl status sshd
   ```

2. **MCP Server Won't Start**
   ```bash
   # Check logs
   sudo journalctl -u mcp-server-litellm -f
   
   # Test manually
   cd /opt/mcp-server-litellm
   source venv/bin/activate
   python -m server_litellm
   ```

3. **Permission Issues**
   ```bash
   # Fix permissions
   sudo chown -R mcp-user:mcp-user /opt/mcp-server-litellm
   sudo chmod +x /opt/mcp-server-litellm/venv/bin/python
   ```

4. **Firewall Issues**
   ```bash
   # Check firewall status
   sudo ufw status
   
   # Allow SSH and MCP ports
   sudo ufw allow ssh
   sudo ufw allow 8000/tcp
   ```

### Performance Optimization

1. **Enable HTTP/2:**
   ```bash
   # Check if HTTP/2 is working
   grep "HTTP/2" /var/log/syslog
   ```

2. **Monitor Resource Usage:**
   ```bash
   # Check CPU and memory
   htop
   
   # Check network connections
   netstat -tlnp | grep :8000
   ```

3. **Optimize SSH for MCP:**
   ```bash
   # Add to ~/.ssh/config on your local machine
   Host your-server-ip
       HostName your-server-ip
       User mcp-user
       Compression yes
       ServerAliveInterval 60
       ServerAliveCountMax 3
       TCPKeepAlive yes
   ```

## 🔒 Security Considerations

1. **Use SSH Keys Only:**
   ```bash
   # Disable password authentication
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

2. **Restrict SSH Access:**
   ```bash
   # Allow only specific IPs
   sudo ufw allow from your-ip-address to any port ssh
   ```

3. **Regular Updates:**
   ```bash
   # Update system regularly
   sudo apt update && sudo apt upgrade -y
   ```

## 📈 Performance Monitoring

### Create a monitoring dashboard:
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Create performance log
sudo tee /opt/mcp-server-litellm/performance-monitor.sh > /dev/null <<'EOF'
#!/bin/bash
echo "=== MCP Server Performance Monitor ==="
echo "Date: $(date)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
echo "Active Connections: $(netstat -an | grep :8000 | wc -l)"
echo "MCP Service Status: $(systemctl is-active mcp-server-litellm)"
EOF

sudo chmod +x /opt/mcp-server-litellm/performance-monitor.sh
```

### Set up automated monitoring:
```bash
# Add to crontab
sudo crontab -e
# Add: */5 * * * * /opt/mcp-server-litellm/performance-monitor.sh >> /var/log/mcp-performance.log
```

## 🎯 Success Checklist

- [ ] Server installation completed
- [ ] Environment variables configured
- [ ] SSH key authentication working
- [ ] MCP service running and healthy
- [ ] Cursor configuration updated
- [ ] Connection tested successfully
- [ ] Performance monitoring set up
- [ ] Security measures implemented

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u mcp-server-litellm -f`
2. Test the connection manually
3. Verify firewall and network settings
4. Check the troubleshooting section above
5. Create an issue on the GitHub repository

Your MCP server should now be running on your Ubuntu ARM64 server and accessible from Cursor! 