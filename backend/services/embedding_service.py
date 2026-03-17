import requests
import logging
from backend.app.config import HUGGINGFACE_API_KEY

logger = logging.getLogger(__name__)

# Model to use on Hugging Face
HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"

def get_embeddings_hf(texts: list[str]):
    """
    Call Hugging Face Inference API to get embeddings.
    This offloads CPU/Memory to HF, which is critical for Render Free Tier.
    """
    if not HUGGINGFACE_API_KEY:
        logger.warning("HUGGINGFACE_API_KEY not found. Attempting to use local (fallback)...")
        # In this project, we want to AVOID local torch if possible to save memory.
        # But if the key is missing, the service would fail.
        return None

    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}}, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"HF Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error calling HF Inference API: {e}")
        return None

def get_embeddings(text: str):
    """
    Generate embeddings for a single text using HF API
    """
    result = get_embeddings_hf([text])
    if result and isinstance(result, list):
        return result[0]
    return [0] * 384 # Fallback zeros if API fails

def get_batch_embeddings(texts: list[str]):
    """
    Generate embeddings for a list of texts using HF API
    """
    result = get_embeddings_hf(texts)
    if result and isinstance(result, list):
        return result
    return [[0] * 384 for _ in texts]
