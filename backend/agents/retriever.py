import arxiv
import aiohttp
import asyncio
from backend.app.config import SEMANTIC_SCHOLAR_API_KEY
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

async def fetch_semantic_scholar_papers(query: str, max_results: int = 5):
    """
    Fetch papers with Semantic Scholar via API
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={max_results}&fields=title,abstract,authors,year,url,openAccessPdf"
    headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY} if SEMANTIC_SCHOLAR_API_KEY else {}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    papers = []
                    for item in data.get('data', []):
                        # Construct a similar object to arXiv for consistency
                        pdf_data = item.get('openAccessPdf')
                        pdf_url = pdf_data.get('url') if pdf_data else item.get('url', '')
                        
                        papers.append({
                            "title": item.get('title', ''),
                            "summary": item.get('abstract', '') or '',
                            "pdf_url": pdf_url, 
                            "year": item.get('year', 0),
                            "authors": [a.get('name') for a in item.get('authors', [])],
                            "categories": ["Research"], # default
                            "source": "semantic_scholar"
                        })
                    return papers
                else:
                    print(f"Semantic Scholar Error: {response.status}")
                    return []
    except Exception as e:
        print(f"Error fetching from Semantic Scholar: {e}")
        return []

async def fetch_papers(query: str, max_results: int = 8):
    """
    Fetch papers from multiple sources in parallel.
    Biases towards previously liked papers if found in Pinecone.
    """
    # 1. Self-Improving Bias: Retrieve IDs of highly-rated papers from Pinecone
    loop = asyncio.get_event_loop()
    top_liked_ids = await loop.run_in_executor(None, get_top_rated_results, query)
    # If we have liked results, we could specifically look for them, but for now we'll just note it.
    
    # 2. Parallel Fetching
    arxiv_task = fetch_arxiv_papers(query, max_results=max_results // 2)
    semantic_task = fetch_semantic_scholar_papers(query, max_results=max_results // 2)
    
    results = await asyncio.gather(arxiv_task, semantic_task)
    
    # Combine and de-duplicate (simple title-based)
    combined = results[0] + results[1]
    unique_papers = {}
    
    for p in combined:
        if p["title"].lower().strip() not in unique_papers:
            # Self-Improving check: if this paper was previously liked, mark it high priority
            if p["title"][:50] in top_liked_ids:
                p["priority"] = 10
            else:
                p["priority"] = 0
            unique_papers[p["title"].lower().strip()] = p
            
    # Sort by priority
    sorted_papers = sorted(unique_papers.values(), key=lambda x: x["priority"], reverse=True)
    
    return sorted_papers[:max_results]
