from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Callable

_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="quant-mas-job")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _new_job_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"job-{stamp}-{uuid.uuid4().hex[:6]}"


def create_job(
    job_type: str,
    params: dict[str, Any],
    *,
    submitted_by: str = "anonymous",
    summary: str = "",
) -> dict[str, Any]:
    """Create a queued job and schedule background execution."""
    job_id = _new_job_id()
    job = {
        "job_id": job_id,
        "type": job_type,
        "status": "queued",
        "progress": 0.0,
        "summary": summary or f"Queued {job_type} job.",
        "params": params,
        "submitted_by": submitted_by,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "started_at": "",
        "completed_at": "",
        "live_trading_enabled": False,
        "result": None,
        "error": "",
        "events": [
            {
                "timestamp": _utc_now(),
                "type": "job.queued",
                "message": f"Job {job_id} queued.",
            }
        ],
    }
    with _lock:
        _jobs[job_id] = job
    _executor.submit(_execute_job, job_id)
    return _public_job(job)


def _append_event(job_id: str, event_type: str, message: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["events"].append(
            {
                "timestamp": _utc_now(),
                "type": event_type,
                "message": message,
            }
        )
        job["updated_at"] = _utc_now()


def _update_job(job_id: str, **fields: Any) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.update(fields)
        job["updated_at"] = _utc_now()


def _execute_job(job_id: str) -> None:
    from backend.services.job_tasks import run_job_task

    _update_job(job_id, status="running", progress=0.05, started_at=_utc_now())
    _append_event(job_id, "job.started", "Job execution started.")

    def progress(value: float, message: str) -> None:
        _update_job(job_id, progress=max(0.0, min(1.0, value)))
        _append_event(job_id, "job.progress", message)

    try:
        result = run_job_task(job_id, progress)
        _update_job(
            job_id,
            status="completed",
            progress=1.0,
            completed_at=_utc_now(),
            result=result,
            summary=result.get("summary", "Job completed."),
            error="",
        )
        _append_event(job_id, "job.completed", "Job completed successfully.")
    except Exception as exc:
        _update_job(
            job_id,
            status="failed",
            progress=1.0,
            completed_at=_utc_now(),
            error=str(exc),
            summary=f"Job failed: {exc}",
        )
        _append_event(job_id, "job.failed", str(exc))


def list_jobs(include_demo_when_empty: bool = True) -> dict[str, Any]:
    """Return jobs newest-first, with optional demo fallback."""
    with _lock:
        jobs = sorted(
            [_public_job(item) for item in _jobs.values()],
            key=lambda item: item["created_at"],
            reverse=True,
        )
    if jobs:
        return {"source": "job_store", "jobs": jobs}
    if include_demo_when_empty:
        return {"source": "fallback_jobs", "jobs": [_demo_job()]}
    return {"source": "job_store", "jobs": []}


def _demo_job() -> dict[str, Any]:
    return {
        "job_id": "job-demo-001",
        "type": "artifact_export",
        "status": "completed",
        "progress": 1.0,
        "summary": "Fallback paper artifact export job.",
        "live_trading_enabled": False,
    }


def get_job_detail(job_id: str) -> dict[str, Any]:
    """Return one job with events."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            return {"source": "job_store", "job": _public_job(job), "events": list(job["events"])}
    from backend.services.job_store import _demo_job

    fallback = _demo_job()
    if job_id == fallback["job_id"]:
        return {
            "source": "fallback_jobs",
            "job": fallback,
            "events": [
                {"type": "job.created", "message": "Fallback job created for UI integration."},
                {"type": "job.completed", "message": "No live trading operation was performed."},
            ],
        }
    return {"source": "job_store", "job": None, "events": [], "message": "Job not found."}


def get_job_record(job_id: str) -> dict[str, Any] | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def _public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": job["job_id"],
        "type": job["type"],
        "status": job["status"],
        "progress": job["progress"],
        "summary": job["summary"],
        "submitted_by": job.get("submitted_by", ""),
        "created_at": job.get("created_at", ""),
        "updated_at": job.get("updated_at", ""),
        "live_trading_enabled": job.get("live_trading_enabled", False),
        "error": job.get("error", ""),
        "result": job.get("result"),
    }
