#!/bin/bash
# Script to start the MCP server with virtual environment

# Change to the project directory
cd /Users/thi/workspaces/mcp-server-litellm

# Activate virtual environment and run the server
source venv/bin/activate
python -m server_litellm 