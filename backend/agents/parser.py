from backend.utils.llm import call_llm
from backend.tools.pdf_parser import parse_pdf_from_url
import json
import asyncio

async def parse_paper(paper: dict):
    """
    Asynchronous paper parsing with PDF support
    """
    # Run URL download/parse in a separate thread if it's synchronous requests-based
    # The pdf_parser currently uses `requests` which is sync.
    loop = asyncio.get_event_loop()
    pdf_text = await loop.run_in_executor(None, parse_pdf_from_url, paper["pdf_url"])
    
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

    response = await call_llm(prompt, model="mixtral-8x7b-32768")
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        parsed_json = json.loads(response[json_start:json_end])
    except:
        parsed_json = {
            "methodologies": ["Unknown"],
            "datasets": ["Unknown"],
            "limitations": [response[:200]],
            "contributions": ["Unknown"],
            "findings": response[:500]
        }
    
    return {
        "title": paper["title"],
        "year": paper.get("year"),
        "parsed": response, 
        "structured_data": parsed_json,
        "metadata": paper
    }
