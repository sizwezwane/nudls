# Dinopark Maintenance System (TypeScript Version)

This is a Node.js/TypeScript port of the Dinopark maintenance system backend.

## Tech Stack
- **Node.js**
- **TypeScript**
- **Express**: Web framework
- **SQLite**: Database (shared with the Python version)
- **Zod**: Validation and typing
- **Axios**: HTTP client for feed consumption
- **Node-cron**: Task scheduling

## Setup

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

The API will be available at `http://localhost:8001`.
- **Park Grid Status**: `http://localhost:8001/park/grid`
