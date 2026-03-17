from backend.utils.llm import call_llm
from backend.tools.pdf_parser import parse_pdf_from_url
import json

def parse_paper(paper: dict):
    """
    Fetch PDF text and extract structured info with explicit entity extraction for the graph.
    """
    pdf_text = parse_pdf_from_url(paper["pdf_url"])
    content_to_analyze = pdf_text[:4000] if pdf_text else paper["summary"]
    
    prompt = f"""
    Extract structured research information from the following paper text.
    You MUST return the output in VALID JSON format.

    Title: {paper['title']}
    Content: {content_to_analyze}

    JSON Structure:
    {{
        "methodologies": ["list of strings"],
        "datasets": ["list of strings"],
        "limitations": ["list of strings"],
        "contributions": ["list of strings"],
        "findings": "summary string"
    }}
    """

    response = call_llm(prompt, model="mixtral-8x7b-32768")
    
    try:
        # Clean response string to ensure it's just JSON
        # In case the LLM adds markdown or chatter
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        parsed_json = json.loads(response[json_start:json_end])
    except:
        # Fallback if JSON parsing fails
        parsed_json = {{
            "methodologies": ["Unknown"],
            "datasets": ["Unknown"],
            "limitations": [response[:200]],
            "contributions": ["Unknown"],
            "findings": response[:500]
        }}
    
    return {
        "title": paper["title"],
        "year": paper.get("year"),
        "parsed": response, # keep original for summary
        "structured_data": parsed_json,
        "metadata": paper
    }
