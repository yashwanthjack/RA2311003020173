from fastapi import FastAPI
from logging_middleware import Log

app = FastAPI(title="Campus Notifications API")

@app.on_event("startup")
async def startup_event():
    # Example usage of the mandatory logger
    Log("backend", "info", "config", "FastAPI server starting up")

@app.get("/")
def health_check():
    Log("backend", "debug", "route", "Health check endpoint called")
    return {"status": "ok"}
