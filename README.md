# LiteLLM MCP Server

An MCP server that integrates LiteLLM to handle text completions using specific LLM models through a LiteLLM proxy.

## Features

- Connect to specific LLM models through your LiteLLM proxy
- **Supported Models:**
  - `gpt-4o` (OpenAI)
  - `anthropic.claude-3-7-sonnet-20250219-v1:0` (Anthropic)
- Configurable temperature and max tokens
- Model validation and error handling
- Easy integration with MCP-compatible clients

## Installation

Install the package:
```bash
pip install mcp-server-litellm
```

Or install in development mode:
```bash
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` with your LiteLLM proxy settings:
```bash
# LiteLLM Proxy URL
LITELLM_PROXY_URL=https://litellm.shared-services.adb.adi.tech

# API Key for the LiteLLM proxy
LITELLM_API_KEY=sk-jhBs4H8kSBGagA7e179rkw
```

## Usage

### Running the MCP Server

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run the MCP server
mcp-server-litellm
```

### Available Tools

The server provides two main tools:

1. **`complete`** - Send completion requests to supported LLM models
   - `model`: Model name (only `gpt-4o` or `anthropic.claude-3-7-sonnet-20250219-v1:0`)
   - `messages`: Array of conversation messages
   - `temperature`: Controls randomness (0.0-2.0, default: 0.7)
   - `max_tokens`: Maximum tokens to generate (default: 1000)

2. **`list_models`** - List the supported models

### Example Usage

```python
# Example completion request
{
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 150
}
```

## Performance Optimization

The MCP server includes several performance optimizations to improve response speed:

### HTTP Client Optimizations
- **Connection Pooling**: Reuses HTTP connections for faster subsequent requests
- **HTTP/2 Support**: Enabled by default for better performance
- **Configurable Timeouts**: Adjustable connection and request timeouts
- **Keep-Alive Connections**: Maintains persistent connections

### Performance Configuration
You can tune performance settings via environment variables:

```bash
# HTTP Client Settings
HTTP_TIMEOUT=30.0                    # Request timeout in seconds
HTTP_CONNECT_TIMEOUT=10.0            # Connection timeout in seconds
HTTP_MAX_KEEPALIVE_CONNECTIONS=20    # Max keep-alive connections
HTTP_MAX_CONNECTIONS=100             # Max total connections
HTTP_ENABLE_HTTP2=true               # Enable HTTP/2

# Performance Monitoring
LOG_PERFORMANCE_METRICS=true         # Enable performance logging
LOG_SLOW_QUERIES_THRESHOLD=5.0       # Log requests slower than 5 seconds
```

### Streaming Support
Enable streaming for faster perceived response times:
```python
{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true  # Enable streaming
}
```

### Performance Testing
Run the performance test suite to benchmark your setup:
```bash
python test_performance.py
```

This will test response times across different models and query types, providing detailed performance metrics and optimization recommendations.

## Testing

### Quick Test
```bash
python example_usage.py
```

### Comprehensive Test Suite
```bash
python test_completion.py
```

### Performance Testing
```bash
python test_performance.py
```

### Interactive Testing
```bash
python interactive_test.py
```

## Supported Models

This MCP server is configured to support only two specific models for security and performance reasons:

- **`gpt-4o`** - OpenAI's latest GPT-4 model
- **`anthropic.claude-3-7-sonnet-20250219-v1:0`** - Anthropic's Claude 3.7 Sonnet model

Any other model requests will be rejected with a clear error message.

## Requirements

- Python 3.10+
- LiteLLM proxy running at the configured URL
- MCP-compatible client

## License

MIT License
