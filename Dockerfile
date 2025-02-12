FROM python:3.10-slim
WORKDIR /app

# Install Redis
RUN apt-get update && apt-get install -y redis-server

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory contents to /app
COPY src/* /app/

# Copy other necessary files
COPY . .

EXPOSE 8000

# Start Redis server and run the application
CMD service redis-server start && python -m uvicorn main:app --host 0.0.0.0 --port 8000