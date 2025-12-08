# Python Server - Dota 2 GSI with OBS Integration

This is the main server component of the Dota 2 GSI (Game State Integration) system. It receives real-time game data from Dota 2 and integrates with OBS Studio for automated recording based on game events.

## Features

- **Real-time GSI Server**: Flask-based server that receives game state data from Dota 2
- **OBS Integration**: Automatic recording control based on game events
- **Event System**: Comprehensive event emission for game state changes
- **Authentication**: Token-based security for GSI connections
- **Combat Log Processing**: Automatic copying of Dota 2 combat logs
- **Client Management**: Tracks multiple Dota 2 client connections
- **Data Logging**: Saves all received data to `gsi_log.txt`

## Architecture

```
python_server/
├── server.py          # Main server with OBS integration & event handlers
├── d2gsi.py           # Core GSI server framework
├── recording.py       # OBS recording manager
├── combatlog.py       # Combat log file copier
├── gsi_log.txt        # Logged GSI data
├── combatlog.txt      # Copied combat log data
└── dota_recordings/   # Recorded match videos
```

## Core Components

### server.py - Main Server Application

The main entry point that orchestrates all components:

```python
# Server configuration
server_options = {
    "port": 3000,
    "tokens": ["my_secret_token_12345", "another_token"],
}

# OBS Recording Manager
recording_manager = RecordingManager(
    matches_folder="./dota_recordings",
    obs_host="localhost",
    obs_port=4455,
    obs_password="123456"
)
```

**Key Features:**
- Initializes OBS WebSocket connection
- Sets up event handlers for game state changes
- Manages combat log copying subprocess
- Handles graceful shutdown

**Event Handlers:**
- Hero health, level, and status tracking
- Ability level and cast availability monitoring
- Item purchase notifications
- Player statistics (KDA) tracking
- Map position updates

### d2gsi.py - GSI Framework

The core Game State Integration framework providing:

**GSIClient Class:**
- Represents a connected Dota 2 client
- Maintains game state and emits events
- Handles authentication and IP tracking

**Middleware System:**
- `@check_auth()`: Validates authentication tokens
- `@check_client()`: Manages client connections
- `@update_gamestate()`: Updates client game state
- `@process_changes()`: Emits events for changed data

**Event System:**
- Global event emitter for server-wide events
- Client-specific event emitters
- Recursive change detection for nested game state

**Key Functions:**
```python
def create_d2gsi_app(options):
    """Creates and configures the Flask GSI application"""
    # Returns (app, host, port) tuple
```

### recording.py - OBS Integration

Manages OBS Studio recording through WebSocket API:

**RecordingManager Class:**
```python
class RecordingManager:
    def __init__(self, matches_folder, obs_host, obs_port, obs_password):
        # Initializes OBS WebSocket connection
        # Sets up recording directories

    def start_recording(self, match_id):
        # Creates match folder
        # Sets OBS recording path
        # Starts OBS recording

    def stop_recording(self):
        # Stops OBS recording
        # Cleans up connection
```

**Features:**
- Automatic match detection from game state
- Organized recording storage by match ID
- Sync file creation with timestamps
- Error handling for OBS connection issues

**Recording Structure:**
```
dota_recordings/
└── {match_id}/
    ├── recording.mp4    # OBS recorded video
    └── sync.txt         # Timestamp sync file
```

### combatlog.py - Combat Log Processor

Continuously copies Dota 2 combat log file:

```python
# Configuration (update paths for your system)
src = "D:/SteamLibrary/steamapps/common/dota 2 beta/game/dota/combatlog.txt"
dest = "D:/HuyDinh/dota2-gsi/combatlog.txt"

def copy_combatlog():
    """Copies combat log every second"""
```

**Features:**
- Real-time combat log mirroring
- Automatic retry on copy failures
- Timestamped copy notifications

## Installation & Setup

### Dependencies

Install required packages:
```bash
pip install flask obs-websocket-py
```

### Configuration

1. **Update OBS Settings** in `server.py`:
   ```python
   recording_manager = RecordingManager(
       matches_folder="./dota_recordings",
       obs_host="localhost",
       obs_port=4455,        # Must match OBS WebSocket port
       obs_password="123456" # Must match OBS WebSocket password
   )
   ```

2. **Update Combat Log Path** in `combatlog.py`:
   ```python
   src = "PATH_TO_YOUR_DOTA/combatlog.txt"
   ```

3. **Configure Authentication Tokens**:
   ```python
   server_options = {
       "tokens": ["your_secure_token_here"]
   }
   ```

## Usage

### Starting the Server

```bash
cd python_server
python server.py
```

**Expected Output:**
```
Recording will save to: [absolute path to dota_recordings]
[OBS] Connecting to OBS at localhost:4455...
[OBS] ✅ Connected to OBS successfully!
GSI up and running and ready to receive data...
Started combatlog process
Dota 2 GSI listening on 127.0.0.1:3000
```

### Game State Events

The server emits events for various game state changes:

#### Hero Events
```python
client.on("hero:health_percent", lambda hp: print(f"Health: {hp}%"))
client.on("hero:level", lambda lvl: print(f"Level up: {lvl}"))
client.on("hero:alive", lambda alive: print("Hero died!" if not alive else "Hero respawned!"))
```

#### Ability Events
```python
client.on("abilities:ability0:level", lambda lvl: print(f"Q ability level: {lvl}"))
client.on("abilities:ability0:can_cast", lambda can: print(f"Can cast Q: {can}"))
```

#### Item Events
```python
client.on("items:slot0:name", lambda item: print(f"New item in slot 0: {item}"))
```

#### Player Stats
```python
client.on("player:kills", lambda k: print(f"Kills: {k}"))
client.on("player:deaths", lambda d: print(f"Deaths: {d}"))
client.on("player:assists", lambda a: print(f"Assists: {a}"))
```

#### Map & Position
```python
client.on("hero:position", lambda pos: print(f"Position: {pos['x']}, {pos['y']}"))
```

#### Raw Data
```python
client.on("newdata", lambda data: print("Received game state update"))
```

## Data Flow

1. **Dota 2** sends game state updates to `http://localhost:3000/`
2. **d2gsi.py** processes authentication and client management
3. **recording.py** detects match start/end and controls OBS recording
4. **combatlog.py** continuously copies combat log data
5. **server.py** emits events for all game state changes
6. All data is logged to `gsi_log.txt`

## Output Files

- `gsi_log.txt`: Complete JSON log of all received game state data
- `combatlog.txt`: Real-time copy of Dota 2 combat log
- `dota_recordings/{match_id}/`: Match recordings with sync timestamps

## Troubleshooting

### OBS Connection Issues
- Ensure OBS WebSocket server is enabled (`Tools` → `WebSocket Server Settings`)
- Verify port and password match between OBS and `server.py`
- Check that OBS is running before starting the server

### No Game Data
- Verify `gamestate_integration.cfg` is in correct Dota 2 directory
- Confirm authentication token matches
- Check server logs for connection messages

### Combat Log Issues
- Update source path in `combatlog.py` to match your Dota 2 installation
- Ensure destination directory is writable
- Check Dota 2 console logging is enabled

## API Reference

### GSIClient Methods
- `on(event, handler)`: Register event handler
- `emit(event, *args)`: Emit custom event

### RecordingManager Methods
- `start_recording(match_id)`: Start recording for match
- `stop_recording()`: Stop current recording
- `handle_game_state(data)`: Process game state for recording decisions

### Global Events
- `"newclient"`: Fired when new Dota 2 client connects
- Client-specific events as documented above

## Security Notes

- Change default authentication tokens before production use
- OBS WebSocket password should be secure
- Server binds to localhost by default for security
- All game data is logged locally - consider privacy implications
