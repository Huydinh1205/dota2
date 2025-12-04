from __future__ import annotations
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Circle, RegularPolygon
import sys
import json

def load_multi_json(text):
    decoder = json.JSONDecoder()
    idx = 0
    length = len(text)
    objects = []

    while idx < length:
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break

        obj, new_idx = decoder.raw_decode(text, idx)
        objects.append(obj)
        idx = new_idx
    return objects

class DotaPositionVisualizer:
    def __init__(self, log_file='gsi_log.txt'):
        self.log_file = log_file
        self.data_entries = []
        self.map_bounds = {'x': [-8000, 8000], 'y': [-8000, 8000]}
        self.load_data()

    def load_data(self):
        print(f"Loading {self.log_file}...")
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.data_entries = load_multi_json(content)
        print(f"Loaded {len(self.data_entries)} game state entries")

    def extract_positions_at_timestamp(self, timestamp_index):
        """Extract hero positions and watchers at a specific timestamp"""
        if timestamp_index >= len(self.data_entries):
            return None, None, None

        entry = self.data_entries[timestamp_index]

        # Extract timestamp and game time
        timestamp = entry.get('provider', {}).get('timestamp', 0)
        game_time = entry.get('map', {}).get('game_time', 0)

        # Extract hero positions
        heroes = {'radiant': [], 'dire': []}

        hero_data = entry.get('hero', {})
        for team_key, team_name in [('team2', 'radiant'), ('team3', 'dire')]:
            team_data = hero_data.get(team_key, {})
            for player_key, player_data in team_data.items():
                player_data = team_data.get(player_key)
                if player_data and 'xpos' in player_data and 'ypos' in player_data:
                    hero_info = {
                        'x': player_data['xpos'],
                        'y': player_data['ypos'],
                        'name': player_data.get('name', f'{team_name}_{player_key}').replace('npc_dota_hero_', ''),
                        'alive': player_data.get('alive', True),
                        'level': player_data.get('level', 1)
                    }
                    heroes[team_name].append(hero_info)

        # Extract watchers
        watchers = []
        map_data = entry.get('map', {})
        watchers_data = map_data.get('watchers', {})
        for watcher_key in [f'watcher{i}' for i in range(8)]:
            watcher_data = watchers_data.get(watcher_key)
            if watcher_data:
                watcher_info = {
                    'x': watcher_data.get('location_x', 0),
                    'y': watcher_data.get('location_y', 0),
                    'state': watcher_data.get('capture_state', 'not_captured')
                }
                watchers.append(watcher_info)
        print(f"Extracted positions for timestamp index {timestamp_index}: {len(heroes['radiant'])} Radiant heroes, {len(heroes['dire'])} Dire heroes, {len(watchers)} watchers")
        return heroes, watchers, (timestamp, game_time)

    def create_map_background(self):
        """Create the Dota 2 map background with key locations"""
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_xlim(self.map_bounds['x'])
        ax.set_ylim(self.map_bounds['y'])
        ax.set_aspect('equal')

        # Set dark background
        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#1a1a1a')

        # Draw the main map boundaries (approximate)
        # River
        river_width = 200
        ax.fill_between([-8000, 8000], [-river_width/2, -river_width/2], [river_width/2, river_width/2],
                       color='#2e5c8a', alpha=0.3)

        # Towers (simplified representation)
        tower_positions = [
            # Radiant top lane
            (-5500, 3500), (-4500, 4500), (-3500, 5500),
            # Radiant mid lane
            (-1500, 1500), (-500, 500),
            # Radiant bottom lane
            (3500, -5500), (4500, -4500), (5500, -3500),
            # Dire top lane
            (-5500, -3500), (-4500, -4500), (-3500, -5500),
            # Dire mid lane
            (-1500, -1500), (-500, -500),
            # Dire bottom lane
            (3500, 5500), (4500, 4500), (5500, 3500)
        ]

        for tower_x, tower_y in tower_positions:
            ax.add_patch(Circle((tower_x, tower_y), 150, color='#8B4513', alpha=0.7))

        # Ancient locations
        ax.add_patch(Circle((5500, 5500), 300, color='#FFD700', alpha=0.5))  # Radiant ancient
        ax.add_patch(Circle((-5500, -5500), 300, color='#FF4500', alpha=0.5))  # Dire ancient

        # Jungle camps (simplified)
        camp_positions = [
            (-3000, 1000), (1000, 3000), (3000, -1000), (-1000, -3000)  # Radiant camps
        ]
        for camp_x, camp_y in camp_positions:
            ax.add_patch(Circle((camp_x, camp_y), 100, color='#228B22', alpha=0.4))

        return fig, ax

    def plot_positions(self, heroes, watchers, timestamp_info, ax):
        """Plot heroes and watchers on the map"""
        timestamp, game_time = timestamp_info

        # Clear previous positions
        for artist in ax.lines + ax.collections + ax.patches[-8:]:  # Keep map elements, remove dynamic ones
            if hasattr(artist, 'get_xy') or hasattr(artist, 'get_paths'):
                if not isinstance(artist, Circle) or artist.get_radius() > 200:  # Keep map circles
                    continue
            artist.remove()

        # Plot heroes
        for team, color, label in [('radiant', '#00BFFF', 'Radiant'), ('dire', '#FF6347', 'Dire')]:
            team_heroes = heroes.get(team, [])
            for hero in team_heroes:
                if hero['alive']:
                    # Hero position
                    ax.scatter(hero['x'], hero['y'], c=color, s=200, alpha=0.8, edgecolors='white', linewidth=2)

                    # Hero name and level
                    ax.text(hero['x'] + 50, hero['y'] + 50, f"{hero['name']}\nLv.{hero['level']}",
                           fontsize=8, color='white', ha='left', va='bottom',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.7))
                else:
                    # Dead hero (grayed out)
                    ax.scatter(hero['x'], hero['y'], c='#808080', s=150, alpha=0.5, marker='x')

        # Plot watchers
        for watcher in watchers:
            # Triangle for observers
            triangle = RegularPolygon((watcher['x'], watcher['y']),numVertices=3,
    radius=120,
                                    color='#32CD32' if watcher['state'] == 'radiant' else
                                         '#FF69B4' if watcher['state'] == 'dire' else '#FFFF00',
                                    alpha=0.8, orientation=0)
            ax.add_patch(triangle)

        # Add timestamp info
        minutes = game_time // 60
        seconds = game_time % 60
        time_str = f"{minutes}:{seconds:02d}"
        ax.set_title(f"Dota 2 Match Positions - Game Time: {time_str} - Timestamp: {timestamp}",
                    color='white', fontsize=14, pad=20)

        return ax

    def animate_positions(self, start_frame=0, end_frame=None, interval=1000):
        """Animate positions through time"""
        if end_frame is None:
            end_frame = len(self.data_entries) - 1

        fig, ax = self.create_map_background()

        def animate(frame):
            frame_idx = start_frame + frame
            if frame_idx >= len(self.data_entries):
                return

            heroes, watchers, timestamp_info = self.extract_positions_at_timestamp(frame_idx)
            if heroes is not None:
                self.plot_positions(heroes, watchers, timestamp_info, ax)
            return ax,

        anim = animation.FuncAnimation(fig, animate, frames=end_frame-start_frame+1,
                                     interval=interval, repeat=False)

        plt.tight_layout()
        plt.show()

    def show_frame(self, frame_index):
        """Show a single frame at the given index"""
        fig, ax = self.create_map_background()

        heroes, watchers, timestamp_info = self.extract_positions_at_timestamp(frame_index)
        if heroes is not None:
            self.plot_positions(heroes, watchers, timestamp_info, ax)
        else:
            print(f"No data available for frame {frame_index}")

        plt.tight_layout()
        plt.show()

    def find_frame_by_timestamp(self, target_timestamp):
        """Find the frame index closest to the target timestamp"""
        if not self.data_entries:
            return None

        closest_index = 0
        closest_diff = abs(self.data_entries[0].get('provider', {}).get('timestamp', 0) - target_timestamp)

        for i, entry in enumerate(self.data_entries):
            timestamp = entry.get('provider', {}).get('timestamp', 0)
            diff = abs(timestamp - target_timestamp)
            if diff < closest_diff:
                closest_diff = diff
                closest_index = i

        return closest_index, closest_diff

    def find_frame_by_game_time(self, target_game_time):
        """Find the frame index closest to the target game time"""
        if not self.data_entries:
            return None

        closest_index = 0
        closest_diff = abs(self.data_entries[0].get('map', {}).get('game_time', 0) - target_game_time)

        for i, entry in enumerate(self.data_entries):
            game_time = entry.get('map', {}).get('game_time', 0)
            diff = abs(game_time - target_game_time)
            if diff < closest_diff:
                closest_diff = diff
                closest_index = i

        return closest_index, closest_diff

    def show_timestamp(self, target_timestamp):
        """Show positions at a specific timestamp"""
        frame_index, time_diff = self.find_frame_by_timestamp(target_timestamp)
        if frame_index is not None:
            print(f"Found frame {frame_index} with timestamp difference of {time_diff} seconds")
            self.show_frame(frame_index)
        else:
            print("No data loaded")

    def show_game_time(self, target_game_time):
        """Show positions at a specific game time (in seconds)"""
        frame_index, time_diff = self.find_frame_by_game_time(target_game_time)
        if frame_index is not None:
            print(f"Found frame {frame_index} with game time difference of {time_diff} seconds")
            self.show_frame(frame_index)
        else:
            print("No data loaded")

    def show_latest_frame(self):
        """Show the most recent frame"""
        if self.data_entries:
            self.show_frame(len(self.data_entries) - 1)
        else:
            print("No data loaded")

def main():
    visualizer = DotaPositionVisualizer()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'animate':
            # Animate through all frames
            start_frame = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            end_frame = int(sys.argv[3]) if len(sys.argv) > 3 else None
            interval = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
            visualizer.animate_positions(start_frame, end_frame, interval)
        elif sys.argv[1] == 'frame':
            # Show specific frame
            frame_index = int(sys.argv[2]) if len(sys.argv) > 2 else len(visualizer.data_entries) - 1
            visualizer.show_frame(frame_index)
        elif sys.argv[1] == 'timestamp':
            # Show positions at specific timestamp
            if len(sys.argv) > 2:
                target_timestamp = int(sys.argv[2])
                visualizer.show_timestamp(target_timestamp)
            else:
                print("Usage: python position.py timestamp <timestamp>")
        elif sys.argv[1] == 'gametime':
            # Show positions at specific game time (in seconds)
            if len(sys.argv) > 2:
                target_game_time = int(sys.argv[2])
                visualizer.show_game_time(target_game_time)
            else:
                print("Usage: python position.py gametime <seconds>")
        elif sys.argv[1] == 'latest':
            # Show latest frame
            visualizer.show_latest_frame()
        else:
            print("Usage:")
            print("  python position.py                          # Show latest frame")
            print("  python position.py latest                   # Show latest frame")
            print("  python position.py frame <index>            # Show specific frame")
            print("  python position.py timestamp <timestamp>    # Show positions at specific timestamp")
            print("  python position.py gametime <seconds>       # Show positions at specific game time")
            print("  python position.py animate [start] [end] [interval_ms]  # Animate frames")
    else:
        # Default: show latest frame
        visualizer.show_latest_frame()

if __name__ == "__main__":
    main()
