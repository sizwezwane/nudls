FROM node:20-slim

WORKDIR /app

# Install build dependencies for sqlite3 (required for some environments)
RUN apt-get update && apt-get install -y \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy package manifests
COPY package*.json ./

# Install dependencies including tsx
RUN npm install

# Copy project source
COPY . .

# Expose the API port
EXPOSE 8001

# The application expects dinopark.db at the root (/app/dinopark.db)
# Persist with a volume when running: 
# docker run -p 8001:8001 -v $(pwd)/dinopark.db:/app/dinopark.db <image_name>

CMD ["npm", "run", "start"]
