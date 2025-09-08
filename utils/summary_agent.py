import os
import openai
from openai_api import client

#openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-5-nano"

def summarize_article(article_text: str) -> str:
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You summarize news articles in 2 to 4 concise sentences. Return only the summary, no commentary."},
            {"role": "user", "content": article_text}
        ]
    )
    summary = response.choices[0].message.content.strip()
    return summary