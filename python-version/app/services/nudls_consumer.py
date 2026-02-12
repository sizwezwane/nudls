
import logging
import requests
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, crud, schemas
from app.database import SessionLocal

logger = logging.getLogger(__name__)

NUDLS_FEED_URL = "https://dinoparks.herokuapp.com/nudls/feed"

def fetch_and_process_feed():
    logger.info("Starting NUDLS feed fetch...")
    try:
        response = requests.get(NUDLS_FEED_URL, timeout=10)
        response.raise_for_status()
        events = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch NUDLS feed: {e}")
        return

    # Process events.
    # The feed is a list of events clearly in reverse chronological order?
    # Or random?
    # Example snippet in previous turn showed newest first (2026-02-09 then 2026-02-08).
    # To process correctly (state reconstruction), we should process OLDEST first.
    # So we reverse the list.
    
    # Sort events by time just in case.
    try:
        events.sort(key=lambda x: x['time'])
    except KeyError:
        logger.warning("Events missing 'time' field, processing as is.")

    db = SessionLocal()
    try:
        for event in events:
            process_event(db, event)
    except Exception as e:
        logger.error(f"Error processing events: {e}")
    finally:
        db.close()
    logger.info("Finished processing NUDLS feed.")

def process_event(db: Session, event: dict):
    kind = event.get('kind')
    event_time_str = event.get('time')
    if not event_time_str:
        return
    
    # Parse time. Format: "2026-02-09T18:23:14.428Z"
    # Python 3.11+ supports 'Z' with fromisoformat, but earlier might need replacement.
    # Safe to replace 'Z' with '+00:00'
    try:
        event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
    except ValueError:
        logger.warning(f"Invalid time format: {event_time_str}")
        return

    if kind == 'dino_added':
        dino_id = event.get('id')
        existing = db.query(models.Dinosaur).filter(models.Dinosaur.id == dino_id).first()
        if not existing:
            # Create
            new_dino = models.Dinosaur(
                id=dino_id,
                name=event.get('name'),
                species=event.get('species'),
                gender=event.get('gender'),
                digestion_period_in_hours=event.get('digestion_period_in_hours'),
                herbivore=event.get('herbivore'),
                location=None, # Not set in added?
                last_fed_time=None,
                last_location_update_time=None # Use event_time? No, added time isn't update time.
            )
            db.add(new_dino)
            db.commit()
            
    elif kind == 'dino_removed':
        crud.remove_dinosaur(db, event.get('dinosaur_id'))

    elif kind == 'dino_location_updated':
        dino_id = event.get('dinosaur_id')
        loc = event.get('location')
        # Check existing time
        dino = crud.get_dinosaur(db, dino_id)
        if dino:
            # Only update if event_time is newer than what we have
            if not dino.last_location_update_time or event_time > dino.last_location_update_time.replace(tzinfo=event_time.tzinfo):
                 dino.location = loc
                 dino.last_location_update_time = event_time
                 db.commit()
    
    elif kind == 'dino_fed':
        dino_id = event.get('dinosaur_id')
        dino = crud.get_dinosaur(db, dino_id)
        if dino:
            if not dino.last_fed_time or event_time > dino.last_fed_time.replace(tzinfo=event_time.tzinfo):
                dino.last_fed_time = event_time
                db.commit()

    elif kind == 'maintenance_performed':
        loc = event.get('location')
        log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.location == loc).first()
        if not log:
            log = models.MaintenanceLog(location=loc, last_maintenance_time=event_time)
            db.add(log)
            db.commit()
        else:
            if event_time > log.last_maintenance_time.replace(tzinfo=event_time.tzinfo):
                log.last_maintenance_time = event_time
                db.commit()
