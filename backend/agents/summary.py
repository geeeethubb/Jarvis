"""
Stage 6a — Summary Agent
Reads all previous stage outputs and compiles one cohesive evaluation summary.
"""

import anthropic
from config import get_client


async def run_summary(
    user_name: str,
    idea: str,
    stage1_report: str,
    stage2_report: str,
    deep_dive: str,
) -> str:
    """
    Compile a concise evaluation summary from all stage reports.
    """
    client = get_client()

    system = """You are a summary tool. You receive multiple reports and output ONE single evaluation summary.
Do not introduce yourself. Do not ask questions. Output the summary immediately and stop.

Output exactly this format:

EVALUATION SUMMARY
Founder: [Name]
Idea: [extract idea title]

ONE LINE SUMMARY
[One sentence describing the idea and its core value]

KEY FINDINGS
- Market: [one line on market opportunity and size]
- Validation: [overall score X/10 and verdict]
- Strategic Fit: [score and one line]
- Financial Viability: [score and one line]

SKILL GAPS IDENTIFIED
- Gap 1: [specific skill or capability missing]
- Gap 2: [specific skill or capability missing]
- Gap 3: [specific skill or capability missing]
- Gap 4: [specific skill or capability missing]

CRITICAL ISSUES
1. [most critical issue in one line]
2. [second critical issue in one line]

INNOVATION HIGHLIGHTS
- [what makes this idea genuinely novel]
- [biggest risk to watch]

VERDICT: [copy exact verdict from the validation report]

Stop here. Do not output anything else."""

    combined = f"""Founder: {user_name}
Idea: {idea}

--- STAGE 1 REPORT ---
{stage1_report}

--- STAGE 2 REPORT ---
{stage2_report}

--- INNOVATION DEEP DIVE ---
{deep_dive}"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": combined}],
    )

    return msg.content[0].text.strip()
