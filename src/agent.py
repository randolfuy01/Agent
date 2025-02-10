from pinecone import Pinecone
from dotenv import load_dotenv
import openai
import logging
import os
import time
import datetime
import json

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
        self.conversational_data = []
        
    async def instantiate_api(self) -> None:
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
            index_name = self.index_name
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
        
    async def query_vector(self, query: str):
        """Performing query to retrieve from vector database based on similarity

        Args:
            query (str): The sentence / text to perform vectorized comparison for 

        Returns:
            _type_: Response from pinecone contianing the document context
        """
        index = self.load_index()
        
        time.sleep(10)

        # Create embedding
        try:
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

    async def response(self, query: str) -> str:
        """ Perform end to end RAG application by finding document tied to data and 
            contextualizating with LLM
        Args:
            query (str): The sentence / text to perform vectorized comparison for 

        Returns:
            _type_: Response from LLM based on the query and RAG results
        """
        
        question_time = datetime.datetime.now()
        
        rag_result = await self.query_vector(query=query)
        context = rag_result["matches"][0]["metadata"]["text"]

        prompt = f"""You are an AI assistant that helps people learn about Randolf Uy who is a recent graduate, you are hosted on his website.
            Here is what you know about him:
            {context}.
            This is the history of your conversation:
            {self.conversational_data}
            Now, answer the user's question in a friendly and conversational way, be more relaxed, like talking to an old friend at a company event. Limit the response to something casual, around 1 -2 sentences.
            User: {query}
            Chatbot:"""

        response = self.open_ai_agent.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], stream=False
        )
        
        response_time = datetime.datetime.now()
        
        data_user = {
            "role": "user",
            "timestamp": question_time,
            "query": query,
        }
        
        data_response = {
            "role": "chatbot",
            "timestamp": response_time,
            "query": query
        }
        
        self.conversational_data.append(data_user)
        self.conversational_data.append(data_response)
        return response.choices[0].message.content
    