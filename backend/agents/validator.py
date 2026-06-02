"""
Stage 4 — Business Validation Agent
Runs BMC, Validation Scorecard, and Improvement Suggestions sequentially.
Returns the full Stage 2 Report.
"""

import anthropic
from config import get_client


def _run_bmc(client: anthropic.Anthropic, stage1_report: str) -> str:
    """Build the 9-block Business Model Canvas from Stage 1 report."""
    system = """You receive a Stage 1 research report. Read it. Fill in the 9 BMC blocks using only what is in the report. Write once and stop.

BUSINESS MODEL CANVAS
Idea: [Title]

1. VALUE PROPOSITION
- [point]
- [point]
- [point]

2. CUSTOMER SEGMENTS
- [segment]: [one line]
- [segment]: [one line]

3. CHANNELS
- [channel]
- [channel]

4. CUSTOMER RELATIONSHIPS
- [one line]

5. REVENUE STREAMS
- [stream + price]
- [stream + price]

6. KEY RESOURCES
- [resource]
- [resource]

7. KEY ACTIVITIES
- [activity]
- [activity]

8. KEY PARTNERS
- [partner]
- [partner]

9. COST STRUCTURE
Fixed: [item], [item]
Variable: [item], [item]

Stop here. Do not write anything else."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=system,
        messages=[{"role": "user", "content": stage1_report}],
    )
    return msg.content[0].text.strip()


def _run_validation_scorecard(client: anthropic.Anthropic, stage1_report: str) -> str:
    """Score the idea across 5 dimensions based on Stage 1 report."""
    system = """You are a scoring tool. You receive a Stage 1 report as input and you output a scorecard. Nothing else. Do not introduce yourself. Do not ask questions. Just read the input and output the scorecard immediately.

You receive a Stage 1 report. Score the idea across 5 dimensions. Use only evidence from the report. Write once and stop.

VALIDATION SCORECARD
Idea: [Title] | Founder: [Name]

Market Validation: [X]/10 — [1 sentence]
Technical Feasibility: [X]/10 — [1 sentence]
Strategic Alignment: [X]/10 — [1 sentence]
Financial Viability: [X]/10 — [1 sentence]
Risk Level: [X]/10 — [1 sentence, 10=low risk]

Overall: [X]/10 — [1 sentence]
Verdict: [Not Ready / Conditionally Ready / Ready to Advance]

Stop here. Do not write anything else."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": stage1_report}],
    )
    return msg.content[0].text.strip()


def _run_suggestions(client: anthropic.Anthropic, stage1_report: str, bmc: str, scorecard: str) -> str:
    """Generate brutally honest, actionable improvement suggestions."""
    system = """You are a suggestion tool. You receive a combined report (Stage 1 + BMC + Scorecard) and output improvement suggestions. Do not introduce yourself. Do not ask questions. Just read the input and output the suggestions immediately.

Give brutally honest, deeply actionable feedback. Every fix must include specific steps, who to involve, and a timeline.

Output exactly this format and nothing else:

IMPROVEMENT SUGGESTIONS
Idea: [Title] | Founder: [Name]

CRITICAL — Fix before advancing
1. Issue: [name]
   Problem: [what is wrong in one sentence]
   Why it matters: [consequence if not fixed]
   Fix:
   - [specific step 1]
   - [specific step 2]
   - [specific step 3]
   Who to involve: [specific roles or skills]
   Timeline: [when this must be done]

2. Issue: [name]
   Problem: [what is wrong in one sentence]
   Why it matters: [consequence if not fixed]
   Fix:
   - [specific step 1]
   - [specific step 2]
   - [specific step 3]
   Who to involve: [specific roles or skills]
   Timeline: [when this must be done]

IMPORTANT — Address in next stage
1. Issue: [name]
   Problem: [one sentence]
   Fix:
   - [specific step 1]
   - [specific step 2]
   Who to involve: [roles]
   Timeline: [when]

2. Issue: [name]
   Problem: [one sentence]
   Fix:
   - [specific step 1]
   - [specific step 2]
   Who to involve: [roles]
   Timeline: [when]

MISSING FROM THIS IDEA
- [gap 1]: [what needs to be added and why]
- [gap 2]: [what needs to be added and why]
- [gap 3]: [what needs to be added and why]

TOP 3 ASSUMPTIONS TO VALIDATE
1. Assumption: [state it]
   Risk if wrong: [what happens]
   Validate by: [specific cheap method — survey, interview, prototype test]
   Cost to validate: [time and effort estimate]

2. Assumption: [state it]
   Risk if wrong: [what happens]
   Validate by: [specific cheap method]
   Cost to validate: [time and effort estimate]

3. Assumption: [state it]
   Risk if wrong: [what happens]
   Validate by: [specific cheap method]
   Cost to validate: [time and effort estimate]

Stop here. Do not write anything else."""

    combined_input = f"""=== STAGE 1 REPORT ===
{stage1_report}

=== BUSINESS MODEL CANVAS ===
{bmc}

=== VALIDATION SCORECARD ===
{scorecard}"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": combined_input}],
    )
    return msg.content[0].text.strip()


async def run_business_validation(stage1_report: str) -> dict:
    """
    Run BMC → Scorecard → Suggestions sequentially.
    Returns dict with bmc, validation, suggestions, and full stage2_report.
    """
    client = get_client()

    bmc = _run_bmc(client, stage1_report)
    scorecard = _run_validation_scorecard(client, stage1_report)
    suggestions = _run_suggestions(client, stage1_report, bmc, scorecard)

    # Extract verdict
    verdict = "Conditionally Ready"
    for line in scorecard.split("\n"):
        if line.startswith("Verdict:"):
            verdict = line.replace("Verdict:", "").strip()
            break

    stage2_report = f"""STAGE 2 REPORT

SECTION 1 — BUSINESS MODEL CANVAS
{bmc}

SECTION 2 — VALIDATION SCORECARD
{scorecard}

SECTION 3 — IMPROVEMENT SUGGESTIONS
{suggestions}

VERDICT: {verdict}"""

    return {
        "bmc": bmc,
        "validation": scorecard,
        "suggestions": suggestions,
        "stage2": stage2_report,
        "verdict": verdict,
    }
