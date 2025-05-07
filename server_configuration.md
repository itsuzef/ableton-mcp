# Ableton MCP Server Configuration Guide

This document provides detailed instructions for configuring and running the Ableton MCP server. It covers the different methods of starting the server, configuration options, and common troubleshooting steps.

## Table of Contents

1. [Server Architecture](#server-architecture)
2. [Configuration Methods](#configuration-methods)
3. [Running the Server](#running-the-server)
4. [MCP Integration](#mcp-integration)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Server Architecture

The Ableton MCP server consists of several key components:

1. **FastMCP Server**: The core server component built on the Model Context Protocol framework
2. **CLI Interface**: A command-line interface for interacting with the server
3. **Remote Script**: The script that runs within Ableton Live and communicates with the server

### Key Files

- `MCP_Server/server.py`: The main server implementation
- `MCP_Server/cli.py`: The command-line interface
- `AbletonMCP_Remote_Script/__init__.py`: The Ableton Live Remote Script

## Configuration Methods

There are three main ways to configure and run the Ableton MCP server:

### 1. Direct Server Module

Running the server module directly is the most basic approach:

```bash
python -m MCP_Server.server
```

**Important**: The `server.py` module uses environment variables for configuration:
- `MCP_HOST`: The host to bind to (default: "127.0.0.1")
- `MCP_PORT`: The port to bind to (default: "8000")
- `MCP_TRANSPORT`: The transport method to use (default: "sse")

The server's `main()` function reads these environment variables and passes them to the FastMCP instance. **Do not** modify the `mcp.run()` call to include parameters directly, as this will cause errors with the FastMCP library.

### 2. CLI Interface

The CLI interface provides a more user-friendly way to run the server:

```bash
python -m MCP_Server.cli server --host 127.0.0.1 --port 8000
```

Or if installed as a package:

```bash
ableton-mcp server --host 127.0.0.1 --port 8000
```

The CLI interface accepts command-line arguments and converts them to the appropriate environment variables before calling the server module.

### 3. MCP Configuration

When integrating with MCP systems like Claude, you need to configure the server in the MCP configuration file:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "/path/to/python",
      "args": [
        "-m",
        "MCP_Server.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/ableton-mcp",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8766",
        "MCP_TRANSPORT": "sse"
      }
    }
  }
}
```

**Critical**: Do not use command-line arguments in the MCP configuration. Instead, use environment variables as shown above. The MCP system has specific ways of passing arguments that may not be compatible with your CLI interface.

## Running the Server

### Using the start_local_server.sh Script

The included `start_local_server.sh` script provides a convenient way to start the server:

```bash
#!/bin/bash
cd "$(dirname "$0")"
source ableton_mcp_venv/bin/activate

# Get environment variables with defaults
HOST="${MCP_HOST:-127.0.0.1}"
PORT="${MCP_PORT:-8000}"

# Run the server using the CLI module
python -m MCP_Server.cli server --host "$HOST" --port "$PORT"
```

### Using Docker

If using Docker, the Dockerfile should be configured to use the appropriate command:

```dockerfile
# Use the CLI interface
CMD ["ableton-mcp", "server"]

# OR use the server module directly with environment variables
# CMD ["python", "-m", "MCP_Server.server"]
```

## MCP Integration

When integrating with MCP systems like Claude, follow these guidelines:

1. **Use Environment Variables**: Configure the server using environment variables, not command-line arguments
2. **Specify PYTHONPATH**: Always include the PYTHONPATH environment variable pointing to your project directory
3. **Direct Module Call**: Use `python -m MCP_Server.server` rather than the CLI interface
4. **Test Locally First**: Always test your configuration locally before integrating with MCP systems

### Example MCP Configuration

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "/Users/youssefhemimy/Documents/ableton-mcp/ableton_mcp_venv/bin/python",
      "args": [
        "-m",
        "MCP_Server.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/youssefhemimy/Documents/ableton-mcp",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8766",
        "MCP_TRANSPORT": "sse"
      }
    }
  }
}
```

## Troubleshooting

### Common Errors

#### 1. "Unexpected keyword argument 'port'"

```
TypeError: FastMCP.run() got an unexpected keyword argument 'port'
```

**Solution**: The FastMCP library doesn't accept direct parameters to the `run()` method. Use environment variables instead:

```python
# Incorrect
mcp.run(port=port, transport=transport)

# Correct
os.environ["MCP_PORT"] = str(port)
os.environ["MCP_TRANSPORT"] = transport
mcp.run()
```

#### 2. "Unrecognized arguments: server"

```
error: unrecognized arguments: server
```

**Solution**: This occurs when trying to pass subcommands to a script that doesn't support them. Make sure you're using the correct command structure:

- For CLI: `ableton-mcp server --port 8000`
- For direct module: `python -m MCP_Server.server --port 8000`

#### 3. "No module named 'MCP_Server'"

**Solution**: Make sure your PYTHONPATH includes the project directory:

```bash
export PYTHONPATH=/path/to/ableton-mcp
```

Or in the MCP configuration:

```json
"env": {
  "PYTHONPATH": "/path/to/ableton-mcp"
}
```

## Best Practices

1. **Use Environment Variables**: For configuration whenever possible
2. **Consistent Interface**: Keep the CLI and server module interfaces consistent
3. **Test Both Methods**: Test both direct server calls and CLI interface calls
4. **Document Changes**: Document any changes to the server configuration or startup process
5. **Version Control**: Keep track of configuration changes in version control
6. **Separate Concerns**: Keep the server logic separate from the CLI interface

By following these guidelines, you can avoid configuration issues and ensure that the Ableton MCP server works reliably across different environments and integration points.

## Differences from Original Repository

The original `ahujasid/ableton-mcp` repository uses a simpler approach where:

1. The server module directly calls `mcp.run()` without parameters
2. The FastMCP library reads configuration from environment variables
3. There is no CLI interface with subcommands

Our enhanced version adds:

1. A CLI interface with subcommands (`server`, `info`, `version`, `install`)
2. More configuration options and better error handling
3. Enhanced device parameter control

When using our enhanced version, be careful to maintain compatibility with the FastMCP library's expectations, especially when integrating with MCP systems like Claude.
