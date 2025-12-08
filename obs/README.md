# OBS Integration Tools

This directory contains tools for capturing frames and video from OBS Studio output, complementing the automated recording system in `python_server`.

## Overview

The OBS tools provide multiple methods to capture gameplay footage:

- **Virtual Camera Capture**: Capture from OBS Virtual Camera
- **RTMP Stream Capture**: Capture from OBS streaming output
- **Preview Window Capture**: Screen capture of OBS preview
- **Frame Processing**: Convert captured frames to video

## Files Structure

```
obs/
├── obs.py              # Main frame capture tool
├── game_frames/        # Captured frame images
├── output.mp4          # Processed video output
└── README.md           # This documentation
```

## obs.py - Frame Capture Tool

A comprehensive tool for extracting frames from OBS Studio using multiple capture methods.

### Features

- **Multiple Capture Methods**: Virtual Camera, RTMP, Screen Capture
- **Auto-Detection**: Automatically finds OBS Virtual Camera
- **High Performance**: Optimized for real-time capture (16.7 FPS)
- **Flexible Output**: Configurable frame folders and intervals
- **Interactive Setup**: Guided configuration for each method

### Usage

#### Interactive Mode (Recommended)

```bash
python obs.py
```

**Menu Options:**
1. **Virtual Camera**: Capture from OBS Virtual Camera (recommended)
2. **RTMP Stream**: Capture from OBS streaming output
3. **Preview Window**: Screen capture of OBS preview window

#### Command Line Mode

```bash
# Virtual Camera capture
python obs.py --method virtual-camera --output my_frames --interval 0.06

# RTMP Stream capture
python obs.py --method rtmp --rtmp-url rtmp://localhost:1935/live/game

# Preview capture with custom region
python obs.py --method preview --max-frames 1000
```

### Capture Methods

#### 1. Virtual Camera (Recommended)

**Setup:**
1. Open OBS Studio
2. Add Dota 2 as Game Capture source
3. Go to `Tools` → `Virtual Camera` → `Start`
4. Run frame capture tool and select option 1

**Pros:**
- Direct capture from OBS output
- No screen capture performance impact
- Clean, processed video feed
- Automatic camera detection

**Requirements:**
- OBS Virtual Camera started
- Game Capture source configured

#### 2. RTMP Stream Capture

**Setup:**
1. Open OBS Studio
2. Configure streaming settings:
   - Service: Custom
   - Server: `rtmp://localhost:1935/live`
   - Stream Key: `game`
3. Start streaming in OBS
4. Run capture tool and select option 2

**Pros:**
- Network-based capture
- Can capture remotely
- OBS handles encoding

**Requirements:**
- RTMP server (nginx-rtmp recommended)
- OBS streaming configuration

#### 3. Preview Window Capture

**Setup:**
1. Open OBS Studio with game capture
2. Position/size OBS window for clear preview
3. Run capture tool and select option 3
4. Define capture region when prompted

**Pros:**
- No OBS configuration needed
- Works with any OBS setup
- Simple screen capture

**Cons:**
- Performance impact from screen capture
- Requires OBS window to be visible
- May capture other screen elements

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--method` | menu | Capture method (virtual-camera, rtmp, preview) |
| `--output` | game_frames | Output folder for frames |
| `--interval` | 0.06 | Seconds between captures (~16.7 FPS) |
| `--max-frames` | None | Maximum frames to capture |
| `--rtmp-url` | rtmp://localhost:1935/live/game | RTMP stream URL |

### Output

**Frame Files:**
```
game_frames/
├── frame_000000.jpg
├── frame_000001.jpg
├── frame_000002.jpg
└── ...
```

**Naming Convention:**
- `frame_{6-digit-number}.jpg`
- Zero-padded for proper sorting
- JPEG format for efficient storage

**Performance:**
- ~16.7 FPS (every 0.06 seconds)
- Progress reporting every 100 frames
- Automatic cleanup on interruption

## Dependencies

### Required Packages

```bash
pip install opencv-python mss
```

### System Requirements

- **Windows**: DirectShow for camera access
- **OpenCV**: For image processing and camera capture
- **MSS**: For screen capture (preview method)

## Integration with Python Server

The frame capture tools complement the automated recording system:

### Use Cases

1. **Automated Recording** (python_server):
   - Full match recordings with OBS
   - Automatic start/stop based on game events
   - High-quality video with OBS encoding

2. **Frame Analysis** (obs tools):
   - Extract individual frames for AI analysis
   - Custom frame rates and regions
   - Research and statistical analysis

### Combined Workflow

```bash
# 1. Start main server for automated recording
cd python_server
python server.py

# 2. In parallel, capture frames for analysis
cd obs
python obs.py --method virtual-camera --output analysis_frames
```

## Video Processing

Captured frames can be converted back to video using `processing_data/frame2vid.py`:

```bash
python processing_data/frame2vid.py --input obs/game_frames --output obs/output.mp4
```

## Troubleshooting

### Virtual Camera Issues

**"Could not open camera"**
- Ensure OBS Virtual Camera is started
- Try different camera indices (0, 1, 2...)
- Restart OBS Virtual Camera

**"Camera not found"**
- Verify OBS is running with Virtual Camera enabled
- Check Windows camera permissions
- Try restarting OBS

### RTMP Stream Issues

**"Could not open RTMP stream"**
- Verify RTMP server is running (nginx-rtmp)
- Check OBS streaming settings
- Confirm stream URL and key

**Connection timeout**
- Ensure firewall allows RTMP traffic
- Check network connectivity
- Verify OBS is actively streaming

### Preview Capture Issues

**"Screen capture failed"**
- Ensure OBS preview window is visible
- Check capture region coordinates
- Try running as administrator

**Performance problems**
- Close other applications
- Reduce capture resolution
- Increase capture interval

### General Issues

**Low frame rate**
- Reduce `--interval` value (minimum 0.01)
- Close background applications
- Check system resources

**Storage space**
- Monitor disk space during long captures
- Use `--max-frames` to limit capture duration
- Consider JPEG compression settings

## Performance Optimization

### For High FPS Capture
```bash
python obs.py --method virtual-camera --interval 0.01 --output high_fps_frames
```

### For Long Duration Capture
```bash
python obs.py --method virtual-camera --max-frames 10000 --interval 0.1
```

### For Analysis-Ready Frames
```bash
python obs.py --method virtual-camera --interval 0.06 --output analysis_frames
```

## File Formats

- **Input**: Live OBS video stream
- **Output**: Individual JPEG frames (frame_XXXXXX.jpg)
- **Frame Rate**: Configurable (default 16.7 FPS)
- **Resolution**: Matches OBS output resolution

## Security Considerations

- Virtual Camera capture is local only
- RTMP streams may be network accessible
- Screen capture may include sensitive information
- Store captured frames securely
- Consider privacy implications of recorded gameplay
