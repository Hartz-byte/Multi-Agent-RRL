from groq import Groq
from backend.app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def call_llm(prompt, model="llama3-70b-8192"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
