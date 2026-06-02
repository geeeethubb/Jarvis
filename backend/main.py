"""
JARVIS — FastAPI Backend
The main entry point. All API routes are defined here.
"""

import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import CORS_ORIGINS
from pipeline import run_pipeline, get_job, create_job
from database import get_all_reports, get_report, save_improvement
from agents.improvement import run_improvement_assessment

app = FastAPI(
    title="Jarvis API",
    description="Your personal AI innovation companion",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"],  # '*' allows the local HTML file to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────── REQUEST MODELS ───────────────────────

class SubmitIdeaRequest(BaseModel):
    idea: str
    user_name: str = "Founder"
    user_id: str = "default"


class RefinedIdeaRequest(BaseModel):
    original_idea: str
    answers: list[str]
    questions: list[str]
    user_name: str = "Founder"
    user_id: str = "default"


class ImprovementRequest(BaseModel):
    report_id: str
    improvements: str
    user_id: str = "default"


class ProceedSimilarRequest(BaseModel):
    idea: str
    user_name: str = "Founder"
    user_id: str = "default"


# ─────────────────────── ROUTES ───────────────────────

@app.get("/")
def root():
    return {"status": "Jarvis is online", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/submit")
async def submit_idea(req: SubmitIdeaRequest, background_tasks: BackgroundTasks):
    """
    Submit a raw idea. Returns a job_id immediately.
    Poll /api/status/{job_id} to track progress.
    """
    job_id = str(uuid.uuid4())
    create_job(job_id, req.idea.strip(), req.user_name, req.user_id)
    background_tasks.add_task(_run_pipeline_wrapper, job_id)
    return {"status": "queued", "job_id": job_id}


@app.post("/api/submit/refined")
async def submit_refined(req: RefinedIdeaRequest, background_tasks: BackgroundTasks):
    """
    Submit a refined idea after answering follow-up questions.
    """
    # Combine the original idea with the Q&A answers into an enriched submission
    qa_text = "\n".join(
        f"Q: {q}\nA: {a}"
        for q, a in zip(req.questions, req.answers)
    )
    enriched_idea = (
        f"REFINED_SUBMISSION:\n"
        f"Original idea: {req.original_idea}\n\n"
        f"Additional context provided:\n{qa_text}"
    )

    job_id = str(uuid.uuid4())
    create_job(job_id, enriched_idea, req.user_name, req.user_id)
    background_tasks.add_task(_run_pipeline_wrapper, job_id)
    return {"status": "queued", "job_id": job_id}


@app.post("/api/submit/proceed")
async def proceed_despite_similarity(req: ProceedSimilarRequest, background_tasks: BackgroundTasks):
    """
    User acknowledged the similarity warning and wants to proceed anyway.
    Skips the similarity check and goes straight to research.
    """
    from pipeline import _jobs
    job_id = str(uuid.uuid4())
    create_job(job_id, req.idea, req.user_name, req.user_id)
    # Mark as bypass similarity so pipeline skips stage 2
    _jobs[job_id]["bypass_similarity"] = True
    background_tasks.add_task(_run_pipeline_wrapper, job_id)
    return {"status": "queued", "job_id": job_id}


@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    """
    Poll this endpoint to check pipeline progress.
    Returns stage name, progress %, and result when done.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job_id,
        "status": job["status"],
        "stage": job.get("stage", 0),
        "stage_name": job.get("stage_name", ""),
        "progress": job.get("progress", 0),
    }

    if job["status"] in ("completed", "followup", "similar", "error"):
        response["result"] = job.get("result")
        response["error"] = job.get("error")

    return response


@app.get("/api/reports")
def list_reports(user_id: str = "default"):
    """List all past reports for a user (for the idea vault)."""
    return {"reports": get_all_reports(user_id)}


@app.get("/api/reports/{report_id}")
def fetch_report(report_id: str):
    """Fetch a specific report by ID."""
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.post("/api/improve")
async def improve_idea(req: ImprovementRequest):
    """
    Submit improvements since last report.
    Jarvis evaluates progress and recommends the next prototype type.
    """
    report = get_report(req.report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Original report not found")

    assessment = await run_improvement_assessment(report, req.improvements)

    save_improvement(req.report_id, req.user_id, req.improvements, assessment)

    return {
        "status": "OK",
        "report_id": req.report_id,
        "assessment": assessment,
    }


# ─────────────────────── HELPERS ───────────────────────

async def _run_pipeline_wrapper(job_id: str):
    """Wrapper to handle top-level exceptions in background tasks."""
    try:
        await run_pipeline(job_id)
    except Exception as e:
        from pipeline import _jobs
        if job_id in _jobs:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
