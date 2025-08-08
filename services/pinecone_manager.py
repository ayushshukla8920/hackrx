from pinecone import Pinecone, ServerlessSpec
import os
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL_NAME = "openai/text-embedding-3-small"
AZURE_TOKEN = os.getenv("GITHUB_TOKEN")
azure_client = EmbeddingsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_TOKEN)
)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "hackrx-index"
pc = Pinecone(api_key=PINECONE_API_KEY)
def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    response = azure_client.embed(input=texts, model=AZURE_MODEL_NAME)
    return [item.embedding for item in response.data]
def index_chunks(chunks: list[str], namespace: str):
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
    index = pc.Index(INDEX_NAME)
    embeddings = get_embeddings(chunks)
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append((str(i), embedding, {"text": chunk}))
    index.upsert(vectors=vectors, namespace=namespace)
def query_chunks(query: str, namespace: str, top_k: int = 3) -> list:
    index = pc.Index(INDEX_NAME)
    embedding = get_embeddings([query])[0]
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace=namespace)
    return [match["metadata"]["text"] for match in results.get("matches", [])]
def check_if_indexed(namespace: str) -> bool:
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    return namespace in stats.get('namespaces', {}) and stats['namespaces'][namespace]['vector_count'] > 0