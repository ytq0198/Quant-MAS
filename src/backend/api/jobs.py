from __future__ import annotations

import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.security.api_keys import Principal
from backend.security.audit import append_audit_event
from backend.security.dependencies import require_role
from backend.security.roles import Role
from backend.services.jobs import get_job_detail_payload, list_jobs_payload, submit_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

ALLOWED_JOB_TYPES = {"backtest", "walk_forward_oos", "paper_export"}


class CreateJobRequest(BaseModel):
    type: str = Field(..., description="Job type: backtest, walk_forward_oos, paper_export")
    params: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


@router.get("")
def read_jobs() -> dict[str, Any]:
    """Return job list.

    返回任务列表。
    """
    return list_jobs_payload()


@router.post("")
def create_job(
    request: CreateJobRequest,
    principal: Annotated[Principal, Depends(require_role(Role.RESEARCHER))],
) -> dict[str, Any]:
    """Submit a research job (backtest, OOS, paper export).

    提交研究任务（回测、OOS、论文导出）。
    """
    if request.type not in ALLOWED_JOB_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported job type: {request.type}")
    try:
        job = submit_job(
            request.type,
            request.params,
            submitted_by=principal.role.value,
            summary=request.summary,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    audit_path = os.getenv("QUANT_MAS_AUDIT_WRITE_PATH")
    if audit_path:
        append_audit_event(
            audit_path,
            {
                "event_type": "job.submitted",
                "job_id": job["job_id"],
                "job_type": request.type,
                "role": principal.role.value,
                "key_fingerprint": principal.key_fingerprint,
            },
        )
    return {"source": "job_store", "job": job}


@router.get("/{job_id}")
def read_job_detail(job_id: str) -> dict[str, Any]:
    """Return one job detail.

    返回单个任务详情。
    """
    return get_job_detail_payload(job_id)


@router.get("/{job_id}/events")
def read_job_events(job_id: str) -> dict[str, Any]:
    """Return job event stream.

    返回任务事件流。
    """
    payload = get_job_detail_payload(job_id)
    return {
        "source": payload.get("source"),
        "job_id": job_id,
        "events": payload.get("events", []),
    }
