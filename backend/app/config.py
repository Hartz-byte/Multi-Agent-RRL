import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
# OpenAlex is primarily free/open and doesn't require an API key for general use.
# You can add an email for the 'polite pool' if needed.
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
