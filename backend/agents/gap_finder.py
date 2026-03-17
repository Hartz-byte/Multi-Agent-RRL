from backend.utils.llm import call_llm

def find_gaps(analysis):
    prompt = f"""
    Identify research gaps based on:
    {analysis}

    Focus on:
    - missing approaches
    - repeated limitations
    - unexplored areas
    """

    return call_llm(prompt)
