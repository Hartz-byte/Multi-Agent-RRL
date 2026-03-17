from groq import AsyncGroq
from backend.app.config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)

async def call_llm(prompt, model="llama3-70b-8192"):
    """
    Asynchronous LLM call using Groq
    """
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
