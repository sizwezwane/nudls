# Dinopark Maintenance System (NUDLS Backend)

This project provides a backend solution for the Dinopark maintenance system. It is available in two implementations:

## 📂 Project Structure

- **[python-version/](./python-version/)**: The original implementation using **FastAPI** (Python).
- **[typescript-version/](./typescript-version/)**: A port using **Express** (Node.js/TypeScript).
- **dinopark.db**: Shared SQLite database used by both implementations.

---

## 🚀 Live Demo

The API is currently deployed on AWS EC2 (Python version) at:
[http://13.245.109.136:8000/docs](http://13.245.109.136:8000/docs)

---

## 🛠 Choose Your Version

### Python (FastAPI)
See the [Python Version README](./python-version/README.md) for setup and running instructions.
- Default Port: `8000`

### TypeScript (Express)
See the [TypeScript Version README](./typescript-version/README.md) for setup and running instructions.
- Default Port: `8001`

---

## 📝 Approach & Architecture
Both versions follow the same core logic:
1. **Feed Consumer**: Robust background polling of the NUDLS feed with state reconstruction.
2. **Persistence**: Persistent state storage in SQLite.
3. **API**: RESTful endpoints for the park dashboard, including the real-time grid status.

For more details on scaling, resiliency, and technical trade-offs, please refer to the version-specific documentation.
