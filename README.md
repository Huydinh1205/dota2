# Dota 2 GSI Server - Python Flask Version

This is a Python Flask implementation of the Dota 2 Game State Integration (GSI) server, ported from the original Node.js version.

## Features

- **Authentication**: Token-based authentication for secure connections
- **Client Management**: Tracks connected Dota 2 clients by IP address
- **Event System**: Emits events for game state changes (health, abilities, items, etc.)
- **Combat Log**: Automatically copies Dota 2 combat log file
- **Logging**: Saves all received data to `gsi_log.txt`

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Files

- `d2gsi.py` - Main GSI server module
- `server.py` - Server setup with event listeners
- `combatlog.py` - Combat log file copier
- `test_server.py` - Test script for the server
- `requirements.txt` - Python dependencies

## Usage

### Start the Server

Run the main server:
```bash
python server.py
```

This will:
- Start the Flask server on port 3000
- Begin copying `combatlog.txt` from Dota 2 directory
- Set up event listeners for game state changes

### Configure Dota 2

In your Dota 2 `gamestate_integration.cfg` file, add:

```
"Dota 2 GSI"
{
    "uri" "http://localhost:3000/"
    "timeout" "5.0"
    "buffer" "0.1"
    "throttle" "0.1"
    "heartbeat" "30.0"
    "auth"
    {
        "token" "my_secret_token_12345"
    }
    "data"
    {
        "hero" "1"
        "abilities" "1"
        "items" "1"
        "player" "1"
        "map" "1"
        "previously" "1"
        "added" "1"
    }
}
```

### Test the Server

Run the test script to verify everything works:
```bash
python test_server.py
```

## Events

The server emits events for various game state changes:

### Hero Status
- `hero:health_percent` - Hero health percentage
- `hero:level` - Hero level
- `hero:alive` - Hero alive/dead status

### Abilities
- `abilities:ability0:level` - Ability level (ability0-ability5)
- `abilities:ability0:can_cast` - Ability cast availability

### Items
- `items:slot0:name` - Item in slot (slot0-slot8)

### Player Info
- `player:kills` - Player kills
- `player:deaths` - Player deaths
- `player:assists` - Player assists

### Map Info
- `hero:position` - Hero position {x, y}

### Raw Data
- `newdata` - Complete raw JSON payload

## Configuration

Edit `server.py` to change:
- Port number (default: 3000)
- Authentication tokens
- Event handlers

## Troubleshooting

1. **Server won't start**: Check if port 3000 is available
2. **No events received**: Verify Dota 2 config file and token
3. **Combat log not copying**: Check Dota 2 installation path in `combatlog.py`

## Comparison to Node.js Version

This Python version maintains feature parity with the original Node.js implementation:
- Same API endpoints and data processing
- Equivalent event emission system
- Identical authentication and client management
- Compatible with existing Dota 2 GSI configurations