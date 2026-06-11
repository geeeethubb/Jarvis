"""
Database layer — Supabase if configured, local JSON fallback otherwise.
All reports, ideas, and sessions are stored here.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from config import get_supabase

# Local storage path (fallback when Supabase is not configured)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

REPORTS_FILE = DATA_DIR / "reports.json"
IDEAS_FILE = DATA_DIR / "ideas.json"


def _load_json(path: Path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return []
    return []


def _save_json(path: Path, data: list):
    path.write_text(json.dumps(data, indent=2, default=str))


# ─────────────────────── IDEAS ───────────────────────

def get_all_ideas(user_id: str = "default") -> list:
    sb = get_supabase()
    if sb:
        res = sb.table("ideas").select("*").eq("user_id", user_id).execute()
        return res.data or []
    ideas = _load_json(IDEAS_FILE)
    return [i for i in ideas if i.get("user_id") == user_id]


def save_idea(idea_text: str, user_name: str, score: int, user_id: str = "default") -> str:
    idea_id = str(uuid.uuid4())
    record = {
        "id": idea_id,
        "user_id": user_id,
        "user_name": user_name,
        "idea_title": idea_text[:80],
        "idea_description": idea_text,
        "score": score,
        "date_submitted": datetime.now(timezone.utc).isoformat(),
    }
    sb = get_supabase()
    if sb:
        sb.table("ideas").insert(record).execute()
    else:
        ideas = _load_json(IDEAS_FILE)
        ideas.append(record)
        _save_json(IDEAS_FILE, ideas)
    return idea_id


def check_idea_similarity(new_idea: str, user_id: str = "default") -> dict:
    """
    Check new idea against past ideas using Jaccard similarity.
    Returns { status: SIMILAR/UNIQUE, score, matched_idea }
    """
    past_ideas = get_all_ideas(user_id)
    if not past_ideas:
        return {"status": "UNIQUE", "similarity_score": 0, "matched_idea": None}

    STOPWORDS = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "was",
        "had", "our", "out", "who", "get", "how", "its", "use", "will", "with",
        "that", "this", "from", "they", "what", "been", "have", "more", "when",
        "also", "into", "than", "then", "some", "your", "just", "like", "make",
        "many", "most", "over", "such", "take", "time", "very", "well", "were",
        "even", "back", "does", "done", "give", "good", "know", "last", "made",
        "need", "only", "part", "same", "tell", "used", "want", "ways", "work",
        "would", "could", "their", "about", "which", "there", "other", "after",
        "first", "these", "those", "where", "while", "should", "a", "an", "to",
        "is", "it", "in", "of", "on", "at", "be", "by", "or",
    }

    def tokenize(text: str) -> set:
        words = set(text.lower().split())
        return {w for w in words if len(w) > 3 and w not in STOPWORDS}

    new_words = tokenize(new_idea)
    best_score = 0
    best_match = None

    for idea in past_ideas:
        existing = tokenize(idea.get("idea_description", ""))
        if not existing:
            continue
        intersection = len(new_words & existing)
        union = len(new_words | existing)
        score = round((intersection / union) * 100) if union > 0 else 0
        if score > best_score:
            best_score = score
            best_match = idea

    THRESHOLD = 40
    return {
        "status": "SIMILAR" if best_score >= THRESHOLD else "UNIQUE",
        "similarity_score": best_score,
        "matched_idea": best_match,
    }


# ─────────────────────── REPORTS ───────────────────────

def save_report(report: dict, user_id: str = "default") -> str:
    """Save the full report. Returns the report_id."""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    import random
    report_id = "RPT-" + "".join(random.choices(chars, k=6))
    report["report_id"] = report_id
    report["user_id"] = user_id
    report["created_at"] = datetime.now(timezone.utc).isoformat()

    sb = get_supabase()
    if sb:
        sb.table("reports").insert(report).execute()
    else:
        reports = _load_json(REPORTS_FILE)
        reports.append(report)
        _save_json(REPORTS_FILE, reports)

    return report_id


def get_report(report_id: str) -> dict | None:
    sb = get_supabase()
    if sb:
        res = sb.table("reports").select("*").eq("report_id", report_id).execute()
        return res.data[0] if res.data else None
    reports = _load_json(REPORTS_FILE)
    for r in reports:
        if r.get("report_id") == report_id:
            return r
    return None


def get_all_reports(user_id: str = "default") -> list:
    sb = get_supabase()
    if sb:
        res = (
            sb.table("reports")
            .select("report_id,idea_title,verdict,final_score,created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []
    reports = _load_json(REPORTS_FILE)
    user_reports = [r for r in reports if r.get("user_id") == user_id]
    user_reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return [
        {
            "report_id": r.get("report_id"),
            "idea_title": r.get("idea_title", "Untitled"),
            "verdict": r.get("verdict", ""),
            "final_score": r.get("final_score"),
            "created_at": r.get("created_at"),
        }
        for r in user_reports
    ]


def delete_report(report_id: str, user_id: str = "default") -> bool:
    """Delete a report from the vault. Returns True if a report was deleted."""
    sb = get_supabase()
    if sb:
        res = (
            sb.table("reports")
            .delete()
            .eq("report_id", report_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(res.data)
    reports = _load_json(REPORTS_FILE)
    remaining = [
        r for r in reports
        if not (r.get("report_id") == report_id and r.get("user_id") == user_id)
    ]
    if len(remaining) == len(reports):
        return False
    _save_json(REPORTS_FILE, remaining)
    return True


def save_improvement(report_id: str, user_id: str, improvements: str, assessment: str):
    record = {
        "id": str(uuid.uuid4()),
        "report_id": report_id,
        "user_id": user_id,
        "improvements": improvements,
        "assessment": assessment,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    sb = get_supabase()
    if sb:
        sb.table("improvements").insert(record).execute()
    else:
        imp_file = DATA_DIR / "improvements.json"
        items = _load_json(imp_file)
        items.append(record)
        _save_json(imp_file, items)
