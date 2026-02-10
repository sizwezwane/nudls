
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
from app import crud, models, schemas
from app.database import get_db

router = APIRouter()

@router.get("/park/grid", response_model=List[List[schemas.ZoneStatus]])
def get_park_grid(db: Session = Depends(get_db)):
    # Fetch all data
    dinos = db.query(models.Dinosaur).all()
    logs = db.query(models.MaintenanceLog).all()

    # Map dinos by location
    dino_map = {}
    for d in dinos:
        if d.location:
            if d.location not in dino_map:
                dino_map[d.location] = []
            dino_map[d.location].append(d)

    # Map maintenance logs
    log_map = {l.location: l for l in logs}

    now = datetime.now(timezone.utc)
    
    grid = []
    # Columns A-Z
    cols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Rows 0-15
    for row_idx in range(16):
        row_data = []
        for col_char in cols:
            zone_id = f"{col_char}{row_idx}"
            
            zone_dinos = dino_map.get(zone_id, [])
            maint_log = log_map.get(zone_id)

            # Maintenance check
            maintenance_required = True
            if maint_log and maint_log.last_maintenance_time:
                # Ensure timezone awareness match
                log_time = maint_log.last_maintenance_time
                if log_time.tzinfo is None:
                    log_time = log_time.replace(tzinfo=timezone.utc) # Assume UTC if naive from DB
                
                diff = now - log_time
                if diff.days <= 30:
                    maintenance_required = False
            
            # Safety check
            is_safe = True
            carnivores = [d for d in zone_dinos if not d.herbivore]
            if carnivores:
                for carn in carnivores:
                    if not carn.last_fed_time:
                         is_safe = False
                         break
                    
                    fed_time = carn.last_fed_time
                    if fed_time.tzinfo is None:
                        fed_time = fed_time.replace(tzinfo=timezone.utc)
                    
                    # details from brief: "digesting their last meal"
                    # "estimated digestion time which is logged when the animal is first moved into the park"
                    # We have digestion_period_in_hours
                    
                    hours_since_fed = (now - fed_time).total_seconds() / 3600
                    if hours_since_fed > carn.digestion_period_in_hours:
                        is_safe = False
                        break
            
            row_data.append(schemas.ZoneStatus(
                id=zone_id,
                maintenance_required=maintenance_required,
                is_safe=is_safe,
                dinosaurs=zone_dinos
            ))
        grid.append(row_data)
    
    return grid

@router.get("/park/dinosaurs", response_model=List[schemas.Dinosaur])
def read_dinosaurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dinosaurs = crud.get_dinosaurs(db, skip=skip, limit=limit)
    return dinosaurs

@router.get("/park/dinosaurs/{dinosaur_id}", response_model=schemas.Dinosaur)
def read_dinosaur(dinosaur_id: int, db: Session = Depends(get_db)):
    db_dinosaur = crud.get_dinosaur(db, dinosaur_id=dinosaur_id)
    if db_dinosaur is None:
        pass # return 404
    return db_dinosaur
