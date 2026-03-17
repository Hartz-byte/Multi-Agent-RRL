import arxiv

async def fetch_papers(query: str, max_results: int = 5):
    """
    Fetch papers with more comprehensive metadata
    """
    search = arxiv.Search(query=query, max_results=max_results)
    
    papers = []
    
    for result in search.results():
        papers.append({
            "title": result.title,
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "year": result.published.year,
            "authors": [a.name for a in result.authors],
            "categories": result.categories
        })

    return papers
