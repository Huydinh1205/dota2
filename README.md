# Dota 2 GSI Server with OBS Integration

This is a comprehensive Dota 2 Game State Integration (GSI) server that receives real-time game data from Dota 2 and integrates with OBS Studio for automated recording and frame capture.

## Features

- **Real-time Game State Integration**: Receives live data from Dota 2 (health, abilities, items, player stats, etc.)
- **Automated OBS Recording**: Automatically starts/stops OBS recordings based on game events
- **Frame Capture**: Extract frames from OBS output for analysis or video processing
- **Combat Log Processing**: Automatically copies and processes Dota 2 combat logs
- **Authentication**: Token-based security for GSI connections
- **Event System**: Emits events for various game state changes

## Quick Start

1. **Install Dependencies**
2. **Configure Dota 2 GSI**
3. **Set Up OBS Studio**
4. **Run the Server**

---

## 1. Installation & Dependencies

### Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

For OBS integration, also install:

```bash
pip install obs-websocket-py opencv-python mss
```

### Directory Structure

```
dota2-gsi/
├── python_server/          # Main server code
│   ├── server.py           # Main server with OBS integration
│   ├── d2gsi.py            # GSI server module
│   ├── recording.py        # OBS recording manager
│   └── combatlog.py        # Combat log processor
├── obs/                    # OBS-related tools
│   └── obs.py              # Frame capture from OBS
├── gamestate_integration_dota2-gsi.cfg  # Dota 2 config
└── requirements.txt        # Python dependencies
```

---

## 2. Configure Dota 2 Game State Integration

### Step 1: Locate Dota 2 Configuration Folder

Find your Dota 2 configuration directory:

- **Windows**: `C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\`
- **macOS**: `~/Library/Application Support/Steam/steamapps/common/dota 2 beta/game/dota/cfg/`
- **Linux**: `~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/`

### Step 2: Create/Update gamestate_integration.cfg

Copy the provided `gamestate_integration_dota2-gsi.cfg` file to your Dota 2 cfg folder:

```cfg
"dota2-gsi Configuration"
{
    "uri"               "http://localhost:3000/"
    "timeout"           "5.0"
    "buffer"            "0.1"
    "throttle"          "0.1"
    "heartbeat"         "30.0"
    "data"
    {
        "buildings"     "1"
        "provider"      "1"
        "map"           "1"
        "player"        "1"
        "hero"          "1"
        "abilities"     "1"
        "items"         "1"
        "draft"         "1"
        "wearables"     "1"
    }
    "auth"
    {
        "token"         "hello1234"
    }
}
```

### Step 3: Verify Configuration

1. Make sure the file is named exactly `gamestate_integration.cfg`
2. The token `"hello1234"` must match the token in `server.py`
3. The URI points to your server (default: `http://localhost:3000/`)

### Step 4: Test GSI Connection

Launch Dota 2 and check the server logs. You should see a connection message when Dota 2 starts sending data.

---

## 3. Set Up OBS Studio Integration

### Option A: Automated Recording (Recommended)

The server can automatically control OBS recording based on game events.

#### Step 1: Install OBS WebSocket Plugin

1. Open OBS Studio
2. Go to `Tools` → `WebSocket Server Settings`
3. Check `Enable WebSocket server`
4. Set a password (default: `123456`) - remember this for `server.py`
5. Note the port (default: `4455`)

#### Step 2: Configure OBS for Game Capture

1. Add a `Game Capture` source in OBS
2. Select `Dota 2` as the game
3. Configure your recording settings (format, quality, etc.)

#### Step 3: Update Server Configuration

In `python_server/server.py`, update the OBS settings:

```python
recording_manager = RecordingManager(
    matches_folder="./dota_recordings",
    obs_host="localhost",
    obs_port=4455,           # Must match OBS WebSocket port
    obs_password="123456"    # Must match OBS WebSocket password
)
```

### Option B: Manual Frame Capture

Use the frame capture tool to extract frames from OBS output.

#### Step 1: Set Up OBS Virtual Camera

1. In OBS, add your Dota 2 game as a `Game Capture` source
2. Go to `Tools` → `Virtual Camera` → `Start`

#### Step 2: Run Frame Capture

```bash
python obs/obs.py
```

Select capture method:

1. **Virtual Camera** (recommended) - Captures from OBS Virtual Camera
2. **RTMP Stream** - Captures from OBS streaming output
3. **Preview Window** - Screen capture of OBS preview

The tool will automatically detect your OBS setup and start capturing frames to the `game_frames/` folder.

---

## 4. Running the Server

### Start the GSI Server

Navigate to the python_server directory and run:

```bash
cd python_server
python server.py
```

The server will:

- Start on port 3000
- Connect to OBS WebSocket
- Begin monitoring for Dota 2 connections
- Start combat log processing

### Expected Output

```
Recording will save to: [absolute path to dota_recordings]
[OBS] Connecting to OBS at localhost:4455...
[OBS] ✅ Connected to OBS successfully!
GSI up and running and ready to receive data...
Started combatlog process
Dota 2 GSI listening on 127.0.0.1:3000
```

### Launch Dota 2

Start Dota 2 and enter a match. The server will automatically:

- Detect when you enter a match
- Start OBS recording
- Begin receiving game state data
- Process combat logs

### Stop Recording

The server automatically stops recording when:

- The match ends
- You disconnect from the server (Ctrl+C)
- Dota 2 closes

---

## Game Events & Data

The server provides real-time events for:

### Hero Status

- `hero:health_percent` - Health percentage (0-100)
- `hero:level` - Current hero level
- `hero:alive` - Alive/dead status (true/false)

### Abilities

- `abilities:ability{X}:level` - Ability level (X = 0-5)
- `abilities:ability{X}:can_cast` - Cast availability

### Items

- `items:slot{X}:name` - Item in inventory slot (X = 0-8)

### Player Statistics

- `player:kills` - Kill count
- `player:deaths` - Death count
- `player:assists` - Assist count

### Map & Position

- `hero:position` - Hero coordinates {x, y}
- `map:game_time` - Game time in seconds

### Raw Data

- `newdata` - Complete JSON payload from Dota 2

---

## Configuration Options

### Server Settings (server.py)

```python
server_options = {
    "port": 3000,                                    # Server port
    "tokens": ["hello1234", "additional_token"],     # Auth tokens
}
```

### OBS Settings

```python
recording_manager = RecordingManager(
    matches_folder="./dota_recordings",  # Where to save recordings
    obs_host="localhost",                # OBS WebSocket host
    obs_port=4455,                       # OBS WebSocket port
    obs_password="123456"                # OBS WebSocket password
)
```

### Combat Log Settings (combatlog.py)

Update the Dota 2 path in `combatlog.py`:

```python
dota_path = r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota"
```

---

## Troubleshooting

### Server Won't Start

- Check if port 3000 is available
- Verify all Python dependencies are installed
- Ensure you're in the `python_server` directory

### No OBS Connection

- Confirm OBS WebSocket plugin is installed and enabled
- Verify the password and port match between OBS and server.py
- Check that OBS is running before starting the server

### No Dota 2 Data

- Verify `gamestate_integration.cfg` is in the correct Dota 2 folder
- Check that the auth token matches between config file and server
- Ensure Dota 2 is running and in a match
- Look for connection messages in server logs

### Combat Log Not Copying

- Update the Dota 2 installation path in `combatlog.py`
- Check file permissions for the combat log file
- Verify Dota 2 console logging is enabled

### Frame Capture Issues

- For Virtual Camera: Ensure OBS Virtual Camera is started
- For RTMP: Set up an RTMP server (nginx-rtmp recommended)
- For Preview: Make sure OBS preview window is visible and not minimized

---

## Output Files

### Recordings

- Saved in `dota_recordings/{match_id}/`
- Includes video file and `sync.txt` with timestamps

### Combat Logs

- `combatlog.txt` - Raw combat log data
- `gsi_log.txt` - All received GSI data

### Frame Captures

- `game_frames/frame_XXXXXX.jpg` - Individual frames from OBS
- Captured at ~16.7 FPS (every 0.06 seconds)

---

## Advanced Usage

### Custom Event Handlers

Add custom event handlers in `server.py`:

```python
client.on("hero:health_percent", lambda hp:
    print("⚠️ LOW HEALTH!" if hp < 25 else f"Health: {hp}%")
)
```

### Multiple OBS Instances

Configure multiple OBS instances by running separate servers with different ports and OBS connections.

### Video Processing

Use the captured frames for:

- AI analysis
- Highlight generation
- Statistical overlays
- Video editing

Combine with `processing_data/frame2vid.py` to convert frame sequences back to video.

---

## Requirements Summary

- **Python 3.7+**
- **Dota 2** (with GSI enabled)
- **OBS Studio** (with WebSocket plugin for recording)
- **OpenCV** (for frame capture)
- **obs-websocket-py** (for OBS control)

This setup provides a complete pipeline for capturing, processing, and analyzing Dota 2 gameplay data with automated recording capabilities.

## Project Structure Overview

### Main Components

- **`python_server/`**: Main GSI server with OBS integration (see detailed README)
- **`obs/`**: Frame capture tools for OBS output (see detailed README)

### Draft/Experimental Components

These directories contain experimental or draft implementations that are not part of the main production system:

- **`example/`**: Legacy Node.js examples for basic GSI integration

  - `events.js`: Event-driven GSI client example
  - `polling.js`: Polling-based GSI client example

- **`react_server/`**: Experimental React-based GSI server implementation

  - Node.js server with React frontend
  - Alternative to the main Python server
  - Contains `package.json`, `server.js`, and related files

- **`processing_data/`**: Data processing utilities and converters

  - `combatlog_converter.js`: Combat log processing scripts
  - `frame2vid.py`: Convert captured frames back to video
  - `position.py`: Position/movement analysis tools
  - `combatlog_format.txt`: Combat log data format documentation

- **`test_server.py`**: Standalone test server for development
- **`test.py`**: Additional testing utilities

### Configuration Files

- **`gamestate_integration_dota2-gsi.cfg`**: Dota 2 GSI configuration template
- **`requirements.txt`**: Python dependencies for the main server
- **`LICENSE-MIT.md`**: Project license information

The main production system uses `python_server/` as the core component, with `obs/` providing complementary frame capture capabilities.
