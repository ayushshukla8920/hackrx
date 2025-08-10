import os
import logging
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()
client = chromadb.PersistentClient(path="./chroma_db")
logger.info("Loading embedding model all-MiniLM-L6-v2...")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts or not all(isinstance(t, str) and t.strip() for t in texts):
        return []
    try:
        embeddings = embedding_model.encode(texts, convert_to_numpy=True).tolist()
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        return [[] for _ in texts]
def index_chunks(chunks: list[str], namespace: str):
    collection = client.get_or_create_collection(name=namespace)
    logger.info(f"Indexing {len(chunks)} chunks into collection: '{namespace[:10]}...'")
    embeddings = get_embeddings(chunks)
    if not any(embeddings):
        logger.error("No embeddings generated. Skipping indexing.")
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
        logger.warning(f"Collection '{namespace[:10]}...' not found. Returning empty list.")
        return []
    logger.info(f"Querying '{namespace[:10]}...' for: '{query[:40]}...'")
    query_embedding = get_embeddings([query])
    if not any(query_embedding):
        return []
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results.get('documents', [[]])[0]
def check_if_indexed(namespace: str) -> bool:
    all_collections = [c.name for c in client.list_collections()]
    if namespace not in all_collections:
        logger.info(f"Collection '{namespace[:10]}...' not found.")
        return False
    collection = client.get_collection(name=namespace)
    count = collection.count()
    is_indexed = count > 0
    logger.info(f"Collection '{namespace[:10]}...' contains {count} items. Indexed: {is_indexed}")
    return is_indexed