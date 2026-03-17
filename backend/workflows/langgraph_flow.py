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
    Parallel Paper Parsing (Async Processing Optimization)
    """
    papers = state.get("papers")
    topic = state.get("topic")
    
    # 1. Parallel Parsing utilizing asyncio.gather
    tasks = [parse_paper(p) for p in papers]
    parsed_papers = await asyncio.gather(*tasks)
    
    # 2. Persistence (Parallelized with Thread Pool to avoid blocking Event Loop)
    loop = asyncio.get_event_loop()
    for parsed in parsed_papers:
        # Generate embedding
        embedding = get_embeddings(f"{parsed['title']} : {parsed['parsed'][:1000]}")
        
        # Store in Pinecone through executor as it's a sync function
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

async def analyze_papers_node(state: ResearchState):
    parsed = state.get("parsed_papers")
    analysis = await analyze_papers(parsed)
    return {"analysis": analysis}

async def analyze_trends_node(state: ResearchState):
    parsed = state.get("parsed_papers")
    trends = await analyze_trends(parsed)
    return {"trends": trends}

async def detect_contradictions_node(state: ResearchState):
    analysis = state.get("analysis")
    contradictions = await detect_contradictions(analysis)
    return {"contradictions": contradictions}

async def gap_finder_node(state: ResearchState):
    analysis = state.get("analysis")
    gaps = await find_gaps(analysis)
    return {"gaps": gaps}

def graph_builder_node(state: ResearchState):
    parsed = state.get("parsed_papers")
    G = build_research_graph(parsed)
    graph_json = graph_to_json(G)
    return {"graph_data": graph_json}

async def generate_outputs_node(state: ResearchState):
    parsed = state.get("parsed_papers")
    gaps = state.get("gaps")
    
    # Run these in parallel too
    rrl_task = generate_rrl(parsed, gaps)
    proposal_task = generate_proposal(gaps)
    
    rrl, proposal = await asyncio.gather(rrl_task, proposal_task)
    
    return {"rrl": rrl, "proposal": proposal}

# --- Build Workflow ---

def build_research_graph_pipeline():
    workflow = StateGraph(ResearchState)

    workflow.add_node("retriever", retrieve_papers_node)
    workflow.add_node("parser", parse_papers_node)
    workflow.add_node("graph_builder", graph_builder_node)
    workflow.add_node("analyzer", analyze_papers_node)
    workflow.add_node("trends_analyzer", analyze_trends_node)
    workflow.add_node("contradiction_finder", detect_contradictions_node)
    workflow.add_node("gap_finder", gap_finder_node)
    workflow.add_node("writer", generate_outputs_node)

    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "parser")
    
    workflow.add_edge("parser", "graph_builder")
    workflow.add_edge("parser", "analyzer")
    workflow.add_edge("parser", "trends_analyzer")
    
    workflow.add_edge("analyzer", "contradiction_finder")
    workflow.add_edge("analyzer", "gap_finder")
    
    workflow.add_edge("gap_finder", "writer")
    workflow.add_edge("trends_analyzer", "writer")
    workflow.add_edge("contradiction_finder", "writer")
    workflow.add_edge("graph_builder", "writer")
    
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
