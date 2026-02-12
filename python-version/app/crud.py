
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime

def get_dinosaur(db: Session, dinosaur_id: int):
    return db.query(models.Dinosaur).filter(models.Dinosaur.id == dinosaur_id).first()

def get_dinosaurs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Dinosaur).offset(skip).limit(limit).all()

def create_dinosaur(db: Session, dinosaur: schemas.DinosaurCreate):
    db_dino = models.Dinosaur(
        id=dinosaur.id,
        name=dinosaur.name,
        species=dinosaur.species,
        gender=dinosaur.gender,
        digestion_period_in_hours=dinosaur.digestion_period_in_hours,
        herbivore=dinosaur.herbivore,
        # location and other fields default to None or passed
        location=dinosaur.location,
        last_fed_time=dinosaur.last_fed_time,
        last_location_update_time=dinosaur.last_location_update_time
    )
    db.add(db_dino)
    db.commit()
    db.refresh(db_dino)
    return db_dino

def update_dinosaur_location(db: Session, dinosaur_id: int, location: str, time: datetime):
    db_dino = get_dinosaur(db, dinosaur_id)
    if db_dino:
        # Check timestamp order if needed, but feed might be out of order. usually we take latest.
        # But we don't have existing timestamp stored for location update in db for comparison (except maybe a new column).
        # We'll just update for now. Ideally we check if event time > stored time.
        db_dino.location = location
        db_dino.last_location_update_time = time
        db.commit()
        db.refresh(db_dino)
    return db_dino

def feed_dinosaur(db: Session, dinosaur_id: int, time: datetime):
    db_dino = get_dinosaur(db, dinosaur_id)
    if db_dino:
        # Check if this feed is newer? Or just update.
        db_dino.last_fed_time = time
        db.commit()
        db.refresh(db_dino)
    return db_dino

def remove_dinosaur(db: Session, dinosaur_id: int):
    # Depending on requirements, maybe soft delete? Or hard delete.
    # "dino_removed" usually implies gone.
    db.query(models.Dinosaur).filter(models.Dinosaur.id == dinosaur_id).delete()
    db.commit()

def log_maintenance(db: Session, location: str, time: datetime):
    db_log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.location == location).first()
    if not db_log:
        db_log = models.MaintenanceLog(location=location, last_maintenance_time=time)
        db.add(db_log)
    else:
        # Only update if new time is more recent
        if time > db_log.last_maintenance_time:
            db_log.last_maintenance_time = time
    db.commit()
    db.refresh(db_log)
    return db_log

def get_all_maintenance(db: Session):
    return db.query(models.MaintenanceLog).all()
