from backend.utils.llm import call_llm
from backend.tools.pdf_parser import parse_pdf_from_url

def parse_paper(paper: dict):
    """
    Fetch PDF text and extract structured info
    """
    # Fetch PDF text for deeper analysis
    pdf_text = parse_pdf_from_url(paper["pdf_url"])
    
    # Use only first 4k chars to fit in context window and minimize token usage
    content_to_analyze = pdf_text[:4000] if pdf_text else paper["summary"]
    
    prompt = f"""
    Extract structured research information from the following paper text:
    Title: {paper['title']}
    Content: {content_to_analyze}

    Return precise details on:
    1. Primary Methodologies
    2. Key Datasets
    3. Notable Results
    4. Explicit and Implicit Limitations (Critical)
    5. Key Contributions
    """

    response = call_llm(prompt, model="mixtral-8x7b-32768")
    
    return {
        "title": paper["title"],
        "year": paper.get("year"),
        "parsed": response,
        "metadata": paper
    }
