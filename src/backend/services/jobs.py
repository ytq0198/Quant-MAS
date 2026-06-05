from __future__ import annotations

from typing import Any


def list_jobs() -> dict[str, Any]:
    """Return fallback job list.

    返回回退任务列表。
    """
    return {"source": "fallback_jobs", "jobs": [_fallback_job()]}


def get_job_detail(job_id: str) -> dict[str, Any]:
    """Return one fallback job with events.

    返回带事件的单个回退任务。
    """
    job = _fallback_job()
    if job_id != job["job_id"]:
        return {"source": "fallback_jobs", "job": None, "events": [], "message": "Job not found."}
    return {
        "source": "fallback_jobs",
        "job": job,
        "events": [
            {"type": "job.created", "message": "Fallback job created for UI integration."},
            {"type": "job.completed", "message": "No live trading operation was performed."},
        ],
    }


def _fallback_job() -> dict[str, Any]:
    return {
        "job_id": "job-demo-001",
        "type": "artifact_export",
        "status": "completed",
        "progress": 1.0,
        "summary": "Fallback paper artifact export job.",
        "live_trading_enabled": False,
    }
