import requests
import json
import os
import threading

# Get the absolute path to the token file (two levels up from this script)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
LOG_API_URL = "http://20.207.122.201/evaluation-service/logs"

def get_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f).get('access_token')
    except Exception:
        return None

def _send_log(payload, token):
    """Background worker to send the log without blocking the main thread"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        # short timeout so we don't hang threads
        requests.post(LOG_API_URL, json=payload, headers=headers, timeout=3.0)
    except Exception as e:
        # Silently fail in prod so we don't crash the app if the logging server is down
        print(f"[Logging Middleware Error] Failed to send log: {e}")

def Log(stack: str, level: str, package: str, message: str):
    token = get_token()
    
    # Always print locally for debugging
    print(f"[LOCAL DBG] [{level.upper()}] {package}: {message}")
    
    # Fallback to local print if token is missing
    if not token:
        print(f"[{level.upper()}] {package}: {message} (Token missing)")
        return
        
    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }
    
    # Fire and forget using a daemon thread to keep FastAPI fast
    thread = threading.Thread(target=_send_log, args=(payload, token))
    thread.daemon = True
    thread.start()
