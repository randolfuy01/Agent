from pinecone import Pinecone
from dotenv import load_dotenv
import logging
import os
import time


class Chat_Agent:
    """
    Integration agent using vector embeddings and LLM
    """

    def __init__(self, index_name="personal"):

        # Logger for error handling
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.pinecone = None
        self.agent = None
        self.index_name = index_name

    def instantiate_rag(self) -> None:
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

        try:
            api_key = os.getenv("PINECONE_API")
            if not api_key:
                self.logger.error("No api key provided for pinecone")
                return
            self.pinecone = Pinecone(api_key=api_key)
        except Exception as e:
            self.logger.error(
                f"Unable to instantiate pinecone connection using api key: {e}"
            )

    def query_vector(self, query: str, namespace: str):
        try:
            indexes = self.pinecone.list_indexes()
            if self.index_name in indexes:
                self.logger.info(f"Index {self.index_name} found.")
            else:
                self.logger.info(f"Index does not exist")
                return
        except Exception as e:
            self.logger.error(f"Error checking index existence: {e}")

        index = self.pinecone.Index(self.index_name)

        # Create embedding
        try:
            self.logger.info(f"Attempting to create embedding for query")
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
            self.logger.info(f"Querying using vector embeddings")
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
        index = Pinecone.Index(self.index_name)
        return results
