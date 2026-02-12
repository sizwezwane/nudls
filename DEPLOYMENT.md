# Deployment Guide: Updating the EC2 Instance

The API has been migrated from Python to **Node.js/TypeScript**. Since the security groups on the EC2 instance are already configured for port **8000**, the new version has been set to use the same port.

### Prerequisites
- Docker and Docker Compose installed on the EC2 instance.

### Steps to Deploy

1. **SSH into the Instance**:
   ```bash
   ssh -i "your-key.pem" ubuntu@13.245.109.136
   ```

2. **Clean up old Python containers** (if any):
   ```bash
   sudo docker stop $(sudo docker ps -q --filter ancestor=nudls-backend)
   sudo docker rm $(sudo docker ps -aq --filter ancestor=nudls-backend)
   ```

3. **Clone/Update the code**:
   ```bash
   cd ~/nudls
   git pull origin main
   ```

4. **Build the New TypeScript Image**:
   ```bash
   sudo docker build -t dinopark-backend .
   ```

5. **Run the New Container**:
   ```bash
   # Using port 8000 and mounting the database for persistence
   sudo docker run -d \
     --name dinopark-api \
     -p 8000:8000 \
     -v $(pwd)/dinopark.db:/app/dinopark.db \
     --restart unless-stopped \
     dinopark-backend
   ```

6. **Verify**:
   Visit `http://13.245.109.136:8000/` in your browser.
   The welcome message should now say: **"Welcome to Dinopark Maintenance API"**.

### Troubleshooting
- **Logs**: Run `sudo docker logs -f dinopark-api` to see real-time output.
- **Port Conflict**: If port 8000 is still in use, run `sudo lsof -i :8000` to find the process and kill it.
