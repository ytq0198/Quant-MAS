from __future__ import annotations

import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.security.api_keys import Principal
from backend.security.audit import append_audit_event
from backend.security.dependencies import require_role
from backend.security.roles import Role
from backend.services.artifacts import list_paper_artifacts
from backend.services.jobs import submit_job

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


class ExportPaperRequest(BaseModel):
    memory_path: str = ""
    audit_dir: str = ""
    output_dir: str = ""


@router.get("/paper")
def read_paper_artifacts() -> dict[str, Any]:
    """List paper artifacts.

    列出论文产物。
    """
    return list_paper_artifacts()


@router.post("/export")
def export_paper_artifacts_job(
    request: ExportPaperRequest,
    principal: Annotated[Principal, Depends(require_role(Role.RESEARCHER))],
) -> dict[str, Any]:
    """Queue a paper artifact export job.

    提交论文产物导出任务。
    """
    params = {
        key: value
        for key, value in {
            "memory_path": request.memory_path,
            "audit_dir": request.audit_dir,
            "output_dir": request.output_dir,
        }.items()
        if value
    }
    job = submit_job(
        "paper_export",
        params,
        submitted_by=principal.role.value,
        summary="Paper artifact export requested from UI.",
    )
    audit_path = os.getenv("QUANT_MAS_AUDIT_WRITE_PATH")
    if audit_path:
        append_audit_event(
            audit_path,
            {
                "event_type": "artifact.export.requested",
                "job_id": job["job_id"],
                "role": principal.role.value,
                "key_fingerprint": principal.key_fingerprint,
            },
        )
    return {"source": "job_store", "job": job}
