"""
Stage 1 — Idea Scorer Agent
Scores the idea 1-10 and decides PASS or FOLLOWUP.
"""

import json
import re
import anthropic
from config import get_client


async def score_idea(idea: str, user_name: str = "") -> dict:
    """
    Score an idea 1-10 on clarity, relevance, feasibility, and originality.
    Returns: { score, reason, status, questions }
    """
    client = get_client()

    system_prompt = """You are an idea quality scorer. You receive a founder's idea and score it.

IMPORTANT: If the input contains a section called "This is a refined submission with detailed context:" or "Additional context provided:" — treat the FULL submission as an enriched idea and score it based on ALL the content including the additional context. Do not score just the first sentence. Read everything before scoring.

Score the idea from 1-10 based on:
- Clarity: Is the problem and solution clearly defined?
- Relevance: Does it relate to a real business or technology problem?
- Feasibility: Is it realistically achievable?
- Originality: Does it bring something new?

Output ONLY this JSON and nothing else:
{
  "score": [number 1-10],
  "reason": "[one sentence on why this score]",
  "status": "[PASS or FOLLOWUP]",
  "questions": ["[question 1]", "[question 2]", "[question 3]"]
}

Rules:
- If score >= 5: set status to "PASS" and questions to []
- If score < 5: set status to "FOLLOWUP" and provide exactly 3 specific questions that would help the founder strengthen their idea
- The 3 questions must be specific to the submitted idea — not generic
- A refined submission with detailed Q&A answers should almost always score >= 5
- Output ONLY the JSON object. No preamble. No explanation. No markdown. No code blocks."""

    user_message = f"Founder: {user_name}\nIdea: {idea}"

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()

    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        parsed = json.loads(match.group(0)) if match else {}
    except Exception:
        parsed = {"score": 5, "status": "PASS", "reason": "Could not parse score", "questions": []}

    score = parsed.get("score", 5)
    status = parsed.get("status", "PASS" if score >= 5 else "FOLLOWUP")

    return {
        "score": score,
        "reason": parsed.get("reason", ""),
        "status": status,
        "questions": parsed.get("questions", []),
    }
