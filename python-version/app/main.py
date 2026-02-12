
from fastapi import FastAPI, Depends
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers import park
from app.database import engine, Base
from app.services.nudls_consumer import fetch_and_process_feed
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(park.router)

@app.on_event("startup")
def startup_event():
    import os
    if os.getenv("TESTING"):
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_process_feed, 'interval', minutes=1)
    scheduler.start()
    
    # Run fetch once immediately to populate data on startup
    try:
        fetch_and_process_feed()
    except Exception as e:
        logger.error(f"Initial feed fetch failed: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to Dinopark Maintenance API"}
