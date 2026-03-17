from backend.utils.llm import call_llm

async def generate_rrl(parsed: list[dict], gaps: str):
    content = "\n".join([f"Title: {p['title']}\nContent: {p['parsed'][:500]}" for p in parsed])

    prompt = f"""
    As a Senior Academic Researcher, write a comprehensive Literature Review (RRL) 
    based on the following papers and identified research gaps:

    Papers Content:
    {content}

    Gaps to Mention:
    {gaps}

    Ensure proper academic tone and clear thematic organization.
    """

    return await call_llm(prompt)

async def generate_proposal(gaps: str):
    prompt = f"""
    Based on the following research gaps, generate a structured research proposal for a potential PhD thesis or research grant:
    
    Gaps:
    {gaps}
    
    Proposal Structure:
    1. Proposed Title
    2. Problem Statement
    3. Primary Objective
    4. Proposed Methodology
    5. Expected Contributions
    6. Future Impact
    """
    
    return await call_llm(prompt)
