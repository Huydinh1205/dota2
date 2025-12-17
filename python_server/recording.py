from __future__ import annotations

from pathlib import Path
import time
try:
    from obswebsocket import obsws, requests as obs_requests
    OBS_AVAILABLE = True
except ImportError:
    print("⚠️ WARNING: obs-websocket-py not installed!")
    print("Install it with: pip install obs-websocket-py")
    OBS_AVAILABLE = False
# OBS Recording Configuration
class RecordingManager:
    def __init__(self, matches_folder=".", obs_host="localhost", obs_port=4455, obs_password=""):
        self.matches_folder = Path(matches_folder)
        self.in_progress = False
        self.running = True  # Auto-start recording mode
        self.current_match_id = None
        
        # OBS WebSocket connection
        self.obs_client = None
        self.obs_connected = False
        
        if OBS_AVAILABLE:
            try:
                print(f"[OBS] Connecting to OBS at {obs_host}:{obs_port}...")
                self.obs_client = obsws(obs_host, obs_port, obs_password)
                self.obs_client.connect()
                self.obs_connected = True
                print("[OBS] ✅ Connected to OBS successfully!")
            except Exception as e:
                print(f"[OBS] ❌ Failed to connect to OBS: {e}")
                print("[OBS] Make sure OBS is running and WebSocket server is enabled")
        else:
            print("[OBS] obs-websocket-py not available, recording will be simulated only")
    def get_unique_match_path(self, match_id):
        base_path = self.matches_folder / str(match_id)
        if not base_path.exists():
            return base_path

        index = 1
        while True:
            new_path = self.matches_folder / f"{match_id}_{index}"
            if not new_path.exists():
                return new_path
            index += 1


    def start_recording(self, match_id):
        """Start OBS recording for a match"""
        if self.in_progress:
            print("[RECORDING] Already in progress")
            return
            
        match_path = self.matches_folder / str(match_id)
        
        try:
            # 🔥 LUÔN lấy folder mới nếu bị trùng
            match_path = self.get_unique_match_path(match_id)

            print(f"[RECORDING] Creating folder: {match_path}")
            match_path.mkdir(parents=True)

            # Create sync file
            sync_file = match_path / "sync.txt"
            sync_file.write_text(
                f"Recording started - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            print(f"[RECORDING] *** STARTING RECORDING for Match {match_id} ***")
            print(f"[RECORDING] Recording path: {match_path}")

            # Set OBS recording path
            if self.obs_connected:
                try:
                    self.obs_client.call(
                        obs_requests.SetRecordDirectory(
                            recordDirectory=str(match_path.absolute())
                        )
                    )
                    print(f"[OBS] Set recording path to: {match_path.absolute()}")
                except Exception as e:
                    print(f"[OBS] Warning: Could not set recording path: {e}")

            # Start recording
            if self.obs_connected:
                try:
                    self.obs_client.call(obs_requests.StartRecord())
                    print("[OBS] ✅ Recording started in OBS!")
                except Exception as e:
                    print(f"[OBS] ❌ Failed to start recording: {e}")
            else:
                print("[RECORDING] 📝 Simulated start (OBS not connected)")

            self.in_progress = True
            self.current_match_id = match_id

        except Exception as e:
            print(f"[ERROR] Failed to start recording: {e}")
            import traceback
            traceback.print_exc()

    print("[DEBUG] NOT DO ANYTHING ELSE IN start_recording!")

    
    def stop_recording(self):
        """Stop OBS recording"""
        print(f"[DEBUG] stop_recording called!")
        if not self.in_progress:
            return
            
        print(f"[RECORDING] *** STOPPING RECORDING for Match {self.current_match_id} ***")
        
        # Stop OBS recording
        if self.obs_connected:
            try:
                self.obs_client.call(obs_requests.StopRecord())
                print("[OBS] ✅ Recording stopped in OBS!")
            except Exception as e:
                print(f"[OBS] ❌ Failed to stop recording: {e}")
        else:
            print("[RECORDING] 📝 Simulated stop (OBS not connected)")
        
        self.in_progress = False
        self.current_match_id = None
    
    def disconnect(self):
        """Disconnect from OBS"""
        if self.obs_connected and self.obs_client:
            try:
                self.obs_client.disconnect()
                print("[OBS] Disconnected from OBS")
            except:
                pass
    
    def handle_game_state(self, data):
        """Process game state and manage recording"""
        print(f"[DEBUG] handle_game_state called!")
        print(f"[DEBUG] Recording manager running: {self.running}")
        print(f"[DEBUG] Recording in progress: {self.in_progress}")
        print(f"[DEBUG] Data received: {data is not None}")
        
        if not self.running:
            print("[RECORDING] Recording manager is disabled")
            return
        
        if not data:
            print("[DEBUG] No data received")
            return
        
        # Extract game data
        try:
            map_data = data.get("map", {})
            if not map_data:
                print("[DEBUG] No 'map' data in payload")
                self.stop_recording()
                
            game_state = map_data.get("game_state")
            match_id = map_data.get("matchid")
            game_time = map_data.get("game_time")
            
            print(f"[DEBUG] Extracted data:")
            print(f"  - Game State: {game_state}")
            print(f"  - Match ID: {match_id}")
            print(f"  - Game Time: {game_time}")
            
            # If no game state, we might be disconnected - stop recording
            if not game_state:
                print("[DEBUG] No game_state - possibly disconnected")
                if self.in_progress:
                    print("[RECORDING] No game state detected, stopping recording")
                    self.stop_recording()
                return
            
            # Skip early game states (before match starts)
            if game_state in [
                "DOTA_GAMERULES_STATE_INIT",
                "DOTA_GAMERULES_STATE_WAIT_FOR_PLAYERS_TO_LOAD",
            ]:
                print(f"[RECORDING] Skipping early state: {game_state}")
                return
            
            # Start recording when game actually starts
            if match_id and not self.in_progress:
                print(f"[DEBUG] Match ID exists and not recording yet")
                # Start recording on hero selection or when game is in progress
                if game_state in [
                    "DOTA_GAMERULES_STATE_HERO_SELECTION",
                    "DOTA_GAMERULES_STATE_STRATEGY_TIME",
                    "DOTA_GAMERULES_STATE_PRE_GAME",
                    "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS",
                ]:
                    print(f"[DEBUG] ✅ Conditions met! Starting recording...")
                    self.start_recording(match_id)
                else:
                    print(f"[DEBUG] ❌ Game state '{game_state}' not in trigger list")
            elif not match_id:
                print(f"[DEBUG] ❌ No match ID found")
                # If we were recording but now there's no match ID, stop
                if self.in_progress:
                    print("[RECORDING] Match ID lost, stopping recording")
                    self.stop_recording()
            elif self.in_progress:
                print(f"[DEBUG] ℹ️ Already recording match {self.current_match_id}")
            
            # Stop recording when game ends
            # This matches the original auto_record_dota2.py behavior
            if self.in_progress and game_state in [
                "DOTA_GAMERULES_STATE_POST_GAME",
                "DOTA_GAMERULES_STATE_DISCONNECT",
            ]:
                print(f"[RECORDING] Game ending (state: {game_state}), stopping recording...")
                self.stop_recording()
                
        except KeyError as e:
            print(f"[ERROR] Missing key in game state data: {e}")
            # If we're recording and data is malformed, might mean disconnected
            if self.in_progress:
                print("[RECORDING] Data error during recording, stopping as safety measure")
                self.stop_recording()
        except Exception as e:
            print(f"[ERROR] Error handling game state: {e}")
            import traceback
            traceback.print_exc()
