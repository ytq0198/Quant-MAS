from __future__ import annotations

from typing import Any

from backend.services.job_store import create_job, get_job_detail, list_jobs


def submit_job(
    job_type: str,
    params: dict[str, Any] | None = None,
    *,
    submitted_by: str = "anonymous",
    summary: str = "",
) -> dict[str, Any]:
    """Queue a research job."""
    allowed = {"backtest", "walk_forward_oos", "paper_export"}
    if job_type not in allowed:
        raise ValueError(f"Unsupported job type: {job_type}")
    return create_job(
        job_type,
        params or {},
        submitted_by=submitted_by,
        summary=summary or f"Submitted {job_type} job.",
    )


def list_jobs_payload() -> dict[str, Any]:
    return list_jobs(include_demo_when_empty=True)


def get_job_detail_payload(job_id: str) -> dict[str, Any]:
    return get_job_detail(job_id)
