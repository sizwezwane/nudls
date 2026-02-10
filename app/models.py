
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

class Dinosaur(Base):
    __tablename__ = "dinosaurs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    species = Column(String)
    gender = Column(String)
    digestion_period_in_hours = Column(Integer)
    herbivore = Column(Boolean)
    location = Column(String, index=True, nullable=True)
    last_fed_time = Column(DateTime, nullable=True)
    last_location_update_time = Column(DateTime, nullable=True)

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    location = Column(String, primary_key=True, index=True)
    last_maintenance_time = Column(DateTime)
