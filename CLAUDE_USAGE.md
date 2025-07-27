# Using Claude (Bedrock) as Default Model

## 🎯 Quick Start

The LiteLLM MCP Server now defaults to using **Claude (Bedrock)** instead of GPT-4o. Here are the easy ways to use it:

### 1. Simple CLI Tool (Recommended)

```bash
# Single query
./claude "What is the meaning of life?"

# Interactive chat
./claude
```

### 2. Python Script

```bash
# Single query
python claude_cli.py "Explain quantum physics"

# Interactive chat
python claude_cli.py
```

### 3. Direct Python Usage

```python
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server_litellm.server import _handle_completion

async def ask_claude(prompt):
    result = await _handle_completion({
        "model": "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    })
    return result[0].text

# Usage
response = asyncio.run(ask_claude("Hello, Claude!"))
print(response)
```

## 🔧 Configuration

### Default Model
- **Claude**: `anthropic.claude-3-7-sonnet-20250219-v1:0` (default)
- **GPT-4o**: `gpt-4o` (alternative)

### Environment Variables
Make sure your `.env` file has:
```bash
LITELLM_PROXY_URL=https://your-litellm-proxy-url
LITELLM_API_KEY=your-api-key
```

## 🚀 Features

### Interactive Chat
- Type your messages and get responses
- Conversation history maintained
- Commands: `help`, `clear`, `history`, `quit`

### Single Queries
- Quick one-off questions
- Perfect for scripts and automation

### Performance
- HTTP/2 support for faster responses
- Connection pooling for efficiency
- Direct proxy calls for Claude

## 📝 Examples

```bash
# Ask for help
./claude "help"

# Creative writing
./claude "Write a short story about a robot learning to paint"

# Code generation
./claude "Write a Python function to sort a list of dictionaries by a key"

# Analysis
./claude "Analyze the pros and cons of renewable energy"

# Interactive mode
./claude
# Then type your messages interactively
```

## 🎉 Why Claude?

- **Better reasoning** for complex tasks
- **More nuanced responses** to ambiguous questions
- **Reduced hallucinations** - says "I don't know" when uncertain
- **Constitutional AI** approach for better alignment
- **Natural conversation** style

## 🔄 Switching Models

If you need to use GPT-4o instead:

```python
result = await _handle_completion({
    "model": "gpt-4o",  # Explicitly specify GPT-4o
    "messages": [{"role": "user", "content": "your prompt"}],
    "temperature": 0.7,
    "max_tokens": 1000
})
```

## 🛠️ Troubleshooting

### Common Issues

1. **Environment variables not set**
   - Check your `.env` file
   - Ensure `LITELLM_PROXY_URL` and `LITELLM_API_KEY` are set

2. **Virtual environment not activated**
   ```bash
   source venv/bin/activate.fish  # for fish shell
   # or
   source venv/bin/activate       # for bash/zsh
   ```

3. **Permission denied on claude script**
   ```bash
   chmod +x claude
   ```

### Getting Help

- Run `./claude help` for interactive help
- Check the logs for detailed error messages
- Ensure your LiteLLM proxy is accessible

---

**Enjoy using Claude (Bedrock) as your default AI assistant! 🤖✨** 