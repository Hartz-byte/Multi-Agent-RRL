from backend.utils.llm import call_llm

def analyze_papers(parsed_papers: list[dict]):
    """
    Standard analysis of multiple research papers
    """
    combined = "\n".join([f"Title: {p['title']}\nParse: {p['parsed']}" for p in parsed_papers])

    prompt = f"""
    Analyze the following research papers:
    {combined}

    Tasks:
    1. Identify recurring patterns in methodologies.
    2. Highlight shared limitations.
    3. Summarize the collective contributions.
    """

    return call_llm(prompt)

def detect_contradictions(analysis: str):
    """
    Identify conflicting findings or opinions in the analysis
    """
    prompt = f"""
    Review the following research analysis and identify any research contradictions, 
    divergent findings, or conflicting opinions between different studies:
    
    {analysis}
    
    Output a structured list of contradictions.
    """
    return call_llm(prompt)

def analyze_trends(parsed_papers: list[dict]):
    """
    Track methodological or conceptual evolution over time
    """
    # Simple temporal analysis based on years
    sorted_papers = sorted(parsed_papers, key=lambda x: x.get('year', 0))
    time_chain = "\n".join([f"Year {p.get('year')}: {p['title']} - {p['parsed']}" for p in sorted_papers])

    prompt = f"""
    Perform a trend analysis on how research methods and focus areas have evolved over time:
    {time_chain}
    
    Highlight:
    - Shift in popular methods
    - Emergence of new datasets
    - Progressive solutions to old limitations
    """
    
    return call_llm(prompt)
