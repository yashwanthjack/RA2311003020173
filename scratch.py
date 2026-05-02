import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notification_app_be.api_client import fetch_notifications

if __name__ == "__main__":
    print("Testing Notification API...")
    res = fetch_notifications()
    print("Result:", res)
