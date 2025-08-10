import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
import logging
logger = logging.getLogger(__name__)
load_dotenv()
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    raise Exception("FATAL ERROR: GOOGLE_API_KEY environment variable not found.")
genai.configure(api_key=GOOGLE_API_KEY)
EMBEDDING_MODEL_NAME = "models/embedding-001"
client = chromadb.PersistentClient(path="./chroma_db")
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
        logger.error(f"An error occurred during Google embedding: {e}", exc_info=True)
        return [[] for _ in texts]
def index_chunks(chunks: list[str], namespace: str):
    collection = client.get_or_create_collection(name=namespace)
    logger.info(f"Indexing {len(chunks)} chunks into collection: '{namespace[:10]}...'")
    embeddings = get_embeddings(chunks)
    if not any(embeddings):
        logger.error("Could not generate any embeddings. Skipping indexing.")
        return
    ids = [str(i) for i in range(len(chunks))]
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=ids
    )
    logger.info("Indexing complete.")
def query_chunks(query: str, namespace: str, top_k: int = 3) -> list:
    try:
        collection = client.get_collection(name=namespace)
    except ValueError:
        logger.warning(f"Query attempted on non-existent collection: '{namespace[:10]}...'. Returning empty list.")
        return []
    logger.info(f"Querying collection '{namespace[:10]}...' for: '{query[:40]}...'")
    query_embedding = get_embeddings([query], task_type="retrieval_query")
    if not query_embedding:
        return []
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results['documents'][0]
def check_if_indexed(namespace: str) -> bool:
    all_collection_names = [c.name for c in client.list_collections()]
    if namespace not in all_collection_names:
        logger.info(f"Collection for namespace '{namespace[:10]}...' not found.")
        return False
    collection = client.get_collection(name=namespace)
    count = collection.count()
    is_indexed = count > 0
    logger.info(f"Collection for '{namespace[:10]}...' found with {count} items. Indexed: {is_indexed}")
    return is_indexed