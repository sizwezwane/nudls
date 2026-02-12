
# Deployment Guide: Hosting on AWS

This guide outlines two ways to host the Nudls Dinopark API on AWS.

**Current Deployment**: The API is currently running on an AWS EC2 instance at `http://13.245.109.136:8000/`.

## Option 1: AWS App Runner (Containerized & Autoscaling)
**Best for**: Demonstrating modern cloud-native deployment (Docker).
**Limitation**: Since we are using **SQLite** (a file-based DB), the database will reset if the container restarts. **For production, you must use AWS RDS**.

### Prerequisites
1.  [AWS CLI](https://aws.amazon.com/cli/) installed and configured (`aws configure`).
2.  Docker installed.

### Steps

1.  **Create an ECR Repository** (to store your Docker image):
    ```bash
    aws ecr create-repository --repository-name nudls-backend
    # Note the "repositoryUri" in the output (e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com/nudls-backend)
    export REPO_URI=123456789012.dkr.ecr.us-east-1.amazonaws.com/nudls-backend
    ```

2.  **Login to ECR**:
    ```bash
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REPO_URI
    ```

3.  **Build and Push the Image**:
    ```bash
    docker build -t nudls-backend .
    docker tag nudls-backend:latest $REPO_URI:latest
    docker push $REPO_URI:latest
    ```

4.  **Create App Runner Service**:
    *   Go to the [AWS App Runner Console](https://console.aws.amazon.com/apprunner).
    *   Click **Create service**.
    *   Source: **Container image**.
    *   URI: Browse and select the image you just pushed.
    *   Deployment settings: **Automatic** (optional).
    *   **Configuration**:
        *   Port: `8000`
        *   Env Vars: Add any if needed (none are strictly required for SQLite default).
    *   Create & Deploy.

5.  **Access**:
    *   App Runner provides a public HTTPS URL (e.g., `https://xyz.us-east-1.awsapprunner.com`).
    *   Grid: `https://xyz.../park/grid`

---

## Option 2: EC2 Instance (Persistent setup with SQLite)
**Best for**: Keeping the SQLite database data persistent on a single machine.

### Steps

1.  **Launch EC2 Instance**:
    *   Go to **EC2 Console** -> **Launch Instance**.
    *   AMI: **Ubuntu 22.04 LTS**.
    *   Instance Type: `t2.micro` (Free tier eligible).
    *   Key Pair: Create one and download the `.pem` file.
    *   Security Group: Allow **SSH (22)** and **Custom TCP (8000)** from Anywhere (`0.0.0.0/0`).

2.  **SSH into the Instance**:
    ```bash
    chmod 400 keypair.pem
    ssh -i "keypair.pem" ubuntu@<PUBLIC-IP>
    ```

3.  **Setup and Run**:
    ```bash
    # Update and install Docker
    sudo apt update
    sudo apt install -y docker.io git

    # Clone your code (upload via git or scp)
    git clone https://github.com/YOUR_USER/nudls.git
    cd nudls/python-version

    # Build and Run
    sudo docker build -t nudls-backend .
    # Mount local dir for persistence (DB at parent dir level in this setup)
    sudo docker run -d -p 8000:8000 -e DATABASE_URL=sqlite:///./dinopark.db -v $(pwd):/app nudls-backend
    ```

4.  **Access**:
    *   `http://<PUBLIC-IP>:8000/park/grid`

---

## Production Note: Switching to RDS

To make **Option 1** robust and persistent:

1.  Create a PostgreSQL database in **AWS RDS**.
2.  Update `app/database.py` to use `os.getenv("DATABASE_URL")` instead of the hardcoded SQLite path.
3.  Install `psycopg2-binary` in `requirements.txt`.
4.  Pass the RDS connection string as an environment variable in App Runner.
