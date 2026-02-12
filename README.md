# Dinopark Maintenance System

This is a Node.js/TypeScript backend solution for the Dinopark maintenance system. It consumes the NUDLS dinosaur feed and exposes a RESTful API for the park dashboard.

## Tech Stack
- **Node.js**
- **TypeScript**
- **Express**: Web framework
- **SQLite**: Database persistence
- **Zod**: Validation and typing
- **Axios**: HTTP client for feed consumption
- **Node-cron**: Task scheduling

## Setup and Running

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run in development mode**:
   ```bash
   npm run dev
   ```

3. **Run in production mode**:
   ```bash
   npm run start
   ```

The API will be available at `http://localhost:8000`.
- **Park Grid Status**: `http://localhost:8000/park/grid`

## Running Tests
Run the test suite using `jest`:
```bash
npm test
```

## Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on how to host and update this application on the existing AWS EC2 instance.

## Running with Docker

1. **Build the image**:
   ```bash
   docker build -t dinopark-backend .
   ```

2. **Run the container**:
   ```bash
   # Mount the database file for persistence
   docker run -d -p 8000:8000 -v $(pwd)/dinopark.db:/app/dinopark.db --name nudls-api dinopark-backend
   ```

## Infrastructure & Uptime

### 1. Resiliency & Uptime (99.99%)

To achieve 100% (or 99.99%) uptime:
- **Redundancy**: Deploy multiple instances behind a Load Balancer (ELB/ALB).
- **Managed Database**: Move from local SQLite to a managed service like Amazon RDS (PostgreSQL/MySQL) with Multi-AZ for failover.
- **Failover**: Use Route53 for DNS-level failover.

### 2. Scaling (1 Million Dinosaurs)

To handle 1M dinosaurs:
- **Database Indexing**: Ensure spatial and status columns are indexed.
- **Aggregation Queries**: Perform the "Safe/Unsafe" calculations at the database layer using SQL aggregations instead of loading all data into memory.
- **Caching**: Use Redis to cache the grid status.

### 3. Firebase Recommendation

While Firebase (Firestore) is great for real-time dashboards, for this safety-critical system, a relational database (SQL) is recommended to ensure strict data consistency and perform complex safety calculations reliably.
