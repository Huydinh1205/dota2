from __future__ import annotations
import cv2
import numpy as np
import os
import time
import datetime
import argparse
import subprocess
import sys

def ensure_dependencies():
    """Ensure all dependencies are installed"""
    try:
        import cv2
    except ImportError:
        print("Installing OpenCV...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
        import cv2

def capture_from_virtual_camera(output_folder="game_frames", interval=0.06, max_frames=None):
    """
    Capture frames from an OBS Virtual Camera feed
    
    Args:
        output_folder: Folder to save frames
        interval: Time between captures in seconds
        max_frames: Maximum number of frames to capture
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    # Open the virtual camera (typically camera 0 is the default)
    # If you have multiple cameras, OBS might be on a different index
    camera_idx = 0
    capture = None
    
    print("Looking for OBS Virtual Camera...")
    
    # Try different camera indices (0-5)
    for i in range(6):
        try:
            test_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            if test_cap.isOpened():
                # Check if this might be the OBS camera
                ret, frame = test_cap.read()
                if ret and frame is not None:
                    # This is a working camera
                    print(f"Found camera at index {i}")
                    # Ask user if this is the OBS virtual camera
                    answer = input(f"Is camera {i} the OBS Virtual Camera? (y/n): ")
                    if answer.lower() == 'y':
                        camera_idx = i
                        capture = test_cap
                        break
                    else:
                        test_cap.release()
            else:
                test_cap.release()
        except Exception as e:
            print(f"Error checking camera {i}: {e}")
    
    # If we haven't found the camera yet, try one more time with the user's index
    if capture is None:
        try:
            camera_idx = int(input("Enter the OBS Virtual Camera index (usually 0, 1, or 2): "))
            capture = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
            if not capture.isOpened():
                print("Could not open camera at specified index")
                return
        except Exception as e:
            print(f"Error opening camera: {e}")
            return
    
    print(f"Successfully connected to camera at index {camera_idx}")
    
    # Set resolution if needed (adjust these values to match your game resolution)
    # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Start capturing frames
    frame_count = 0
    start_time = time.time()
    
    print(f"Starting frame capture (saving to {os.path.abspath(output_folder)})...")
    print("Press Ctrl+C to stop capturing")
    
    try:
        while True:
            # Check if we've reached max frames
            if max_frames is not None and frame_count >= max_frames:
                print(f"Reached maximum frame count of {max_frames}")
                break
            
            # Capture frame
            ret, frame = capture.read()
            
            if ret and frame is not None:
                # Save frame
                filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(filename, frame)
                
                # Update counter
                frame_count += 1
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Captured {frame_count} frames ({fps:.2f} FPS)")
                
                # Wait for the specified interval
                time.sleep(interval)
            else:
                print("Failed to capture frame, retrying...")
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nCapture stopped by user (Ctrl+C)")
    finally:
        # Clean up
        if capture is not None:
            capture.release()
        
        # Print summary
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps = frame_count / elapsed
            print(f"Capture complete: {frame_count} frames in {elapsed:.2f} seconds ({fps:.2f} FPS)")

def capture_from_rtmp(rtmp_url="rtmp://localhost:1935/live/game", output_folder="game_frames", interval=0.06, max_frames=None):
    """
    Capture frames from an RTMP stream (OBS can stream to local RTMP)
    
    Args:
        rtmp_url: RTMP URL to capture from
        output_folder: Folder to save frames
        interval: Time between captures in seconds
        max_frames: Maximum number of frames to capture
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    # Open the RTMP stream
    capture = cv2.VideoCapture(rtmp_url)
    
    if not capture.isOpened():
        print(f"Could not open RTMP stream at {rtmp_url}")
        print("Make sure OBS is streaming to this URL")
        return
    
    print(f"Successfully connected to RTMP stream at {rtmp_url}")
    
    # Start capturing frames
    frame_count = 0
    start_time = time.time()
    
    print(f"Starting frame capture (saving to {os.path.abspath(output_folder)})...")
    print("Press Ctrl+C to stop capturing")
    
    try:
        while True:
            # Check if we've reached max frames
            if max_frames is not None and frame_count >= max_frames:
                print(f"Reached maximum frame count of {max_frames}")
                break
            
            # Capture frame
            ret, frame = capture.read()
            
            if ret and frame is not None:
                # Save frame
                filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(filename, frame)
                
                # Update counter
                frame_count += 1
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Captured {frame_count} frames ({fps:.2f} FPS)")
                
                # Wait for the specified interval
                time.sleep(interval)
            else:
                print("Failed to capture frame, retrying...")
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nCapture stopped by user (Ctrl+C)")
    finally:
        # Clean up
        capture.release()
        
        # Print summary
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps = frame_count / elapsed
            print(f"Capture complete: {frame_count} frames in {elapsed:.2f} seconds ({fps:.2f} FPS)")

def capture_from_monitor_preview(output_folder="game_frames", interval=0.06, max_frames=None, region=None):
    """
    Capture frames from OBS Preview window (must be visible on screen)
    
    Args:
        output_folder: Folder to save frames
        interval: Time between captures in seconds
        max_frames: Maximum number of frames to capture
        region: Region to capture (x, y, width, height) or None for full screen
    """
    # Try to import mss for screen capture
    try:
        import mss
    except ImportError:
        print("Installing mss screen capture library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mss"])
        import mss
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    # Set up screen capture
    sct = mss.mss()
    
    # If no region specified, ask user to define it
    if region is None:
        print("Please position the OBS Preview window so it's visible on screen")
        input("Press Enter when ready...")
        
        print("\nDefine the capture region:")
        try:
            x = int(input("Left position (x): "))
            y = int(input("Top position (y): "))
            width = int(input("Width: "))
            height = int(input("Height: "))
            region = {"left": x, "top": y, "width": width, "height": height}
        except ValueError:
            print("Invalid input. Using full screen.")
            region = sct.monitors[1]  # Primary monitor
    
    print(f"Capturing region: {region}")
    
    # Start capturing frames
    frame_count = 0
    start_time = time.time()
    
    print(f"Starting frame capture (saving to {os.path.abspath(output_folder)})...")
    print("Press Ctrl+C to stop capturing")
    
    try:
        while True:
            # Check if we've reached max frames
            if max_frames is not None and frame_count >= max_frames:
                print(f"Reached maximum frame count of {max_frames}")
                break
            
            # Capture screen region
            img = sct.grab(region)
            
            # Convert to numpy array
            frame = np.array(img)
            
            # Convert BGRA to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Save frame
            filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
            cv2.imwrite(filename, frame)
            
            # Update counter
            frame_count += 1
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"Captured {frame_count} frames ({fps:.2f} FPS)")
            
            # Wait for the specified interval
            time.sleep(interval)
                
    except KeyboardInterrupt:
        print("\nCapture stopped by user (Ctrl+C)")
    finally:
        # Print summary
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps = frame_count / elapsed
            print(f"Capture complete: {frame_count} frames in {elapsed:.2f} seconds ({fps:.2f} FPS)")

def main():
    # Ensure dependencies are installed
    ensure_dependencies()
    print(1)
    parser = argparse.ArgumentParser(description="Capture frames from OBS Studio")
    parser.add_argument("--method", type=str, default="menu", choices=["menu", "virtual-camera", "rtmp", "preview"],
                       help="Capture method to use")
    parser.add_argument("--output", type=str, default="game_frames",
                       help="Output folder for frames")
    parser.add_argument("--interval", type=float, default=0.06,
                       help="Time between captures in seconds (default: 0.06)")
    parser.add_argument("--max-frames", type=int, default=None,
                       help="Maximum number of frames to capture")
    parser.add_argument("--rtmp-url", type=str, default="rtmp://localhost:1935/live/game",
                       help="RTMP URL for RTMP capture method")
    print(2)
    args = parser.parse_args()
    print(3)
    # If method is menu, show menu
    if args.method == "menu":
        print("=== OBS Frame Capture ===")
        print("This tool extracts frames from OBS Studio's output.")
        print("\nSelect a capture method:")
        print("1. Virtual Camera (OBS Virtual Camera)")
        print("2. RTMP Stream (OBS Stream Output)")
        print("3. Preview Window (Screen Capture of OBS Preview)")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (1-3): "))
                if 1 <= choice <= 3:
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Set up OBS (instructions)
        if choice == 1:
            print("\n=== OBS Virtual Camera Setup ===")
            print("1. Open OBS Studio")
            print("2. Add your game as a 'Game Capture' source")
            print("3. Click 'Start Virtual Camera' in OBS")
            print("4. Once the virtual camera is running, press Enter to continue")
            input()
            
            capture_from_virtual_camera(args.output, args.interval, args.max_frames)
        
        elif choice == 2:
            print("\n=== OBS RTMP Stream Setup ===")
            print("1. Open OBS Studio")
            print("2. Add your game as a 'Game Capture' source")
            print("3. Go to Settings > Stream")
            print("4. Select 'Custom...' service")
            print("5. Set Server to 'rtmp://localhost:1935/live'")
            print("6. Set Stream Key to 'game'")
            print("7. Click 'Start Streaming' in OBS")
            print("8. Once streaming is active, press Enter to continue")
            print("\nNote: You need an RTMP server running. Try installing and running Nginx-RTMP.")
            input()
            
            rtmp_url = input("Enter RTMP URL (press Enter for default 'rtmp://localhost:1935/live/game'): ")
            if not rtmp_url:
                rtmp_url = "rtmp://localhost:1935/live/game"
            
            capture_from_rtmp(rtmp_url, args.output, args.interval, args.max_frames)
        
        elif choice == 3:
            print("\n=== OBS Preview Window Setup ===")
            print("1. Open OBS Studio")
            print("2. Add your game as a 'Game Capture' source")
            print("3. Position and size the OBS window so the preview is clearly visible")
            print("4. Once the preview is visible and showing the game, press Enter to continue")
            input()
            
            capture_from_monitor_preview(args.output, args.interval, args.max_frames)
    
    # Otherwise, use the specified method
    elif args.method == "virtual-camera":
        capture_from_virtual_camera(args.output, args.interval, args.max_frames)
    elif args.method == "rtmp":
        capture_from_rtmp(args.rtmp_url, args.output, args.interval, args.max_frames)
    elif args.method == "preview":
        capture_from_monitor_preview(args.output, args.interval, args.max_frames)

if __name__ == "__main__":
    main()
    
'''
ssh into GAME SERVER for pdd9
    - search for human study code and enter
    - go to controller/andrew_degrade_network.py
    - run: sudo systemctl stop openarena-fortress.service
    - run: python3 controller/andrew_degrade_network.py
'''
    
'''
a. Open OBS and configure Virtual Camera to: 
    - Output Type: Source
    - Output Selection: Game Capture

b. python obs_game_capture.py

c. Select a capture method:
    1. Virtual Camera (OBS Virtual Camera)
    2. RTMP Stream (OBS Stream Output)
    3. Preview Window (Screen Capture of OBS Preview)
    - Enter your choice (1-3): 1

d. Found camera at index 1
    - Is camera 1 the OBS Virtual Camera? (y/n): y
    
e. Enter the OBS Virtual Camera index (usually 0, 1, or 2): 1
    - Successfully connected to camera at index 1
'''
