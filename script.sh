#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' 

echo -e "${GREEN}Starting Docker deployment script...${NC}"

# Stop any existing container with the same name
echo "Stopping existing containers..."
docker stop myapp 2>/dev/null || true
docker rm myapp 2>/dev/null || true

# Remove existing image
echo "Removing existing image..."
docker rmi myapp 2>/dev/null || true

# Build the new image
echo "Building new Docker image..."
if docker build -t myapp .; then
    echo -e "${GREEN}Docker image built successfully${NC}"
else
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
fi

# Run the container
echo "Starting container..."
if docker run -d \
    --name myapp \
    -p 8000:8000 \
    -p 6379:6379 \
    --restart unless-stopped \
    myapp; then
    echo -e "${GREEN}Container started successfully${NC}"
else
    echo -e "${RED}Failed to start container${NC}"
    exit 1
fi

# Check if container is running
if docker ps | grep myapp > /dev/null; then
    echo -e "${GREEN}Container is running!${NC}"
    echo "You can access the API at http://localhost:8000"
    echo "To view logs, run: docker logs myapp"
    echo "To stop the container, run: docker stop myapp"
else
    echo -e "${RED}Container failed to start properly${NC}"
    echo "Checking logs..."
    docker logs myapp
fi
