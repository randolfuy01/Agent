# Pinecone & OpenAI API Chat Agent

## Overview
This project is an AI-powered chatbot that integrates Pinecone's vector database with OpenAI's language models to perform retrieval-augmented generation (RAG). The chatbot retrieves relevant documents from Pinecone based on user queries and generates responses using OpenAI's GPT model.

## Features
- Connects to Pinecone for vector similarity search
- Uses OpenAI's API for natural language processing
- Implements logging for error handling
- Loads environment variables from a `.env` file
- Docker support for containerized deployment
- WebSocket support for real-time chat interactions

## Installation

### Local Setup
1. **Clone the repository:**
 ```sh
git clone <your-repo-url>
cd <your-repo-name>
 ```

2. **Create a virtual environment (optional but recommended):**
 ```sh
python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
 ```

3. **Install dependencies:**
 ```sh
pip install -r requirements.txt
 ```

4. **Set up environment variables:**
 Create a `.env` file in the root directory and add your API keys:
 ```ini
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
PINECONE_HOST=your_pinecone_host
 ```

### Docker Setup
1. **Build and run using Docker script:**
 ```sh
# Make the script executable
chmod +x run-docker.sh

# Run the Docker container
./run-docker.sh
 ```

2. **Manual Docker commands (if not using script):**
 ```sh
# Build the Docker image
docker build -t myapp .

# Run the container
docker run -d \
    --name myapp \
    -p 8000:8000 \
    --restart unless-stopped \
    myapp
 ```

3. **Docker troubleshooting:**
 ```sh
# Check container logs
docker logs myapp

# Stop the container
docker stop myapp

# Remove the container
docker rm myapp

# Check port usage
lsof -i :8000

# Kill process using port 8000
sudo lsof -t -i:8000 | xargs kill -9
 ```

## Usage

### Initialize the Chat Agent
```python
from chat_agent import Chat_Agent
agent = Chat_Agent()
agent.instantiate_api()
```

### Query the Chatbot
```python
response = agent.response("Tell me about Randolf Uy")
print(response)
```

### WebSocket Connection
The API is available at `ws://localhost:8000/ws/{client_id}` when running locally or in Docker.

## Project Structure
```
.
├── src/                  # Source directory
│   ├── agent.py         # Main model for RAG
│   ├── main.py          # FastAPI WebSocket server
│   ├── test.py          # Unit testing script
│   └── vector.py        # Script for loading data into pinecone
├── Dockerfile           # Docker configuration
├── run-docker.sh        # Docker deployment script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── .dockerignore        # Docker ignore file
└── README.md           # Project documentation
```

## Troubleshooting
- Ensure your `.env` file contains the correct API keys
- Verify that your Pinecone index is accessible
- Check logs for errors if the chatbot fails to respond
- For Docker issues:
  - Ensure port 8000 is not in use
  - Check Docker logs using `docker logs myapp`
  - Verify Redis connection in Docker container
  - Ensure all required environment variables are set

## Rate Limiting
The WebSocket API implements rate limiting:
- 5 messages per 20-second window
- Exceeding this limit will trigger a warning message

## License
This project is licensed under the MIT License.
