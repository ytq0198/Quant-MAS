from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.jobs import get_job_detail, list_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def read_jobs() -> dict[str, Any]:
    """Return job list.

    返回任务列表。
    """
    return list_jobs()


@router.get("/{job_id}")
def read_job_detail(job_id: str) -> dict[str, Any]:
    """Return one job detail.

    返回单个任务详情。
    """
    return get_job_detail(job_id)
