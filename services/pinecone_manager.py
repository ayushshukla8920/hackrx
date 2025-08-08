import pinecone
import os
from openai import OpenAI

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = "hackrx-index"
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

def get_embedding(text: str) -> list:
	"""
	Get embedding for text using OpenAI API.
	"""
	client = OpenAI()
	response = client.embeddings.create(input=[text], model="text-embedding-ada-002")
	return response.data[0].embedding

def index_chunks(chunks: list):
	"""
	Index chunks in Pinecone.
	"""
	if INDEX_NAME not in pinecone.list_indexes():
		pinecone.create_index(INDEX_NAME, dimension=1536)
	index = pinecone.Index(INDEX_NAME)
	vectors = []
	for i, chunk in enumerate(chunks):
		embedding = get_embedding(chunk)
		vectors.append((str(i), embedding, {"text": chunk}))
	index.upsert(vectors)

def query_chunks(query: str, top_k: int = 3) -> list:
	"""
	Query Pinecone for relevant chunks.
	"""
	index = pinecone.Index(INDEX_NAME)
	embedding = get_embedding(query)
	results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
	return [match["metadata"]["text"] for match in results["matches"]]
