from fastapi import FastAPI
from backend.workflows.langgraph_flow import run_pipeline

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/analyze")
async def analyze(topic: str):
    result = await run_pipeline(topic)
    return result
