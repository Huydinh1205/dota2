import requests
import json
import time

# Test data simulating Dota 2 GSI payload
test_payload = {
    "auth": {
        "token": "my_secret_token_12345"
    },
    "hero": {
        "health_percent": 85,
        "level": 12,
        "alive": True,
        "position": {"x": 1234, "y": 5678}
    },
    "abilities": {
        "ability0": {
            "level": 3,
            "can_cast": True
        }
    },
    "items": {
        "slot0": {
            "name": "item_blink"
        },
        "slot1": {
            "name": "item_force_staff"
        }
    },
    "player": {
        "kills": 5,
        "deaths": 2,
        "assists": 8
    },
    "previously": {
        "hero": {
            "health_percent": True
        }
    },
    "added": {
        "items": {
            "slot0": True
        }
    }
}

def test_server():
    """Test the Flask GSI server with sample data"""
    url = "http://localhost:3000/"

    print("Testing Dota 2 GSI Flask server...")
    print("Make sure the server is running (python server.py)")

    try:
        # Test 1: Send initial payload
        print("\n1. Sending initial game state...")
        response = requests.post(url, json=test_payload)
        print(f"Response status: {response.status_code}")

        # Test 2: Send updated health
        print("\n2. Sending health update...")
        health_update = {
            "auth": {"token": "my_secret_token_12345"},
            "hero": {"health_percent": 45},
            "previously": {"hero": {"health_percent": True}}
        }
        response = requests.post(url, json=health_update)
        print(f"Response status: {response.status_code}")

        # Test 3: Send level up
        print("\n3. Sending level up...")
        level_update = {
            "auth": {"token": "my_secret_token_12345"},
            "hero": {"level": 13},
            "previously": {"hero": {"level": True}}
        }
        response = requests.post(url, json=level_update)
        print(f"Response status: {response.status_code}")

        # Test 4: Send item purchase
        print("\n4. Sending item purchase...")
        item_update = {
            "auth": {"token": "my_secret_token_12345"},
            "items": {"slot2": {"name": "item_ultimate_scepter"}},
            "added": {"items": {"slot2": True}}
        }
        response = requests.post(url, json=item_update)
        print(f"Response status: {response.status_code}")

        # Test 5: Invalid token
        print("\n5. Testing invalid auth token...")
        invalid_auth = {
            "auth": {"token": "invalid_token"},
            "hero": {"health_percent": 100}
        }
        response = requests.post(url, json=invalid_auth)
        print(f"Response status: {response.status_code} (should be 401)")

        print("\nTest completed! Check the server console for event logs.")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure server.py is running.")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    test_server()
