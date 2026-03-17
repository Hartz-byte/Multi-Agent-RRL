from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.workflows.langgraph_flow import run_pipeline
from backend.services.pinecone_service import store_feedback

app = FastAPI()

# Enable CORS for frontend deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/analyze")
async def analyze(topic: str):
    result = await run_pipeline(topic)
    return result

@app.post("/feedback")
async def feedback(topic: str, paper_id: str, rating: int):
    """
    Self-Improving Loop Endpoint: Allows users to rate papers for a specific topic.
    """
    success = store_feedback(topic, paper_id, rating)
    return {"status": "success" if success else "failed"}
