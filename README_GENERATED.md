# LiteLLM MCP Server

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Reference](#api-reference)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Performance Optimization](#performance-optimization)
11. [Security](#security)
12. [Contributing](#contributing)

---

## Project Overview

The **LiteLLM MCP Server** is a lightweight and efficient server designed to act as a Model Control Proxy (MCP) for accessing advanced language models such as GPT-4o and Claude. It integrates seamlessly with LiteLLM proxy, offering enhanced performance and compatibility across multiple shell environments. 

### Benefits:
- **Unified Access**: Provides a single interface for interacting with GPT-4o and Claude models.
- **Performance Optimizations**: Includes HTTP/2 support, connection pooling, and configurable timeouts for faster and more reliable responses.
- **Cross-Shell Compatibility**: Works with bash, zsh, and fish shells, ensuring flexibility for developers.

---

## Features

- **HTTP/2 Support**: Faster and more efficient communication with the LiteLLM proxy.
- **Connection Pooling**: Reduces latency by reusing connections.
- **Configurable Timeouts**: Prevents hanging requests by setting custom timeout durations.
- **Environment Variable Loading**: Improved error handling for `.env` files across shell environments.
- **Enhanced Logging**: Provides detailed logs for debugging proxy connection issues.
- **Fish Shell Compatibility**: Includes a dedicated `start-mcp-server.fish` script for fish shell users.
- **Multi-Model Support**: Access GPT-4o and Claude models with ease.

---

## Prerequisites

Before installing LiteLLM MCP Server, ensure you have the following:

1. **Python**: Version 3.8 or higher.
2. **pip**: Python's package manager.
3. **LiteLLM Proxy**: Ensure LiteLLM is installed and configured.
4. **Environment Variables**: Access to API keys for GPT-4o and Claude models.

---

## Installation

### macOS

```bash
# Update Python and pip
brew install python
pip install --upgrade pip

# Install LiteLLM MCP Server
pip install lite-llm-mcp-server
```

### Linux

```bash
# Update Python and pip
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install --upgrade pip

# Install LiteLLM MCP Server
pip3 install lite-llm-mcp-server
```

### Windows

1. Download and install Python from [python.org](https://www.python.org/).
2. Open Command Prompt and run:
   ```bash
   pip install --upgrade pip
   pip install lite-llm-mcp-server
   ```

---

## Configuration

### Environment Variables

Create a `.env` file in the root directory of your project with the following keys:

```plaintext
GPT4_API_KEY=your_gpt4_api_key
CLAUDE_API_KEY=your_claude_api_key
SERVER_PORT=8000
TIMEOUT=30
```

### Configuration Options

- **`GPT4_API_KEY`**: API key for GPT-4o.
- **`CLAUDE_API_KEY`**: API key for Claude.
- **`SERVER_PORT`**: Port number for the MCP server (default: `8000`).
- **`TIMEOUT`**: Request timeout in seconds (default: `30`).

---

## Usage

### Run via Script

```bash
python -m lite_llm_mcp_server
```

### Run Manually

```bash
python server.py
```

### Run as a Package

```bash
lite-llm-mcp-server
```

---

## API Reference

### Endpoints

#### `/gpt4`
- **Method**: POST
- **Description**: Access GPT-4o model.
- **Parameters**:
  - `prompt` (string): Input prompt for the model.
  - `max_tokens` (integer): Maximum number of tokens to generate.
  - `temperature` (float): Sampling temperature.

#### `/claude`
- **Method**: POST
- **Description**: Access Claude model.
- **Parameters**:
  - `prompt` (string): Input prompt for the model.
  - `max_tokens` (integer): Maximum number of tokens to generate.
  - `temperature` (float): Sampling temperature.

---

## Examples

### Basic Example: GPT-4o Request

```python
import requests

url = "http://localhost:8000/gpt4"
payload = {
    "prompt": "Write a short story about AI.",
    "max_tokens": 100,
    "temperature": 0.7
}
response = requests.post(url, json=payload)
print(response.json())
```

### Advanced Example: Claude Request with Timeout

```python
import requests

url = "http://localhost:8000/claude"
payload = {
    "prompt": "Summarize the latest news in technology.",
    "max_tokens": 150,
    "temperature": 0.5
}
response = requests.post(url, json=payload, timeout=30)
print(response.json())
```

---

## Troubleshooting

### Common Issues

1. **Server Not Starting**:
   - Ensure Python is installed and the required dependencies are installed.
   - Check for missing environment variables in the `.env` file.

2. **API Key Errors**:
   - Verify that the API keys for GPT-4o and Claude are correct.

3. **Timeouts**:
   - Increase the `TIMEOUT` value in the `.env` file.

---

## Performance Optimization

- **Enable HTTP/2**: Ensure your hosting platform supports HTTP/2 for faster communication.
- **Connection Pooling**: Use a library like `httpx` for efficient connection pooling.
- **Adjust Timeouts**: Configure the `TIMEOUT` variable based on your application's needs.

---

## Security

### Best Practices

1. **Secure API Keys**:
   - Never hardcode API keys in your codebase. Use environment variables.
2. **Restrict Access**:
   - Use a firewall or IP whitelisting to restrict access to the MCP server.
3. **HTTPS**:
   - Deploy the server behind an HTTPS proxy for secure communication.

---

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a detailed description of your changes.

### Reporting Issues

If you encounter any issues, please open a GitHub issue with:
- A detailed description of the problem.
- Steps to reproduce the issue.
- Logs or error messages (if applicable).

---

Thank you for using LiteLLM MCP Server! 🚀 