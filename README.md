
# Dinopark Maintenance System (NUDLS Backend)

This is a Python-based backend solution for the Dinopark maintenance system, built with **FastAPI**. It consumes the NUDLS dinosaur feed and exposes a RESTful API for the park dashboard.

**Live Demo**: The API is currently deployed on AWS EC2 at [http://13.245.109.136:8000/docs](http://13.245.109.136:8000/docs).

## Setup and Running

### Prerequisites
- Python 3.9+
- pip

### Installation

1.  **Clone the repository** (if not already):
    ```bash
    git clone <repo_url>
    cd nudls
    ```

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

Start the server using `uvicorn`:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Park Grid Status**: `http://localhost:8000/park/grid`

### Running with Docker (Optional)

Alternatively, you can run the application using Docker:

```bash
docker build -t nudls-backend .
docker run -p 8000:8000 nudls-backend
```

### Running Tests

Run the test suite using `pytest`:

```bash
TESTING=1 pytest tests/
```

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on how to host this application on AWS.

---

## Approach & Architecture

I chose **FastAPI** (Python) for this solution because of its high performance, automatic validation (Pydantic), and ease of use for building REST APIs efficiently.

### Key Components

1.  **Database (SQLite)**: Start simple with a local SQLite database (`dinopark.db`) to persist dinosaur and maintenance states. This meets the persistence requirement without external infrastructure dependencies for a local task.
2.  **NUDLS Consumer Service**: A background service (scheduled via `APScheduler`) that polls the unreliable NUDLS feed every minute. It parses events to reconstruct the current state of the park.
    - **Robustness**: It handles network timeouts and ensures data consistency by processing events chronologically and checking timestamps to avoid overwriting newer data with old events.
    - **Offline Capability**: Since we persist state to the DB, the API remains available even if the feed goes down.
3.  **Park Grid Logic**: The `/park/grid` endpoint aggregates data from `dinosaurs` and `maintenance_logs` to calculate the status of each zone (Safe/Unsafe, Maintenance Required/Not Required) in real-time based on the business rules provided.

### Trade-offs
- **Polling vs Webhook**: The brief mentions a webhook isn't available yet, so I implemented robust polling. If webhooks were available, I would expose a `POST` endpoint to receive events in real-time.
- **In-Memory Calculation**: The grid calculation fetches all dinos. For 26x16 zones, this is efficient. For 1 million dinos, this would need optimization (see Scaling section).

---

## Technical Questions

### 1. Resiliency & Uptime (99.99%)

To achieve 99.99% uptime (approx 52 mins downtime/year):

-   **Redundancy**: Deploy multiple instances of the API behind a Load Balancer (e.g., AWS ALB or Nginx). If one instance fails, traffic is routed to others.
-   **Database Reliability**: Move from SQLite to a managed implementation like Amazon RDS (PostgreSQL/Aurora) with Multi-AZ deployment for automatic failover.
-   **Caching**: Implement Redis to cache the Grid response. Even if the DB is under load or down, we can serve stale but available data for a short TTL.
-   **Feed Decoupling**: The feed consumer should be a separate worker service (e.g., utilizing a queue like SQS/Celery) rather than running inside the API process. This prevents feed processing issues from affecting API availability.

### 2. Scaling (1 Million Dinosaurs)

The current "fetch all and map in memory" approach will break with 1M dinosaurs due to memory and latency constraints.

**Changes:**
-   **Database indexing**: Ensure `location` columns are indexed (already done in this solution).
-   **Spatial/Zone Queries**: Instead of loading all dinos, query counts and "unsafe" flags per zone using SQL aggregation.
    -   Example: `SELECT location, COUNT(*) FROM dinosaurs WHERE herbivore=False AND (last_fed_time < NOW() - interval) GROUP BY location`.
    -   This offloads the heavy lifting to the DB engine.
-   **Pagination**: The grid is fixed size, but `GET /dinosaurs` must be paginated (already implemented default limit=100).
-   **Sharding**: If write volume from the feed is massive, shard the DB by dinosaur ID or Park Zone.

### 3. Firebase Recommendation

Park Technical asked about Firebase.

**Recommendation**: **It depends**, but generally **Proceed with Caution** for this specific use case.

-   **Pros**: Real-time database (Firestore) is excellent for the "live dashboard" requirement. Frontend devs could subscribe to document changes directly without polling our API.
-   **Cons**:
    -   **Complex Queries**: Firebase NoSQL queries are limited compared to SQL. Calculating "safety" based on complex conditions (time diffs) across collections can be tricky and might require cloud functions.
    -   **Vendor Lock-in**: Harder to migrate away from than a standard SQL/Container solution.
    -   **Cost**: rapid state updates (polling feed -> frequent writes) can get expensive at scale.

**Verdict**: If the team wants a *very fast* MVP with real-time updates for the dashboard, Firebase is great. But given the safety-critical nature and complex relational rules (Maintenance vs Time vs Dinos), a relational DB (SQL) provides strict consistency and powerful querying which is safer for "lives depend on this".

---

## Retrospective

### What would I do differently?
-   **Database Migration**: Use Alembic for DB migrations instead of `Base.metadata.create_all`. This allows evolving the schema safely.
-   **Async IO**: Use `httpx` and `asyncpg` (if Postgres) for fully asynchronous I/O to handle higher concurrency.
-   **Authentication**: Add API Key or OAuth middleware to secure the endpoints.
-   **Frontend**: Build a simple React frontend to visualize the grid (as requested by the "outsourced" team).

### What I learned
-   Parsing "unreliable" event logs requires careful thinking about order of operations and idempotency.
-   Balancing "safe defaults" (unsafe if unknown) vs usability.

### How to improve this challenge
-   Provide a test dataset or a mock feed that doesn't require internet, or a Docker setup for the feed.
-   Clarify the grid coordinate system (0-indexed vs 1-indexed) explicitly in examples.
