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

# Import services & tools
from backend.services.pinecone_service import store_research_data
from backend.services.embedding_service import get_embeddings
from backend.graph.builder import build_research_graph, graph_to_json

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
    graph_data: Dict  # New field for relational visualization

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
    topic = state.get("topic")
    parsed_papers = []

    for p in papers:
        parsed = parse_paper(p)
        
        # --- Persistence (Vector Database) ---
        # Generate embedding for the paper summary/content
        embedding = get_embeddings(f"{parsed['title']} : {parsed['parsed']}")
        
        # Store metadata in Pinecone under the topic namespace
        store_research_data(
            topic=topic,
            paper_id=p['title'][:50], # using title as identifier for simplicity
            vector=embedding,
            metadata={
                "title": p['title'],
                "year": p.get('year', 0),
                "summary": p.get('summary', '')[:500]
            }
        )
        
        parsed_papers.append(parsed)
        
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

def graph_builder_node(state: ResearchState):
    """
    Construct the Relational Knowledge Graph for visualization
    """
    parsed = state.get("parsed_papers")
    G = build_research_graph(parsed)
    graph_json = graph_to_json(G)
    return {"graph_data": graph_json}

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

def build_research_graph_pipeline():
    """
    Build the Multi-Agent Research DAG with state management and graph visualization
    """
    workflow = StateGraph(ResearchState)

    # 1. Add Nodes
    workflow.add_node("retriever", retrieve_papers_node)
    workflow.add_node("parser", parse_papers_node)
    workflow.add_node("graph_builder", graph_builder_node) # Map relations
    workflow.add_node("analyzer", analyze_papers_node)
    workflow.add_node("trends_analyzer", analyze_trends_node)
    workflow.add_node("contradiction_finder", detect_contradictions_node)
    workflow.add_node("gap_finder", gap_finder_node)
    workflow.add_node("writer", generate_outputs_node)

    # 2. Define Edges (Multi-Path Propagation)
    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "parser")
    
    # Branch out for parallel analysis and graph building
    workflow.add_edge("parser", "graph_builder")
    workflow.add_edge("parser", "analyzer")
    workflow.add_edge("parser", "trends_analyzer")
    
    # Analyze similarities first, then look for contradictions/gaps
    workflow.add_edge("analyzer", "contradiction_finder")
    workflow.add_edge("analyzer", "gap_finder")
    
    # Final production paths
    workflow.add_edge("gap_finder", "writer")
    workflow.add_edge("trends_analyzer", "writer")
    workflow.add_edge("contradiction_finder", "writer")
    workflow.add_edge("graph_builder", "writer")
    
    workflow.add_edge("writer", END)

    return workflow.compile()

# --- Execution Entry Point ---

async def run_pipeline(topic: str):
    """
    Entry point for the research workflow
    """
    graph = build_research_graph_pipeline()
    
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
        "rrl": "",
        "graph_data": {}
    }
    
    result = await graph.ainvoke(inputs)
    return result
