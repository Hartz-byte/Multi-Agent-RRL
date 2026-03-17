from pinecone import Pinecone
from backend.app.config import PINECONE_API_KEY, PINECONE_INDEX

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def store_embedding(id, vector):
    index.upsert([(id, vector)])

def query_embedding(vector):
    return index.query(vector=vector, top_k=5)
