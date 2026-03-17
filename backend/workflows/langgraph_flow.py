from typing import TypedDict, List, Annotated, Dict
import operator
from langgraph.graph import StateGraph, END
import asyncio

# Import corrected agents and missing functions
from backend.agents.retriever import fetch_papers
from backend.agents.parser import parse_paper
from backend.agents.analyzer import analyze_papers, detect_contradictions, analyze_trends
from backend.agents.gap_finder import find_gaps
from backend.agents.writer import generate_rrl, generate_proposal

# --- Research State Definition ---
class ResearchState(TypedDict):
    """
    Research pipeline state definition
    """
    topic: str
    papers: List[Dict]
    parsed_papers: List[Dict]
    analysis: str
    gaps: str
    trends: str
    contradictions: str
    proposal: str
    rrl: str

# --- Node Implementation ---

async def retrieve_papers_node(state: ResearchState):
    """
    Fetch relevant research papers from databases
    """
    topic = state.get("topic")
    papers = await fetch_papers(topic)
    return {"papers": papers}

def parse_papers_node(state: ResearchState):
    """
    Extract structured data from each paper (Parallel via local parsing)
    """
    papers = state.get("papers")
    parsed_papers = [parse_paper(p) for p in papers]
    return {"parsed_papers": parsed_papers}

def analyze_papers_node(state: ResearchState):
    """
    Synthesize knowledge and uncover patterns
    """
    parsed = state.get("parsed_papers")
    analysis = analyze_papers(parsed)
    return {"analysis": analysis}

def analyze_trends_node(state: ResearchState):
    """
    Identify temporal research trends
    """
    parsed = state.get("parsed_papers")
    trends = analyze_trends(parsed)
    return {"trends": trends}

def detect_contradictions_node(state: ResearchState):
    """
    Search for conflicting opinions or findings
    """
    analysis = state.get("analysis")
    contradictions = detect_contradictions(analysis)
    return {"contradictions": contradictions}

def gap_finder_node(state: ResearchState):
    """
    Detect missing links or repeated limitations
    """
    analysis = state.get("analysis")
    gaps = find_gaps(analysis)
    return {"gaps": gaps}

def generate_outputs_node(state: ResearchState):
    """
    Final synthesis: RRL and Research Proposal
    """
    parsed = state.get("parsed_papers")
    gaps = state.get("gaps")
    
    rrl = generate_rrl(parsed, gaps)
    proposal = generate_proposal(gaps)
    
    return {"rrl": rrl, "proposal": proposal}

# --- Build LangGraph Pipeline ---

def build_research_graph():
    """
    Build the Multi-Agent Research DAG with state management
    """
    workflow = StateGraph(ResearchState)

    # 1. Add Nodes
    workflow.add_node("retriever", retrieve_papers_node)
    workflow.add_node("parser", parse_papers_node)
    workflow.add_node("analyzer", analyze_papers_node)
    workflow.add_node("trends_analyzer", analyze_trends_node)
    workflow.add_node("contradiction_finder", detect_contradictions_node)
    workflow.add_node("gap_finder", gap_finder_node)
    workflow.add_node("writer", generate_outputs_node)

    # 2. Define Edges (Multi-Path Propagation)
    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "parser")
    workflow.add_edge("parser", "analyzer")
    workflow.add_edge("parser", "trends_analyzer")
    
    # Analyze similarities first, then look for contradictions/gaps
    workflow.add_edge("analyzer", "contradiction_finder")
    workflow.add_edge("analyzer", "gap_finder")
    
    # Final production
    workflow.add_edge("gap_finder", "writer")
    workflow.add_edge("trends_analyzer", "writer")
    workflow.add_edge("contradiction_finder", "writer")
    
    workflow.add_edge("writer", END)

    return workflow.compile()

# --- Execution Entry Point ---

async def run_pipeline(topic: str):
    """
    Entry point for the research workflow
    """
    graph = build_research_graph()
    
    # Initialize state
    inputs = {
        "topic": topic,
        "papers": [],
        "parsed_papers": [],
        "analysis": "",
        "gaps": "",
        "trends": "",
        "contradictions": "",
        "proposal": "",
        "rrl": ""
    }
    
    # Use awaitable graph execution
    # For now, simplistic capture of the final state
    result = await graph.ainvoke(inputs)
    return result
