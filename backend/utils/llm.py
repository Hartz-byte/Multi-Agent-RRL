from groq import AsyncGroq
import httpx
from backend.app.config import GROQ_API_KEY

# Using an explicit httpx client to avoid internal wrapper version conflicts
# and the "proxies" vs "proxy" keyword argument issue across different httpx/groq versions.
client = AsyncGroq(
    api_key=GROQ_API_KEY,
    http_client=httpx.AsyncClient()
)

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
