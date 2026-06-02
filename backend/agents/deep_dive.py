"""
Stage 5 — Innovation Deep Dive Agent (NEW — not in original n8n flow)
Applies innovation frameworks, gap analysis, and risk assessment.
"""

import anthropic
from config import get_client


async def run_deep_dive(idea: str, stage1_report: str, stage2_report: str) -> str:
    """
    Run an innovation deep dive using frameworks like JTBD, Blue Ocean, and Design Thinking.
    Returns a structured deep dive report.
    """
    client = get_client()

    system = """You are an innovation coach. You receive an idea, Stage 1 market research, and Stage 2 validation.
Your job is to apply innovation frameworks, identify gaps, and assess risks.
Be specific, direct, and actionable. Use evidence from the reports provided.
Write once and stop. Do not introduce yourself. Do not ask questions.

Output exactly this format:

INNOVATION DEEP DIVE
Idea: [Title]

JOBS TO BE DONE (JTBD)
Functional Job: [What task is the customer actually trying to accomplish?]
Emotional Job: [How does the customer want to feel while doing it?]
Social Job: [How does the customer want to be perceived by others?]
Key Insight: [One sentence on what this reveals about the real opportunity]

BLUE OCEAN ANALYSIS
Eliminate: [What does every competitor do that you could eliminate entirely?]
Reduce: [What could you reduce well below industry standard?]
Raise: [What should you raise well above industry standard?]
Create: [What should you create that the industry has never offered?]
Blue Ocean Opportunity: [1-2 sentences on the whitespace this creates]

SKILL & RESOURCE GAP ANALYSIS
Gap 1 — [Category: Technical / Business / Domain / Network]
  Missing: [specific skill or resource]
  Impact: [what this prevents]
  How to fill: [specific way to acquire this — hire, partner, learn, outsource]

Gap 2 — [Category]
  Missing: [specific skill or resource]
  Impact: [what this prevents]
  How to fill: [specific way to acquire this]

Gap 3 — [Category]
  Missing: [specific skill or resource]
  Impact: [what this prevents]
  How to fill: [specific way to acquire this]

Gap 4 — [Category]
  Missing: [specific skill or resource]
  Impact: [what this prevents]
  How to fill: [specific way to acquire this]

RISK ASSESSMENT
Risk 1: [name]
  Type: [Market / Technical / Execution / Financial / Regulatory]
  Likelihood: [Low / Medium / High]
  Impact: [Low / Medium / High]
  Description: [one sentence on what this risk is]
  Mitigation: [specific steps to reduce this risk]

Risk 2: [name]
  Type: [type]
  Likelihood: [Low / Medium / High]
  Impact: [Low / Medium / High]
  Description: [one sentence]
  Mitigation: [specific steps]

Risk 3: [name]
  Type: [type]
  Likelihood: [Low / Medium / High]
  Impact: [Low / Medium / High]
  Description: [one sentence]
  Mitigation: [specific steps]

INNOVATION SCORE
Framework Alignment: [X]/10 — [one sentence]
Disruption Potential: [X]/10 — [one sentence]
Execution Complexity: [X]/10 — [one sentence, 10=very complex]

Overall Innovation Rating: [X]/10
Summary: [2-3 sentences on what makes this idea genuinely innovative and what would make it more so]

Stop here. Do not write anything else."""

    combined = f"""IDEA:
{idea}

STAGE 1 REPORT (Market Research):
{stage1_report}

STAGE 2 REPORT (Business Validation):
{stage2_report}"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": combined}],
    )

    return msg.content[0].text.strip()
