"""
Configuration — loads environment variables and creates the Anthropic client.
"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Copy .env.example to .env and add your key."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def get_supabase():
    """Returns a Supabase client if credentials are configured, else None."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
]
