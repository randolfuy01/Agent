# Pinecone & OpenAI API Chat Agent

## Overview
This project is an AI-powered chatbot that integrates Pinecone's vector database with OpenAI's language models to perform retrieval-augmented generation (RAG). The chatbot retrieves relevant documents from Pinecone based on user queries and generates responses using OpenAI's GPT model.

## Features
- Connects to Pinecone for vector similarity search
- Uses OpenAI's API for natural language processing
- Implements logging for error handling
- Loads environment variables from a `.env` file

## Installation

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Create a virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
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

## Project Structure
```
.
├── src                  # Source directory
|    |--- agent.py       # Main model for RAG
|    |___ test.py        # Unit testing script 
|    |___ vector.py      # Script for loading data into pinecone
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── README.md            # Project documentation
```

## Troubleshooting
- Ensure your `.env` file contains the correct API keys.
- Verify that your Pinecone index is accessible.
- Check logs for errors if the chatbot fails to respond.

## License
This project is licensed under the MIT License.

