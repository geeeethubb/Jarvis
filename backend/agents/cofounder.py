"""
Stage 6b — Co-Founder / Team Match Agent
Identifies the ideal co-founder profiles based on skill gaps from the evaluation summary.
"""

import anthropic
from config import get_client


async def run_cofounder_match(summary: str, user_name: str = "") -> str:
    """
    Based on the evaluation summary and skill gaps, recommend co-founder profiles.
    For a personal tool this recommends ideal profile types rather than specific people.
    """
    client = get_client()

    system = """You are a team-building advisor. You receive an evaluation summary that includes skill gaps.
Your job is to define the 2 ideal co-founder profiles that would most complement the founder.

Do not ask questions. Do not wait. Process immediately.

Output exactly this format and stop:

CO-FOUNDER ANALYSIS
Founder: [Name]
Idea: [Title]

SKILL GAPS TO FILL
[list the gaps from the summary]

CO-FOUNDER PROFILE 1
Role Title: [e.g. CTO, Head of Growth, Domain Expert]
Fit Score: [X]/10
Why this profile fits: [2 sentences on how their skills fill the gaps]
Key skills needed: [list 3-4 specific skills]
Gaps they fill: [which specific gaps from the list]
Where to find them: [specific communities, platforms, or networks — e.g. YC alumni, specific Slack groups, LinkedIn search terms]
Red flags to screen for: [one line on what to avoid in this role]

CO-FOUNDER PROFILE 2
Role Title: [role]
Fit Score: [X]/10
Why this profile fits: [2 sentences]
Key skills needed: [list 3-4 specific skills]
Gaps they fill: [which specific gaps]
Where to find them: [specific communities, platforms, or networks]
Red flags to screen for: [one line]

TEAM COMPOSITION RECOMMENDATION
[One paragraph: what the ideal founding team looks like with these two profiles added, what combined strengths you'd have, and what you'd still need to address as you grow. Be direct and specific.]

FIRST HIRE (if co-founder not available immediately)
Role: [what to hire first]
Why: [one sentence]
Where to find: [specific platform or community]

Stop here. Do not ask any questions. Do not add anything else."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=system,
        messages=[{"role": "user", "content": f"Founder: {user_name}\n\n{summary}"}],
    )

    return msg.content[0].text.strip()
