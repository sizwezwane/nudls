
from app import models
from app.database import SessionLocal
from datetime import datetime, timedelta, timezone

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Dinopark Maintenance API"}

def test_park_grid_initial(client):
    response = client.get("/park/grid")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 16 # Rows
    assert len(data[0]) == 26 # Columns
    # Check default safe state (no dinos -> safe)
    assert data[0][0]["is_safe"] == True
    # Maintenance required since no logs exist?
    # Logic in service: checks logs. If log exists and diff <= 30 days -> OK. 
    # If NO log, then maintenance_required default=True (step 98 line 40). Correct.
    assert data[0][0]["maintenance_required"] == True

def test_safety_logic(client):
    # Setup state via direct DB manipulation using override session logic
    # But conftest overrides get_db, so we need access to that session or create one bound to same engine.
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    
    now = datetime.now(timezone.utc)
    
    # CASE 1: Herbivore -> Safe
    # Create distinct dino ID
    d1 = models.Dinosaur(
        id=1, name="Herbie", species="Stego", gender="M", 
        digestion_period_in_hours=4, herbivore=True, 
        location="A0", last_fed_time=None
    )
    db.add(d1)
    
    # CASE 2: Carnivore, hungry (never fed) -> Unsafe
    d2 = models.Dinosaur(
        id=2, name="Rex", species="TRex", gender="M", 
        digestion_period_in_hours=48, herbivore=False, 
        location="B0", last_fed_time=None
    )
    db.add(d2)
    
    # CASE 3: Carnivore, fed recently (< digestion period) -> Safe (digesting)
    # Digestion period 48h. Fed 1 hour ago.
    fed_time_safe = now - timedelta(hours=1)
    d3 = models.Dinosaur(
        id=3, name="RexJunior", species="TRex", gender="M", 
        digestion_period_in_hours=48, herbivore=False, 
        location="C0", last_fed_time=fed_time_safe
    )
    db.add(d3)

    # CASE 4: Carnivore, fed long ago (> digestion period) -> Unsafe (finished digesting)
    # Digestion period 48h. Fed 50 hours ago.
    fed_time_unsafe = now - timedelta(hours=50)
    d4 = models.Dinosaur(
        id=4, name="RexSenior", species="TRex", gender="M", 
        digestion_period_in_hours=48, herbivore=False, 
        location="D0", last_fed_time=fed_time_unsafe
    )
    db.add(d4)

    db.commit()
    db.close()

    # Query API
    response = client.get("/park/grid")
    assert response.status_code == 200
    grid = response.json()
    
    # Verify A0 (Herbivore) -> Safe
    # A0 is row 0, col 0? "A" is index 0. "0" is row index 0.
    zone_A0 = grid[0][0]
    assert zone_A0["id"] == "A0"
    assert zone_A0["is_safe"] == True

    # Verify B0 (Hungry Carnivore) -> Unsafe
    zone_B0 = grid[0][1] # B is index 1
    assert zone_B0["id"] == "B0"
    assert zone_B0["is_safe"] == False
    
    # Verify C0 (Digesting Carnivore) -> Safe
    zone_C0 = grid[0][2] # C is index 2
    assert zone_C0["id"] == "C0"
    assert zone_C0["is_safe"] == True

    # Verify D0 (Finished Digesting Carnivore) -> Unsafe
    zone_D0 = grid[0][3] # D is index 3
    assert zone_D0["id"] == "D0"
    assert zone_D0["is_safe"] == False

def test_maintenance_logic(client):
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    
    # CASE 1: Maintained recently -> Not required
    m1 = models.MaintenanceLog(location="A1", last_maintenance_time=now - timedelta(days=5))
    db.add(m1)
    
    # CASE 2: Maintained long ago -> Required
    m2 = models.MaintenanceLog(location="B1", last_maintenance_time=now - timedelta(days=31))
    db.add(m2)
    
    db.commit()
    db.close()
    
    response = client.get("/park/grid")
    grid = response.json()
    
    # A1 is Row 1 (index 1), Col A (index 0)
    zone_A1 = grid[1][0] 
    assert zone_A1["id"] == "A1"
    assert zone_A1["maintenance_required"] == False
    
    # B1 is Row 1 (index 1), Col B (index 1)
    zone_B1 = grid[1][1]
    assert zone_B1["id"] == "B1"
    assert zone_B1["maintenance_required"] == True
