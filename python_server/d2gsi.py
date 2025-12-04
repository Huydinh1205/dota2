import json
import os
from flask import Flask, request, jsonify
from typing import Dict, Any, List, Optional, Callable
import threading

class Events:
    """Simple event emitter implementation"""
    def __init__(self):
        self._events: Dict[str, List[Callable]] = {}

    def on(self, event: str, handler: Callable):
        """Register an event handler"""
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(handler)

    def emit(self, event: str, *args, **kwargs):
        """Emit an event to all registered handlers"""
        if event in self._events:
            for handler in self._events[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event handler for '{event}': {e}")

# Global event emitter and client list
events = Events()
clients: List['GSIClient'] = []

class GSIClient:
    def __init__(self, ip: str, auth: str):
        self.ip = ip
        self.auth = auth
        self.gamestate: Dict[str, Any] = {}
        self._events = Events()

    def emit(self, event: str, *args, **kwargs):
        """Emit event on this client"""
        self._events.emit(event, *args, **kwargs)

    def on(self, event: str, handler):
        """Register event handler for this client"""
        self._events.on(event, handler)

def check_client():
    """Middleware to check if client exists or create new one"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr

            # Check if this IP is already talking to us
            req_client = None
            for client in clients:
                if client.ip == client_ip:
                    req_client = client
                    break

            if req_client is None:
                # Create a new client
                auth_token = request.json.get('auth', {}).get('token', '') if request.json else ''
                new_client = GSIClient(client_ip, auth_token)
                clients.append(new_client)
                req_client = new_client
                req_client.gamestate = request.json or {}

                # Notify about the new client
                events.emit("newclient", new_client)

            # Add client to request object
            request.client = req_client
            return f(*args, **kwargs)
        return wrapper
    return decorator

def emit_all(prefix: str, obj: Dict[str, Any], emitter):
    """Emit all keys in an object with prefix"""
    for key, value in obj.items():
        emitter.emit(f"{prefix}{key}", value)

def recursive_emit(prefix: str, changed: Dict[str, Any], body: Dict[str, Any], emitter):
    """Recursively emit changed game state"""
    for key, value in changed.items():
        if isinstance(value, dict):
            if key in body and body[key] is not None:
                recursive_emit(f"{prefix}{key}:", value, body[key], emitter)
        else:
            # Got a key
            if key in body and body[key] is not None:
                if isinstance(body[key], dict):
                    # Edge case on added:item/ability:x where added shows true at the top level
                    emit_all(f"{prefix}{key}:", body[key], emitter)
                else:
                    emitter.emit(f"{prefix}{key}", body[key])

def process_changes(section: str):
    """Middleware to process changes in a section"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if request.json and section in request.json:
                recursive_emit("", request.json[section], request.json, request.client)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def update_gamestate():
    """Middleware to update client gamestate"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            request.client.gamestate = request.json or {}
            return f(*args, **kwargs)
        return wrapper
    return decorator

def check_auth(tokens: Optional[List[str]]):
    """Middleware to check authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if tokens:
                req_auth = request.json.get('auth', {}) if request.json else {}
                req_token = req_auth.get('token', '') if isinstance(req_auth, dict) else ''

                if req_token and (req_token in tokens or req_token == tokens):
                    return f(*args, **kwargs)
                else:
                    print(f"Dropping message from IP: {request.remote_addr}, no valid auth token")
                    return jsonify({"error": "Invalid auth token"}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator

def new_data():
    """Handle new data and log it"""
    request.client.emit("newdata", request.json)

    # Log data to file
    try:
        log_data = json.dumps(request.json, indent=2)
        with open("gsi_log.txt", "a", encoding="utf8") as f:
            f.write(log_data + "\n")
    except Exception as e:
        print(f"Error logging data: {e}")

    return "", 200

def create_d2gsi_app(options: Optional[Dict[str, Any]] = None):
    """Create and configure the Dota 2 GSI Flask app"""
    options = options or {}
    port = options.get('port', 3000)
    tokens = options.get('tokens', None)
    host = options.get('ip', '0.0.0.0')

    app = Flask(__name__)

    # Ensure log file exists and is empty
    try:
        with open("gsi_log.txt", "w", encoding="utf8") as f:
            f.write("")
    except Exception as e:
        print(f"Warning: Could not initialize log file: {e}")

    @app.route('/', methods=['POST'])
    @check_auth(tokens)
    @check_client()
    @update_gamestate()
    @process_changes("previously")
    @process_changes("added")
    def handle_post():
        return new_data()

    # Store reference to events for external access
    app.events = events

    return app, host, port

if __name__ == '__main__':
    app, host, port = create_d2gsi_app()
    print(f"Dota 2 GSI listening on {host}:{port}")
    app.run(host=host, port=port, debug=False)
