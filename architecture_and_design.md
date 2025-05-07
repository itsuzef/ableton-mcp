# Ableton MCP Architecture and Design Documentation

This document provides a comprehensive overview of the Ableton MCP (Model Context Protocol) system architecture, design patterns, and implementation details. It can be used as a reference for creating a similar system for Bitwig Studio or other DAWs.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Components](#architecture-components)
3. [Communication Flow](#communication-flow)
4. [Remote Script Implementation](#remote-script-implementation)
5. [MCP Server Implementation](#mcp-server-implementation)
6. [Command Structure](#command-structure)
7. [CLI Implementation](#cli-implementation)
8. [Error Handling](#error-handling)
9. [Design Patterns](#design-patterns)
10. [Implementation Considerations for Bitwig](#implementation-considerations-for-bitwig)

## System Overview

The Ableton MCP system is designed to provide a standardized interface for controlling Ableton Live through a REST API. The system consists of three main components:

1. **Remote Script**: A Python script that runs within Ableton Live and communicates with the DAW's internal API
2. **MCP Server**: A FastAPI-based server that exposes a REST API for external applications
3. **CLI Tool**: A command-line interface for interacting with the MCP Server

The system follows a client-server architecture where the MCP Server acts as a bridge between external applications and Ableton Live. The Remote Script acts as a socket server that listens for commands from the MCP Server and translates them into actions within Ableton Live.

## Architecture Components

### Component Diagram

```
+----------------+     HTTP     +---------------+     Socket     +---------------+
|                |  Requests    |               |  Connection    |               |
| External Apps  | <----------> |  MCP Server   | <----------->  | Remote Script | <---> Ableton Live
| (Web, CLI)     |              | (FastAPI)     |                | (Python)      |
|                |              |               |                |               |
+----------------+     REST     +---------------+     JSON       +---------------+
                       API                           Messages
```

### Key Components

1. **Remote Script (`AbletonMCP_Remote_Script/__init__.py`)**
   - Runs within Ableton Live
   - Implements the `ControlSurface` interface
   - Creates a socket server to receive commands
   - Translates commands into Ableton Live actions
   - Returns results back to the MCP Server

2. **MCP Server (`MCP_Server/server.py`)**
   - Implements a FastAPI-based REST API
   - Connects to the Remote Script via socket
   - Translates HTTP requests into socket commands
   - Handles error cases and retries
   - Provides a clean API for external applications

3. **CLI Tool (`MCP_Server/cli.py`)**
   - Provides a command-line interface for the MCP Server
   - Handles installation of the Remote Script
   - Offers commands for starting the server and getting information

## Communication Flow

The communication flow between components follows this pattern:

1. **Client Request**: An external application sends an HTTP request to the MCP Server
2. **Server Processing**: The MCP Server validates the request and translates it into a command
3. **Socket Communication**: The server sends the command to the Remote Script via socket
4. **Remote Script Action**: The Remote Script performs the requested action in Ableton Live
5. **Response Flow**: Results flow back through the same path in reverse

### Example Flow for Creating a MIDI Track

```
Client -> POST /create_midi_track
  -> MCP Server validates request
    -> MCP Server sends JSON command to Remote Script
      -> Remote Script schedules action on Ableton's main thread
        -> Ableton creates the MIDI track
      -> Remote Script sends result back to MCP Server
    -> MCP Server formats the response
  -> Client receives HTTP response
```

## Remote Script Implementation

The Remote Script is implemented as a Python class that extends Ableton's `ControlSurface` class. It sets up a socket server to receive commands from the MCP Server and translates these commands into actions within Ableton Live.

### Key Features

1. **Socket Server**: The Remote Script creates a socket server on port 9877 to receive commands
2. **Command Processing**: Commands are received as JSON objects and processed based on their type
3. **Thread Safety**: Actions that modify Ableton's state are scheduled on the main thread
4. **Error Handling**: Comprehensive error handling with detailed logging
5. **Connection Management**: Handles client connections and disconnections gracefully

### Command Handlers

The Remote Script implements various command handlers that interact with Ableton Live:

- Session management (`_get_session_info`, `_set_tempo`)
- Track management (`_create_midi_track`, `_set_track_name`)
- Clip management (`_create_clip`, `_add_notes_to_clip`)
- Device control (`_get_device_parameters`, `_set_device_parameter`)
- Specialized EQ control (`_set_eq_band`, `_set_eq_global`, `_apply_eq_preset`)
- Browser interaction (`get_browser_tree`, `get_browser_items_at_path`)
- Playback control (`_start_playback`, `_stop_playback`)

## MCP Server Implementation

The MCP Server is built using FastMCP (based on FastAPI) and provides a REST API for controlling Ableton Live. It establishes a socket connection to the Remote Script and translates HTTP requests into socket commands.

### Key Features

1. **REST API**: Exposes a clean REST API for external applications
2. **Socket Client**: Connects to the Remote Script via socket
3. **Connection Management**: Handles connection failures and retries
4. **Error Handling**: Comprehensive error handling with detailed logging
5. **Lifespan Management**: Manages server startup and shutdown

### API Endpoints

The MCP Server exposes various endpoints that correspond to actions in Ableton Live:

- `/get_session_info`: Get information about the current session
- `/get_track_info`: Get information about a specific track
- `/create_midi_track`: Create a new MIDI track
- `/create_clip`: Create a new MIDI clip
- `/add_notes_to_clip`: Add MIDI notes to a clip
- `/set_tempo`: Set the tempo of the session
- `/get_device_parameters`: Get parameters for a device
- `/set_device_parameter`: Set a device parameter
- `/set_eq_band`: Set parameters for an EQ Eight band
- `/set_eq_global`: Set global parameters for an EQ Eight device
- `/apply_eq_preset`: Apply a preset to an EQ Eight device

## Command Structure

Commands are exchanged between the MCP Server and Remote Script as JSON objects with a consistent structure:

### Request Format

```json
{
  "type": "command_type",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Response Format

```json
{
  "status": "success",
  "result": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

Or for errors:

```json
{
  "status": "error",
  "message": "Error message"
}
```

## CLI Implementation

The CLI tool provides a command-line interface for interacting with the MCP Server. It is implemented using Python's `argparse` module and offers various commands:

- `server`: Start the MCP Server
- `info`: Show information about the MCP Server
- `version`: Show version information
- `install`: Install the Remote Script in Ableton Live

### Installation Process

The CLI tool can automatically install the Remote Script in Ableton Live by:

1. Finding the Ableton Live MIDI Remote Scripts directory
2. Creating an `AbletonMCP_Remote_Script` directory
3. Copying the Remote Script files to this directory

## Error Handling

The system implements comprehensive error handling at multiple levels:

1. **Remote Script**: Catches and logs errors, sends error responses back to the MCP Server
2. **MCP Server**: Handles socket errors, timeouts, and invalid responses
3. **CLI Tool**: Provides clear error messages for installation and server startup issues

### Error Response Example

```json
{
  "status": "error",
  "message": "Track index out of range: 10"
}
```

## Design Patterns

The Ableton MCP system employs several design patterns:

1. **Command Pattern**: Commands are encapsulated as objects with a type and parameters
2. **Adapter Pattern**: The Remote Script adapts Ableton's API to a socket-based protocol
3. **Facade Pattern**: The MCP Server provides a simplified interface to Ableton Live
4. **Factory Pattern**: The Remote Script creates and returns various objects based on commands
5. **Observer Pattern**: The Remote Script observes changes in Ableton Live and can report them

## Implementation Considerations for Bitwig

When implementing a similar system for Bitwig Studio, consider the following:

1. **Controller API**: Bitwig uses a different API for controllers, based on Java/JavaScript
2. **Extension System**: Bitwig has an extension system rather than MIDI Remote Scripts
3. **Socket Communication**: Implement socket communication in Java/JavaScript
4. **Command Translation**: Translate commands to Bitwig's API calls
5. **Error Handling**: Implement appropriate error handling for Bitwig's API
6. **Installation Process**: Create an installation process for Bitwig extensions

### Bitwig-Specific Adaptations

1. **Controller Extension**: Create a Bitwig Controller Extension instead of a Remote Script
2. **API Mapping**: Map the MCP commands to Bitwig's Controller API
3. **Socket Implementation**: Implement socket communication in Java
4. **Installation**: Create an installation process for Bitwig extensions
5. **Error Handling**: Adapt error handling to Bitwig's API

## Conclusion

The Ableton MCP system provides a robust architecture for controlling Ableton Live through a REST API. By understanding its design and implementation, you can create a similar system for Bitwig Studio or other DAWs, adapting the patterns and approaches to the specific requirements of the target DAW.
