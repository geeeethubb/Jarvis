"""
Stage 7 — Action Plan Agent (NEW — not in original n8n flow)
Generates a 30/60/90-day action plan and prototype recommendation.
"""

import anthropic
from config import get_client


async def run_action_plan(idea: str, summary: str, stage2_report: str) -> str:
    """
    Generate a concrete 30/60/90-day action plan based on the full evaluation.
    """
    client = get_client()

    system = """You are an execution coach. You receive an idea evaluation summary and Stage 2 report.
Your job is to create a concrete, realistic action plan the founder can start today.
Be specific. Use days and weeks. Name actual tools, methods, and deliverables.
Write once and stop. Do not introduce yourself. Do not ask questions.

Output exactly this format:

ACTION PLAN
Idea: [Title]
Founder: [Name]

PROTOTYPE RECOMMENDATION
Type: [Choose the most appropriate: Landing Page MVP / Concierge MVP / Wizard of Oz MVP / Paper Prototype / Clickable Mockup / Working Prototype]
Why: [2 sentences on why this prototype type fits this idea's current stage]
Goal: [One clear sentence — what specific question this prototype must answer]
Build with: [specific tools — e.g. Bubble, Figma, Carrd, Notion, Google Forms, etc.]
Show it to: [exactly who to test it with and how many people]
Timeline: [realistic days to build this]

30-DAY SPRINT — Validate the Idea
Week 1: Foundation
- Day 1-2: [specific action with exact deliverable]
- Day 3-5: [specific action with exact deliverable]
- Day 6-7: [specific action with exact deliverable]

Week 2: Customer Discovery
- Day 8-10: [specific action — who to talk to, what to ask, how many]
- Day 11-14: [specific action with exact deliverable]

Week 3: Build & Test
- Day 15-18: [specific action — what to build, with what tool]
- Day 19-21: [specific action with exact deliverable]

Week 4: Measure & Decide
- Day 22-25: [specific action — what metrics to track]
- Day 26-30: [decision point — what result means go/no-go]

DECISION POINT (Day 30)
If [this metric is achieved] → proceed to 60-day build phase
If [this metric is NOT achieved] → [specific pivot or kill decision]

60-DAY MILESTONE — Build the MVP
[3-4 bullet points on what the MVP should do/prove]
Key deliverable: [what you should have at day 60]
Budget estimate: [rough cost in USD or time]

90-DAY MILESTONE — Get Traction
[3-4 bullet points on first users, revenue, or proof]
Key metric to hit: [specific number or outcome]
Fundraising signal: [what result would make investors take a meeting]

RESOURCES NEEDED
- Tool 1: [name + cost + what for]
- Tool 2: [name + cost + what for]
- Skill/person: [what to hire or outsource + estimated cost]

NEXT ACTION (Start Today)
[One sentence — the single most important thing to do in the next 24 hours]

Stop here. Do not write anything else."""

    combined = f"""Idea: {idea}

EVALUATION SUMMARY:
{summary}

STAGE 2 IMPROVEMENT SUGGESTIONS (reference for the plan):
{stage2_report}"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": combined}],
    )

    return msg.content[0].text.strip()
