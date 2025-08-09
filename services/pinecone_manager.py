# import os
# import chromadb
# from dotenv import load_dotenv
# from azure.ai.inference import EmbeddingsClient
# from azure.core.credentials import AzureKeyCredential
# load_dotenv()
# try:
#     GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
# except KeyError:
#     print("Warning: GOOGLE_API_KEY not found, but required by llm_answerer.py")
# try:
#     AZURE_TOKEN = os.environ["GITHUB_TOKEN"]
# except KeyError:
#     raise Exception("FATAL ERROR: GITHUB_TOKEN environment variable not found.")
# AZURE_ENDPOINT = "https://models.github.ai/inference"
# AZURE_MODEL_NAME = "openai/text-embedding-3-small"
# azure_client = EmbeddingsClient(
#     endpoint=AZURE_ENDPOINT,
#     credential=AzureKeyCredential(AZURE_TOKEN)
# )
# client = chromadb.PersistentClient(path="./chroma_db")
# collection = client.get_or_create_collection(name="hackrx_local_index_openai")
# def get_embeddings(texts: list[str]) -> list[list[float]]:
#     if not texts or not all(isinstance(t, str) and t for t in texts):
#         return []
#     try:
#         response = azure_client.embed(input=texts, model=AZURE_MODEL_NAME)
#         return [item.embedding for item in response.data]
#     except Exception as e:
#         print(f"An error occurred during OpenAI embedding: {e}")
#         return [[] for _ in texts]
# def index_chunks(chunks: list[str], namespace: str):
#     embeddings = get_embeddings(chunks)
#     if not any(embeddings):
#         return
#     ids = [str(i) for i in range(len(chunks))]
#     collection.add(
#         embeddings=embeddings,
#         documents=chunks,
#         ids=ids
#     )
#     print("[LOCAL DB] Indexing complete.")
# def query_chunks(query: str, namespace: str, top_k: int = 3) -> list:
#     query_embedding = get_embeddings([query])
#     if not query_embedding or not query_embedding[0]:
#         print("[LOCAL DB] ERROR: Could not generate query embedding.")
#         return []
#     results = collection.query(
#         query_embeddings=query_embedding,
#         n_results=top_k
#     )
#     return results['documents'][0]
# def check_if_indexed(namespace: str) -> bool:
#     count = collection.count()
#     is_indexed = count > 0
#     print(f"[LOCAL DB] Checking if indexed... Found {count} items. Indexed: {is_indexed}")
#     return is_indexed


# /services/your_db_manager_file.py

import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    raise Exception("FATAL ERROR: GOOGLE_API_KEY environment variable not found.")

genai.configure(api_key=GOOGLE_API_KEY)
EMBEDDING_MODEL_NAME = "models/embedding-001"


# --- CHROMA DB SETUP ---
client = chromadb.PersistentClient(path="./chroma_db")
# I've updated the name to avoid any potential conflicts
collection = client.get_or_create_collection(name="hackrx_local_google_v1")


def get_embeddings(texts: list[str], task_type="retrieval_document") -> list[list[float]]:
    """Gets embeddings using Google's fast embedding model."""
    if not texts or not all(isinstance(t, str) and t for t in texts):
        return []
    try:
        # Use the Google client to generate embeddings
        result = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=texts,
            task_type=task_type
        )
        return result['embedding']
    except Exception as e:
        print(f"An error occurred during Google embedding: {e}")
        return [[] for _ in texts]


def index_chunks(chunks: list[str], namespace: str): # 'namespace' is not used by Chroma, but kept for compatibility
    """Indexes chunks into the local ChromaDB collection using Google embeddings."""
    print(f"[LOCAL DB] Indexing {len(chunks)} chunks using Google embeddings...")
    embeddings = get_embeddings(chunks)
    
    if not any(embeddings):
        print("[LOCAL DB] ERROR: Could not generate any embeddings. Skipping indexing.")
        return

    ids = [str(i) for i in range(len(chunks))]

    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=ids
    )
    print("[LOCAL DB] Indexing complete.")


def query_chunks(query: str, namespace: str, top_k: int = 3) -> list: # 'namespace' is not used
    """Queries the local ChromaDB collection using Google embeddings."""
    print(f"[LOCAL DB] Querying for: '{query[:40]}...' using Google embeddings.")
    # Specify 'retrieval_query' for the task type when querying
    query_embedding = get_embeddings([query], task_type="retrieval_query")

    if not query_embedding:
        return []

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results['documents'][0]


def check_if_indexed(namespace: str) -> bool: # 'namespace' is not used
    """Checks if the local ChromaDB collection has items."""
    count = collection.count()
    is_indexed = count > 0
    print(f"[LOCAL DB] Checking if indexed... Found {count} items. Indexed: {is_indexed}")
    return is_indexed