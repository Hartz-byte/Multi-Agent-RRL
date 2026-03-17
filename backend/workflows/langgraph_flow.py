from typing import TypedDict, List, Annotated, Dict
from langgraph.graph import StateGraph, END
import asyncio

# Import corrected agents
from backend.agents.retriever import fetch_papers
from backend.agents.parser import parse_paper
from backend.agents.analyzer import analyze_papers, detect_contradictions, analyze_trends
from backend.agents.gap_finder import find_gaps
from backend.agents.writer import generate_rrl, generate_proposal

# Import services
from backend.services.pinecone_service import store_research_data
from backend.services.embedding_service import get_embeddings
from backend.graph.builder import build_research_graph, graph_to_json

# --- Research State Definition ---
class ResearchState(TypedDict):
    topic: str
    papers: List[Dict]
    parsed_papers: List[Dict]
    analysis: str
    gaps: str
    trends: str
    contradictions: str
    proposal: str
    rrl: str
    graph_data: Dict

# --- Async Node Implementation ---

async def retrieve_papers_node(state: ResearchState):
    topic = state.get("topic")
    papers = await fetch_papers(topic)
    return {"papers": papers}

async def parse_papers_node(state: ResearchState):
    """
    Parallel Paper Parsing & Vector Persistence
    """
    papers = state.get("papers")
    topic = state.get("topic")
    
    if not papers:
        return {"parsed_papers": []}

    tasks = [parse_paper(p) for p in papers]
    parsed_papers = await asyncio.gather(*tasks)
    
    # Persistence
    loop = asyncio.get_event_loop()
    for parsed in parsed_papers:
        embedding = get_embeddings(f"{parsed['title']} : {parsed['parsed'][:1000]}")
        await loop.run_in_executor(None, 
            store_research_data,
            topic,
            parsed['title'][:50],
            embedding,
            {
                "title": parsed['title'],
                "year": parsed.get('year', 0),
                "summary": parsed.get('summary', '')[:500]
            }
        )
        
    return {"parsed_papers": parsed_papers}

async def research_reasoning_node(state: ResearchState):
    """
    Consolidated Reasoning Node (Fixes LangGraph Fan-out Error)
    Runs Analysis, Trends, Contradictions, Gaps, and Graph Construction in true parallel.
    """
    parsed = state.get("parsed_papers")
    if not parsed:
        return {}

    # 1. Start parallel reasoning tasks
    # Relationship: analyzer -> (contradictions, gaps)
    # Others are independent
    
    # We'll run the primary analysis first, then others
    analysis = await analyze_papers(parsed)
    
    # Now run sub-analyses and others in parallel
    trends_task = analyze_trends(parsed)
    contradictions_task = detect_contradictions(analysis)
    gaps_task = find_gaps(analysis)
    
    # Graph build is sync but should be fast
    G = build_research_graph(parsed)
    graph_json = graph_to_json(G)
    
    # Wait for all reasoning to complete
    trends, contradictions, gaps = await asyncio.gather(
        trends_task, 
        contradictions_task, 
        gaps_task
    )
    
    return {
        "analysis": analysis,
        "trends": trends,
        "contradictions": contradictions,
        "gaps": gaps,
        "graph_data": graph_json
    }

async def generate_outputs_node(state: ResearchState):
    parsed = state.get("parsed_papers")
    gaps = state.get("gaps")
    
    if not gaps:
        return {"rrl": "No research gaps identified.", "proposal": "N/A"}

    # Parallel generation
    rrl_task = generate_rrl(parsed, gaps)
    proposal_task = generate_proposal(gaps)
    
    rrl, proposal = await asyncio.gather(rrl_task, proposal_task)
    
    return {"rrl": rrl, "proposal": proposal}

# --- Build Workflow ---

def build_research_graph_pipeline():
    workflow = StateGraph(ResearchState)

    workflow.add_node("retriever", retrieve_papers_node)
    workflow.add_node("parser", parse_papers_node)
    workflow.add_node("reasoner", research_reasoning_node)
    workflow.add_node("writer", generate_outputs_node)

    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "parser")
    workflow.add_edge("parser", "reasoner")
    workflow.add_edge("reasoner", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()

async def run_pipeline(topic: str):
    graph = build_research_graph_pipeline()
    
    inputs = {
        "topic": topic,
        "papers": [],
        "parsed_papers": [],
        "analysis": "",
        "gaps": "",
        "trends": "",
        "contradictions": "",
        "proposal": "",
        "rrl": "",
        "graph_data": {}
    }
    
    result = await graph.ainvoke(inputs)
    return result
