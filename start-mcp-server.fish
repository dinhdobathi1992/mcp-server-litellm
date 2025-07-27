#!/usr/bin/env fish
# Fish shell script to start the MCP server with virtual environment

# Get the directory where this script is located
set SCRIPT_DIR (dirname (status -f))
cd $SCRIPT_DIR

# Check if virtual environment exists
if not test -d "venv"
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
end

# Activate virtual environment
if test -f "venv/bin/activate.fish"
    source venv/bin/activate.fish
else
    echo "Error: Virtual environment activation script not found"
    exit 1
end

# Load environment variables from .env file
if test -f ".env"
    echo "Loading environment variables from .env file..."
    # Load each line from .env file and set as environment variable
    for line in (cat .env | grep -v '^#' | grep -v '^$')
        set -l key_value (string split '=' $line)
        if test (count $key_value) -ge 2
            set -l key $key_value[1]
            set -l value (string join '=' $key_value[2..-1])
            set -gx $key $value
            echo "Set $key"
        end
    end
else
    echo "Warning: .env file not found. Using default environment variables."
end

# Install dependencies if needed
if not test -f ".env"
    echo "Environment file not found. Copying from example..."
    cp env.example .env
    echo "Please edit .env file with your LiteLLM proxy settings before running the server."
end

# Run the MCP server
echo "Starting MCP server..."
echo "LITELLM_PROXY_URL: $LITELLM_PROXY_URL"
echo "LITELLM_API_KEY: $LITELLM_API_KEY"
python -m server_litellm 