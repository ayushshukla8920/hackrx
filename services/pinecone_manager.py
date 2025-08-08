from pinecone import Pinecone, ServerlessSpec
import os
from openai import OpenAI
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
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = "hackrx-index"
pc = Pinecone(api_key=PINECONE_API_KEY)

# def get_embedding(text: str) -> list:
#     """
#     Get embedding for text using OpenAI API.
#     """
#     client = OpenAI()
#     response = client.embeddings.create(input=[text], model="text-embedding-ada-002")
#     print("embedding created")
#     return response.data[0].embedding

def get_embedding(text: str) -> list:
    response = azure_client.embed(input=[text], model=AZURE_MODEL_NAME)
    return response.data[0].embedding

def index_chunks(chunks: list):
	"""
	Index chunks in Pinecone.
	"""
	# Create index if not exists
	if INDEX_NAME not in pc.list_indexes().names():
		pc.create_index(
			name=INDEX_NAME,
			dimension=1536,
			metric='cosine',
			spec=ServerlessSpec(
				cloud='aws',  # or 'gcp' if using Google Cloud
				region='us-east-1'
			)
		)
	index = pc.Index(INDEX_NAME)
	vectors = []
	for i, chunk in enumerate(chunks):
		embedding = get_embedding(chunk)
		vectors.append((str(i), embedding, {"text": chunk}))
	index.upsert(vectors)

def query_chunks(query: str, top_k: int = 3) -> list:
	"""
	Query Pinecone for relevant chunks.
	"""
	index = pc.Index(INDEX_NAME)
	embedding = get_embedding(query)
	results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
	return [match["metadata"]["text"] for match in results["matches"]]
