import os
import json
import requests
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_middleware import Log

# Locate the token.json file at the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
NOTIFICATIONS_API_URL = "http://20.207.122.201/evaluation-service/notifications"

def fetch_notifications():
    try:
        if not os.path.exists(TOKEN_FILE):
            return [], f"Token file missing at {TOKEN_FILE}"

        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            token = token_data.get('access_token')

        if not token:
            return [], "Access token missing from token.json"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Log the outgoing external request
        Log("backend", "info", "api", "Fetching notifications from remote test server")

        response = requests.get(NOTIFICATIONS_API_URL, headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get("notifications", [])
            Log("backend", "info", "api", f"Successfully fetched {len(notifications)} notifications")
            return notifications, None
        else:
            err = f"Failed to fetch notifications. Status: {response.status_code}, Body: {response.text}"
            Log("backend", "error", "api", err)
            return [], err

    except Exception as e:
        err = f"Critical error while fetching notifications: {str(e)}"
        Log("backend", "fatal", "api", err)
        return [], err
