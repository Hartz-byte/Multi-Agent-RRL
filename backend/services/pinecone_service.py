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

def store_feedback(topic: str, result_id: str, rating: int):
    """
    Self-Improving Loop: Store feedback to improve future rankings.
    rating: 1 to 5
    """
    try:
        # feedback namespace for specific learning
        namespace = "user_feedback"
        metadata = {
            "topic": topic,
            "rating": rating,
            "result_id": result_id
        }
        # In a production system, we'd adjust weights or store for fine-tuning.
        # Here, we mark the preference for this result under this topic.
        index.upsert([(f"fb_{topic}_{result_id}", [0]*384, metadata)], namespace=namespace)
        return True
    except Exception as e:
        print(f"Feedback Error: {e}")
        return False

def get_top_rated_results(topic: str):
    """
    Retrieve IDs of highly rated papers for this topic to bias retrieval.
    """
    try:
        namespace = "user_feedback"
        # query for feedback related to this topic
        results = index.query(
            vector=[0]*384, 
            top_k=10, 
            namespace=namespace,
            filter={"topic": {"$eq": topic}, "rating": {"$gte": 4}},
            include_metadata=True
        )
        return [match.metadata['result_id'] for match in results.matches]
    except:
        return []
