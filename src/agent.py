from pinecone import Pinecone
from dotenv import load_dotenv
import openai
import logging
import os
import time


class Chat_Agent:
    """
    Integration agent using vector embeddings and LLM
    """

    def __init__(self, index_name="personalbot"):

        # Logger for error handling
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.pinecone = None
        self.open_ai_agent = None
        self.index_name = index_name

    def instantiate_api(self) -> None:
        """
        Instantiating pinecone connection for random augmented retrieval
        """
        local = load_dotenv()
        if not local:
            self.logger.info("Unable to load env variables")
            return
        
        try:
            local = load_dotenv()
        except Exception as e:
            self.logger.error("Unable to locate local environment")

        # Instantiate the pinecone connection
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                self.logger.error("No api key provided for pinecone")
                return
            self.pinecone = Pinecone(api_key=api_key)
            self.logger.info(f"pinecone connection instantiated successfullly")
        except Exception as e:
            self.logger.error(
                f"Unable to instantiate pinecone connection using api key: {e}"
            )

        # Instantiate the openai connection
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.logger.error("No api key provided for openai")
                return
            self.open_ai_agent = openai.OpenAI(api_key=api_key)
            self.logger.info(f"openai connection instantiated successfully")
        except Exception as e:
            self.logger.error(f"Unable to create openai connection using api key: {e}")

    def load_index(self):
        """
        Loads the specified Pinecone index from environment configuration
        """
        try:
            # Default to the index name provided in the class
            index_name = self.index_name
            # Optionally, allow the user to provide a host, but default to Pinecone’s built-in discovery
            pinecone_host = os.getenv("PINECONE_HOST", None)

            if not pinecone_host:
                self.logger.error("PINECONE_HOST environment variable is not set.")
                return

            # Instantiate the Pinecone index
            index = self.pinecone.Index(
                name=index_name,
                host=pinecone_host
            )
            self.logger.info(f"Loaded Pinecone index: {index_name} successfully.")
            return index
        
        except Exception as e:
            self.logger.error(f"Failed to load index: {e}")
            return None
        
    def query_vector(self, query: str):
        
        index = self.load_index()
        
        time.sleep(10)

        # Create embedding
        try:
            self.logger.info("Attempting to create embedding for query")
            embedding = self.pinecone.inference.embed(
                model="multilingual-e5-large",
                inputs=[query],
                parameters={"input_type": "query"},
            )
        except Exception as e:
            self.logger.error(f"Unable to create embedding for query: {e}")
            return

        # Query
        try:
            self.logger.info("Querying using vector embeddings")
            results = index.query(
                namespace="ns1",
                vector=embedding[0].values,
                top_k=1,
                include_values=False,
                include_metadata=True,
            )
        except Exception as e:
            self.logger.error(f"Unabel to query from pinecone: {e}")
            return
        return results

    def response(self, query: str):
        rag_result = self.query_vector(query=query)
        context = rag_result["matches"][0]["metadata"]["text"]

        prompt = f"""You are an AI assistant that helps people learn about Randolf Uy who is a recent graduate.
            Here is what you know about him:
            {context}
            Now, answer the user's question in a friendly and conversational way.
            User: {query}
            Chatbot:"""

        response = self.open_ai_agent.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"]
