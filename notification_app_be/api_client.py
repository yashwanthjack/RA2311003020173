import os
import json
import requests
from logging_middleware import Log

# Locate the token.json file at the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
NOTIFICATIONS_API_URL = "http://20.207.122.201/evaluation-service/notifications"

def fetch_notifications():
    """
    Fetches the raw list of notifications from the Evaluation Server API.
    Uses the mandatory logging middleware to track the request lifecycle.
    """
    try:
        if not os.path.exists(TOKEN_FILE):
            Log("backend", "error", "api", "Token file missing. Cannot fetch notifications.")
            return []

        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            token = token_data.get('access_token')

        if not token:
            Log("backend", "error", "api", "Access token missing from token.json")
            return []

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
            return notifications
        else:
            Log("backend", "error", "api", f"Failed to fetch notifications. Status: {response.status_code}")
            return []

    except Exception as e:
        Log("backend", "fatal", "api", f"Critical error while fetching notifications: {str(e)}")
        return []
