#!/bin/bash
cd "$(dirname "$0")"
source ableton_mcp_venv/bin/activate

# Get environment variables with defaults
HOST="${MCP_HOST:-127.0.0.1}"
PORT="${MCP_PORT:-8000}"

# Run the server using the CLI module
python -m MCP_Server.cli server --host "$HOST" --port "$PORT"
