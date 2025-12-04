import shutil
import time
import os

# Source and destination paths
src = "D:/SteamLibrary/steamapps/common/dota 2 beta/game/dota/combatlog.txt"
dest = "D:/HuyDinh/dota2-gsi/combatlog.txt"

def copy_combatlog():
    """Copy combatlog.txt from Dota 2 directory to local directory"""
    try:
        if os.path.exists(src):
            shutil.copy2(src, dest)
            print(f"Copied combatlog at {time.strftime('%H:%M:%S')}")
        else:
            print(f"Source file not found: {src}")
    except Exception as e:
        print(f"Error copying combatlog: {e}")

if __name__ == "__main__":
    print("Starting combatlog copier...")
    while True:
        copy_combatlog()
        time.sleep(1)  # copy every second
