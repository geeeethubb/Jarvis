"""
Jarvis Pipeline Orchestrator
Runs all 7 stages in order, updating job status at each step.
"""

import asyncio
import traceback
from agents import (
    score_idea,
    run_market_research,
    run_business_validation,
    run_deep_dive,
    run_summary,
    run_cofounder_match,
    run_action_plan,
)
from database import check_idea_similarity, save_idea, save_report

# In-memory job status store
_jobs: dict[str, dict] = {}


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def _update_job(job_id: str, **kwargs):
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)


def create_job(job_id: str, idea: str, user_name: str, user_id: str):
    _jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "stage": 0,
        "stage_name": "Queued",
        "progress": 0,
        "idea": idea,
        "user_name": user_name,
        "user_id": user_id,
        "result": None,
        "error": None,
    }


async def run_pipeline(job_id: str):
    """
    Full 7-stage pipeline. Updates job status at each step.
    """
    job = _jobs.get(job_id)
    if not job:
        return

    idea = job["idea"]
    user_name = job["user_name"]
    user_id = job["user_id"]

    try:
        # ── STAGE 1: Idea Scoring ──────────────────────────────────────────
        _update_job(job_id, status="running", stage=1, stage_name="Scoring your idea", progress=5)
        score_result = await score_idea(idea, user_name)

        if score_result["status"] == "FOLLOWUP" and not job.get("bypass_score"):
            _update_job(
                job_id,
                status="followup",
                stage=1,
                stage_name="Idea needs more detail",
                progress=10,
                result={
                    "status": "FOLLOWUP",
                    "score": score_result["score"],
                    "reason": score_result["reason"],
                    "questions": score_result["questions"],
                },
            )
            return

        # ── STAGE 2: Originality Check ─────────────────────────────────────
        _update_job(job_id, stage=2, stage_name="Checking originality", progress=15)
        similarity = check_idea_similarity(idea, user_id)

        if similarity["status"] == "SIMILAR":
            _update_job(
                job_id,
                status="similar",
                stage=2,
                stage_name="Similar idea found",
                progress=20,
                result={
                    "status": "SIMILAR",
                    "similarity_score": similarity["similarity_score"],
                    "matched_idea": similarity["matched_idea"],
                },
            )
            return

        # Save unique idea to vault
        save_idea(idea, user_name, score_result["score"], user_id)

        # ── STAGE 3: Market Research ───────────────────────────────────────
        _update_job(job_id, stage=3, stage_name="Researching the market", progress=25)
        stage1_report = await run_market_research(idea, user_name)

        # ── STAGE 4: Business Validation ──────────────────────────────────
        _update_job(job_id, stage=4, stage_name="Validating the business model", progress=45)
        validation_result = await run_business_validation(stage1_report)

        # ── STAGE 5: Innovation Deep Dive ──────────────────────────────────
        _update_job(job_id, stage=5, stage_name="Running innovation deep dive", progress=60)
        deep_dive = await run_deep_dive(idea, stage1_report, validation_result["stage2"])

        # ── STAGE 6: Summary + Co-Founder (parallel) ─────────────────────
        _update_job(job_id, stage=6, stage_name="Building evaluation summary", progress=75)
        summary, cofounder = await asyncio.gather(
            run_summary(user_name, idea, stage1_report, validation_result["stage2"], deep_dive),
            run_cofounder_match(deep_dive, user_name),
        )

        # ── STAGE 7: Action Plan ───────────────────────────────────────────
        _update_job(job_id, stage=7, stage_name="Creating your action plan", progress=88)
        action_plan = await run_action_plan(idea, summary, validation_result["suggestions"])

        # ── Compile & Save Report ──────────────────────────────────────────
        _update_job(job_id, stage_name="Saving report", progress=95)

        # Extract idea title from stage1
        idea_title = "Untitled"
        for line in stage1_report.split("\n"):
            if line.strip().startswith("Idea:"):
                idea_title = line.replace("Idea:", "").strip()[:100]
                break

        # Extract final score from validation
        final_score = score_result["score"]
        for line in validation_result["validation"].split("\n"):
            if line.strip().startswith("Overall:"):
                try:
                    final_score = int(line.split("/")[0].split()[-1])
                except Exception:
                    pass
                break

        report = {
            "idea_title": idea_title,
            "idea_raw": idea,
            "user_name": user_name,
            "idea_score": score_result["score"],
            "final_score": final_score,
            "stage1": stage1_report,
            "stage2": validation_result["stage2"],
            "bmc": validation_result["bmc"],
            "validation": validation_result["validation"],
            "suggestions": validation_result["suggestions"],
            "deep_dive": deep_dive,
            "summary": summary,
            "cofounder": cofounder,
            "action_plan": action_plan,
            "verdict": validation_result["verdict"],
        }

        report_id = save_report(report, user_id)

        _update_job(
            job_id,
            status="completed",
            stage=7,
            stage_name="Report ready",
            progress=100,
            result={
                "status": "OK",
                "report_id": report_id,
                "idea_title": idea_title,
                "verdict": validation_result["verdict"],
                "final_score": final_score,
                **report,
            },
        )

    except Exception as e:
        _update_job(
            job_id,
            status="error",
            stage_name="Error occurred",
            error=str(e),
            error_detail=traceback.format_exc(),
        )
