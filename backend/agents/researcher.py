"""
Stage 3 — Market Research Agent
Runs three parallel sub-analyses: Market Landscape, Market Sizing, Strategic Fit.
Returns the full Stage 1 Report.
"""

import asyncio
import anthropic
from config import get_client


async def _market_landscape(client: anthropic.Anthropic, idea: str) -> str:
    """Competitor analysis and market landscape."""
    system = """You receive an idea description. Analyse the market and return exactly this format, nothing else:

MARKET RESEARCH
Idea: [Title]

Market Landscape
[2-3 sentences on current state of this market]

Similar Solutions
- [competitor 1]: [one line]
- [competitor 2]: [one line]
- [competitor 3]: [one line]

Idea Strengths
- [strength]
- [strength]

Idea Weaknesses
- [weakness]
- [weakness]

Market Trends
[2 sentences on trends supporting or threatening this idea]

Stop here."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": f"Idea: {idea}"}],
    )
    return msg.content[0].text.strip()


async def _market_sizing(client: anthropic.Anthropic, idea: str) -> str:
    """TAM / SAM / SOM sizing."""
    system = """You receive an idea description. Analyse the market size and return exactly this format, nothing else:

MARKET SIZING
Idea: [Title]

Industry Size
[1 sentence on current global market size]

TAM: [figure in USD] — [one line explanation]
SAM: [figure in USD] — [one line explanation]
SOM: [figure in USD] — [one line explanation]

Value Creation
[1-2 sentences on value this idea creates]

Revenue Model
- [model 1 + indicative price]
- [model 2 + indicative price]

Stop here."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": f"Idea: {idea}"}],
    )
    return msg.content[0].text.strip()


async def _strategic_fit(client: anthropic.Anthropic, idea: str, user_name: str) -> str:
    """Strategic fit and personal alignment assessment."""
    system = """You receive an idea description. Assess the strategic fit for the founder and return exactly this format, nothing else:

STRATEGIC FIT
Idea: [Title]

Market Alignment
[2 sentences on how well this idea fits current market dynamics and timing]

Founder Fit
[1 sentence on what experience or skills would make someone well-suited to execute this]

Capability Gaps
[1 sentence on what skills or resources are typically missing for this type of idea]

Key Risks
- [risk 1]
- [risk 2]

Strategic Fit Score: [X]/10
Justification: [1 sentence]

Recommendation: [1 sentence on whether this idea has strong legs and what would validate it further]

Stop here."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": f"Founder: {user_name}\nIdea: {idea}"}],
    )
    return msg.content[0].text.strip()


async def _structure_idea(client: anthropic.Anthropic, idea: str, user_name: str) -> str:
    """First step: structure the raw idea into a clean format."""
    system = """You receive a founder name and raw idea. Structure it into exactly this format and nothing else:

Idea Title: [short memorable name]
Problem Statement: [what problem and for whom]
Proposed Solution: [what it does and how]
Target Users: [who benefits most]
Industry / Domain: [sector / space]"""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": f"Founder: {user_name}\nIdea: {idea}"}],
    )
    return msg.content[0].text.strip()


async def run_market_research(idea: str, user_name: str = "") -> str:
    """
    Run all three Stage 1 sub-agents in parallel and return the full Stage 1 Report.
    """
    client = get_client()

    # Step 1: Structure the idea
    structured_idea = await asyncio.to_thread(_structure_idea_sync, client, idea, user_name)

    # Step 2: Run the three research tools in parallel
    landscape, sizing, fit = await asyncio.gather(
        asyncio.to_thread(_market_landscape_sync, client, structured_idea),
        asyncio.to_thread(_market_sizing_sync, client, structured_idea),
        asyncio.to_thread(_strategic_fit_sync, client, structured_idea, user_name),
    )

    # Compile Stage 1 Report
    stage1_report = f"""STAGE 1 REPORT
Founder: {user_name}
Idea: {structured_idea.split(chr(10))[0].replace('Idea Title: ', '')}

{landscape}

---

{sizing}

---

{fit}"""

    return stage1_report


# Sync wrappers for asyncio.to_thread
def _structure_idea_sync(client, idea, user_name):
    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_structure_idea(client, idea, user_name))
    loop.close()
    return result

def _market_landscape_sync(client, idea):
    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_market_landscape(client, idea))
    loop.close()
    return result

def _market_sizing_sync(client, idea):
    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_market_sizing(client, idea))
    loop.close()
    return result

def _strategic_fit_sync(client, idea, user_name):
    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_strategic_fit(client, idea, user_name))
    loop.close()
    return result
