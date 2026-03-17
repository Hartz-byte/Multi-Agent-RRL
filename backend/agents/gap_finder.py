from backend.utils.llm import call_llm

async def find_gaps(analysis: str):
    prompt = f"""
    Identify research gaps based on the following analysis:
    {analysis}

    Focus on:
    - missing approaches
    - repeated limitations
    - unexplored areas
    """

    return await call_llm(prompt)
