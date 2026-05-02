from fastapi import FastAPI
from logging_middleware import Log
from priority_inbox import PriorityInbox
from api_client import fetch_notifications

app = FastAPI(title="Campus Notifications API")

@app.on_event("startup")
async def startup_event():
    # Example usage of the mandatory logger
    Log("backend", "info", "config", "FastAPI server starting up")

@app.get("/")
def health_check():
    Log("backend", "debug", "route", "Health check endpoint called")
    return {"status": "ok"}

@app.get("/priority-inbox")
def get_priority_inbox():
    """
    Returns the top 10 most important notifications based on Weight and Recency.
    """
    Log("backend", "info", "route", "Priority inbox endpoint called")
    
    # 1. Fetch raw notifications from the test server
    raw_notifications = fetch_notifications()
    
    if not raw_notifications:
        Log("backend", "warn", "route", "No notifications fetched or external API failed")
        return {"status": "error", "message": "Failed to fetch notifications"}

    # 2. Process through our O(log K) Min-Heap algorithm
    inbox = PriorityInbox(max_size=10)
    for notif in raw_notifications:
        inbox.add_notification(notif)
        
    # 3. Retrieve the sorted top 10
    top_10 = inbox.get_top_notifications()
    
    Log("backend", "info", "route", f"Successfully processed priority inbox. Returning {len(top_10)} items.")
    return {
        "status": "success",
        "count": len(top_10),
        "data": top_10
    }
