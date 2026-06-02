"""
Improvement Agent
Evaluates founder's progress since last report and recommends next prototype type.
Mirrors the Improvement Webhook flow from the n8n reference.
"""

import anthropic
from config import get_client


async def run_improvement_assessment(
    original_report: dict,
    improvements_text: str,
) -> str:
    """
    Compare original evaluation with founder's stated improvements.
    Returns a progress assessment with new score and prototype recommendation.
    """
    client = get_client()

    system = """You are an innovation progress evaluator. You receive an original evaluation report and a founder's list of improvements they have made since the last evaluation.

Your job is to:
1. Assess how much the founder has improved based on the issues raised in the original report
2. Give a new overall score out of 10
3. Show the delta (improvement) vs original score
4. Recommend the best next prototype type for their stage

OUTPUT EXACTLY THIS FORMAT AND STOP:

IMPROVEMENT ASSESSMENT
Idea: [idea title from original report]
Founder: [founder name]

PROGRESS SUMMARY
[2-3 sentences on what the founder has addressed and what still needs work]

SCORE PROGRESSION
Original Score: [X]/10
New Score: [Y]/10
Delta: [+/- Z points] — [IMPROVED / DECLINED / SAME]

ISSUES ADDRESSED
- [issue from original]: [RESOLVED / PARTIALLY RESOLVED / NOT YET ADDRESSED] — [one line why]
- [repeat for each critical/important issue from original report]

REMAINING GAPS
- [gap 1]: [what still needs to be done]
- [gap 2]: [what still needs to be done]

PROTOTYPE RECOMMENDATION
Recommended: [Choose the most appropriate prototype type for this specific idea and stage]

Why this prototype:
[2-3 sentences explaining why this prototype type fits their current stage, what it will prove, and who they should show it to]

Prototype Goal: [one clear sentence — what question this prototype should answer]
Timeline: [realistic timeline to build this prototype]
Who to involve: [specific roles/skills]

NEXT MILESTONE
[One sentence on what the founder should achieve before their next check-in]

STOP."""

    original_text = f"""STAGE 1 REPORT:
{original_report.get('stage1', '')}

STAGE 2 REPORT:
{original_report.get('stage2', '')}

ORIGINAL VERDICT: {original_report.get('verdict', '')}
ORIGINAL SCORE: {original_report.get('final_score', '?')}/10"""

    combined = f"""ORIGINAL REPORT:
{original_text}

FOUNDER IMPROVEMENTS SUBMITTED:
{improvements_text}"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": combined}],
    )

    return msg.content[0].text.strip()
