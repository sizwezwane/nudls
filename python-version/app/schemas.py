
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DinosaurBase(BaseModel):
    name: str
    species: str
    gender: str
    digestion_period_in_hours: int
    herbivore: bool
    location: Optional[str] = None
    last_fed_time: Optional[datetime] = None
    last_location_update_time: Optional[datetime] = None

class DinosaurCreate(DinosaurBase):
    id: int

class Dinosaur(DinosaurBase):
    id: int

    class Config:
        from_attributes = True

class MaintenanceLogBase(BaseModel):
    location: str
    last_maintenance_time: datetime

class MaintenanceLog(MaintenanceLogBase):
    class Config:
        from_attributes = True

class ZoneStatus(BaseModel):
    id: str  # e.g. "A1"
    maintenance_required: bool
    is_safe: bool
    dinosaurs: List[Dinosaur] = []

class ParkGrid(BaseModel):
    zones: List[List[ZoneStatus]]
