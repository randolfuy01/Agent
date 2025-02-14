# Use python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Redis and supervisor
RUN apt-get update && apt-get install -y \
    redis-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "uvicorn[standard]"

# Copy the src directory contents to /app
COPY src/* /app/

# Copy other necessary files
COPY . .

# Expose the necessary ports
EXPOSE 8000
EXPOSE 6379

# Copy the supervisor configuration file to the container
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start supervisor which will handle both Redis and FastAPI
CMD ["/usr/bin/supervisord"]
