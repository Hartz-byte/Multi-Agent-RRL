from pinecone import Pinecone
from backend.app.config import PINECONE_API_KEY, PINECONE_INDEX

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def store_research_data(topic: str, paper_id: str, vector: list, metadata: dict):
    """
    Store paper embedding and metadata in a namespace specific to the research topic.
    """
    try:
        # Use sanitized topic as namespace
        namespace = topic.lower().replace(" ", "_").strip()
        
        index.upsert(
            vectors=[(paper_id, vector, metadata)],
            namespace=namespace
        )
        return True
    except Exception as e:
        print(f"Pinecone Error (Store): {e}")
        return False

def query_research_context(topic: str, vector: list, top_k: int = 5):
    """
    Query existing knowledge base for similar research context.
    """
    try:
        namespace = topic.lower().replace(" ", "_").strip()
        
        results = index.query(
            vector=vector, 
            top_k=top_k, 
            namespace=namespace, 
            include_metadata=True
        )
        return results.matches
    except Exception as e:
        print(f"Pinecone Error (Query): {e}")
        return []
