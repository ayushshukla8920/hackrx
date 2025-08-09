import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
import logging
logger = logging.getLogger(__name__)
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    raise Exception("FATAL ERROR: GOOGLE_API_KEY environment variable not found.")
genai.configure(api_key=GOOGLE_API_KEY)
EMBEDDING_MODEL_NAME = "models/embedding-001"
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="hackrx_local_google_v1")
def get_embeddings(texts: list[str], task_type="retrieval_document") -> list[list[float]]:
    if not texts or not all(isinstance(t, str) and t for t in texts):
        return []
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=texts,
            task_type=task_type
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"An error occurred during Google embedding: {e}")
        return [[] for _ in texts]
def index_chunks(chunks: list[str], namespace: str):
    logger.info(f"[LOCAL DB] Indexing {len(chunks)} chunks using Google embeddings...")
    embeddings = get_embeddings(chunks)
    if not any(embeddings):
        logger.error("[LOCAL DB] ERROR: Could not generate any embeddings. Skipping indexing.")
        return
    ids = [str(i) for i in range(len(chunks))]
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=ids
    )
    logger.info("[LOCAL DB] Indexing complete.")
def query_chunks(query: str, namespace: str, top_k: int = 3) -> list:
    logger.info(f"[LOCAL DB] Querying for: '{query[:40]}...' using Google embeddings.")
    query_embedding = get_embeddings([query], task_type="retrieval_query")
    if not query_embedding:
        return []
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results['documents'][0]
def check_if_indexed(namespace: str) -> bool:
    count = collection.count()
    is_indexed = count > 0
    logger.info(f"[LOCAL DB] Checking if indexed... Found {count} items. Indexed: {is_indexed}")
    return is_indexed