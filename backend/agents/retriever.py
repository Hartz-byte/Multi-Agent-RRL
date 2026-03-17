import arxiv
import aiohttp
import asyncio
from backend.app.config import OPENALEX_EMAIL
from backend.services.pinecone_service import get_top_rated_results

async def fetch_arxiv_papers(query: str, max_results: int = 5):
    """
    Fetch papers with arXiv, using a thread pool to avoid blocking the loop
    """
    loop = asyncio.get_event_loop()
    
    def fetch():
        search = arxiv.Search(query=query, max_results=max_results)
        return list(search.results())

    results = await loop.run_in_executor(None, fetch)
    
    papers = []
    for result in results:
        papers.append({
            "title": result.title,
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "year": result.published.year,
            "authors": [a.name for a in result.authors],
            "categories": result.categories,
            "source": "arxiv"
        })
    return papers

async def fetch_openalex_papers(query: str, max_results: int = 5):
    """
    Fetch papers from OpenAlex via API
    """
    url = f"https://api.openalex.org/works?search={query}&per_page={max_results}&sort=relevance_score:desc"
    
    # Adding an email for the 'polite pool' improves reliability
    params = {}
    if OPENALEX_EMAIL:
        params["mailto"] = OPENALEX_EMAIL
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    papers = []
                    for item in data.get('results', []):
                        # Construct a similar object to arXiv for consistency
                        
                        # OpenAlex uses inverted index for abstracts, let's try a simple title/display_name if missing
                        # This avoids complex reconstruction for now unless needed
                        summary = item.get('display_name', '') # fallback
                        
                        # If abstract is available in a useful way:
                        # (OpenAlex abstract is usually an inverted index for copyright reasons)
                        # For now we'll use title + snippet or placeholder
                        
                        locations = item.get('primary_location', {}) or {}
                        pdf_url = locations.get('pdf_url') or item.get('doi') or ''
                        
                        authors = [auth.get('author', {}).get('display_name', 'Unknown') 
                                   for auth in item.get('authorships', [])]
                        
                        papers.append({
                            "title": item.get('display_name', ''),
                            "summary": summary, 
                            "pdf_url": pdf_url, 
                            "year": item.get('publication_year', 0),
                            "authors": authors,
                            "categories": [topic.get('display_name') for topic in item.get('topics', [])[:3]],
                            "source": "openalex"
                        })
                    return papers
                else:
                    print(f"OpenAlex Error: {response.status}")
                    return []
    except Exception as e:
        print(f"Error fetching from OpenAlex: {e}")
        return []

async def fetch_papers(query: str, max_results: int = 10):
    """
    Fetch papers from multiple sources (ArXiv & OpenAlex) in parallel.
    Biases towards previously liked papers if found in Pinecone.
    """
    # 1. Self-Improving Bias: Retrieve IDs of highly-rated papers from Pinecone
    loop = asyncio.get_event_loop()
    top_liked_ids = await loop.run_in_executor(None, get_top_rated_results, query)
    
    # 2. Parallel Fetching (5 from ArXiv, 5 from OpenAlex)
    half_results = max_results // 2
    arxiv_task = fetch_arxiv_papers(query, max_results=half_results)
    openalex_task = fetch_openalex_papers(query, max_results=half_results)
    
    results = await asyncio.gather(arxiv_task, openalex_task)
    
    # Combine and de-duplicate (simple title-based)
    combined = results[0] + results[1]
    unique_papers = {}
    
    for p in combined:
        title_key = p["title"].lower().strip()
        if title_key not in unique_papers:
            # Self-Improving check
            if p["title"][:50] in top_liked_ids:
                p["priority"] = 10
            else:
                p["priority"] = 0
            unique_papers[title_key] = p
            
    # Sort by priority
    sorted_papers = sorted(unique_papers.values(), key=lambda x: x["priority"], reverse=True)
    
    return sorted_papers[:max_results]
