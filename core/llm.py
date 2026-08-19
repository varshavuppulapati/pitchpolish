"""Thin wrapper around Groq's OpenAI-compatible API so the rest of the app never touches the SDK directly.

Groq is used instead of OpenAI directly because it has a genuinely free tier
(no card required), which is what makes a public, anyone-can-use deployment of
this app sustainable rather than something that burns a personal API budget.
"""
import os

from openai import OpenAI

_client = None

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
CHAT_MODEL = "openai/gpt-oss-120b"


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys"
            )
        _client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    return _client


def chat(prompt, model=CHAT_MODEL, temperature=0.3):
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
