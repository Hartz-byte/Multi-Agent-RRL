from pinecone import Pinecone, ServerlessSpec
from backend.app.config import PINECONE_API_KEY, PINECONE_INDEX
import time
import logging

logger = logging.getLogger(__name__)

# Singleton index and client holder
_pc_instance = None
_index_instance = None

def get_index():
    """
    Lazy loader for the Pinecone index. 
    Attempts to create the index if it doesn't exist.
    """
    global _index_instance, _pc_instance
    if _index_instance is not None:
        return _index_instance

    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not found in environment variables.")
        return None

    try:
        if _pc_instance is None:
            _pc_instance = Pinecone(api_key=PINECONE_API_KEY)
            
        # Check if index exists
        existing_indexes = [idx.name for idx in _pc_instance.list_indexes()]
        
        if PINECONE_INDEX not in existing_indexes:
            logger.info(f"Index {PINECONE_INDEX} not found. Creating a new Serverless index...")
            _pc_instance.create_index(
                name=PINECONE_INDEX,
                dimension=384, # Matching all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            while not _pc_instance.describe_index(PINECONE_INDEX).status['ready']:
                time.sleep(1)
        
        _index_instance = _pc_instance.Index(PINECONE_INDEX)
        return _index_instance
    except Exception as e:
        logger.warning(f"Could not connect to or create Pinecone Index. Vector features will be disabled. Error: {e}")
        return None

def store_research_data(topic: str, paper_id: str, vector: list, metadata: dict):
    """
    Store paper embedding and metadata in a namespace specific to the research topic.
    """
    index = get_index()
    if index is None: return False
    
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
    index = get_index()
    if index is None: return []
    
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
    """
    index = get_index()
    if index is None: return False
    
    try:
        namespace = "user_feedback"
        metadata = {
            "topic": topic,
            "rating": rating,
            "result_id": result_id
        }
        index.upsert([(f"fb_{topic}_{result_id}", [0]*384, metadata)], namespace=namespace)
        return True
    except Exception as e:
        print(f"Feedback Error: {e}")
        return False

def get_top_rated_results(topic: str):
    """
    Retrieve IDs of highly rated papers for this topic to bias retrieval.
    """
    index = get_index()
    if index is None: return []
    
    try:
        namespace = "user_feedback"
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
