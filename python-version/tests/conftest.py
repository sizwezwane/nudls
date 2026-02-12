
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import Dinosaur, MaintenanceLog # Ensure models are registered explicitly

from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    # Make sure app events (and scheduler) don't run or run harmlessly
    # For simplicity, we create tables.
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # We can block scheduler if needed, but for now client is enough.
    # Note: Using TestClient inside fixture might trigger app startup if using lifespan.
    # We can use TestClient(app) inside test function or here.
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
