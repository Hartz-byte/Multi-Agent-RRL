import os
import sys
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Configure logging to see startup progress in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing Multi-Agent Research AI Backend...")

# Use lazy imports to speed up startup port binding
app = FastAPI()

# Enable CORS for frontend deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(topic: str):
    logger.info(f"Analysis started for topic: {topic}")
    from backend.workflows.langgraph_flow import run_pipeline
    result = await run_pipeline(topic)
    return result

@app.post("/feedback")
async def feedback(topic: str, paper_id: str, rating: int):
    from backend.services.pinecone_service import store_feedback
    success = store_feedback(topic, paper_id, rating)
    return {"status": "success" if success else "failed"}

logger.info("Application instance created. Waiting for uvicorn to bind...")
