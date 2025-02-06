from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import logging
import pypdf
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_pdf(path_name):
    """Function to parse the pdf and extract all the necessary text

    Args:
        path_name (_type_): File path relative to where script is

    Returns:
        string: Content from the pdf
    """
    try:
        reader = pypdf.PdfReader(path_name)
    except:
        logger.error(f"Source does not exist/ error parsing pdf")
        
    pdf_data = ""
    for i in range(0, len(reader.pages)):
        pdf_data += reader.pages[i].extract_text()
    pdf_data = pdf_data.strip()
    
    pdf_data = pdf_data.replace('\t', ' ')
    pdf_data = ' '.join([line.strip() for line in pdf_data.split('\n')])
    return pdf_data

def main():
    local = load_dotenv()
    if not local:
        logger.info("Unable to load env variables")
        return

    pinecone_api_key = os.getenv("PINECONE_API")
    if not pinecone_api_key:
        logger.info("No Pinecone API Key provided")
        return

    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "personal"

    try:
        pc.delete_index(index_name)
    except Exception as e:
        logger.error(f"Error deleting index {index_name}: {e}")

    index_found = False
    try:
        indexes = pc.list_indexes()
        if index_name in indexes:
            logger.info(f"Index {index_name} already exists.")
            index_found = True
        else:
            logger.info(f"Index '{index_name}' does not exist.")
    except Exception as e:
        logger.error(f"Error checking index existence: {e}")
        return

    # If index does not exist, create it
    if not index_found:
        try:
            pc.create_index(
                name=index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            logger.info(f"Index {index_name} created.")
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            return

    # Prepare data
    sources = ["_internship.pdf", "_personal.pdf", "_resume.pdf"]
    data = []
    counter = 0
    for source in sources:
        try:
            result = parse_pdf(source)
            result = result.strip('\n')
            current_id = f"vec{counter}"
            data.append({"id": current_id, "text": result})
            counter += 1
        except Exception as e:
            logger.error(f"Error parsing source {source}: {e}")
            return
        
    # Generate embeddings
    try:
        embeddings = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[d["text"] for d in data],
            parameters={"input_type": "passage", "truncate": "END"},
        )
        logger.info("Embeddings generated.")
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return

    # Wait until index is ready
    while True:
        index_status = pc.describe_index(index_name)  # Refresh index status
        if index_status.get("status", {}).get("ready", False):
            break
        logger.info("Index is not ready yet")
        time.sleep(2)

    # Insert data into the index
    index = pc.Index(index_name)
    vectors = []
    
    for d, e in zip(data, embeddings):
        vectors.append(
            {
                "id": d["id"],
                "values": e["values"],
                "metadata": {"text": d["text"]},
            }
        )

    print(index.describe_index_stats())
    try:
        response = index.upsert(vectors=vectors, namespace="ns1")
        logger.info(f"Upsert response: {response}")
        time.sleep(15)
    except Exception as e:
        logger.error(f"Error upserting data: {e}")
        return

    # Query the index
    queries = ["Randolf Gabrielle Uy", "What are some hobbies of Gabe", "Internship experience?"]
    for query in queries:
        try:
            embedding = pc.inference.embed(
                model="multilingual-e5-large",
                inputs=[query],
                parameters={"input_type": "query"},
            )
            results = index.query(
                namespace="ns1",  
                vector=embedding[0].values, 
                top_k=1,
                include_values=False,
                include_metadata=True,
            )
            print(results)
        except Exception as e:
            logger.error(f"Error querying the index: {e}")

if __name__ == "__main__":
    main()
