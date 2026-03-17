from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Lazy loader for the model
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        _model_instance = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully.")
    return _model_instance

def get_embeddings(text: str):
    """
    Generate embeddings for text using local model
    """
    model = get_model()
    return model.encode(text).tolist()

def get_batch_embeddings(texts: list[str]):
    """
    Generate embeddings for a list of texts
    """
    model = get_model()
    return model.encode(texts).tolist()
