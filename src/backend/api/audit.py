from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.audit import list_audit_logs

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs")
def read_audit_logs(limit: int = 50) -> dict[str, Any]:
    """List audit log events.

    列出审计日志事件。
    """
    return list_audit_logs(limit=max(1, min(limit, 500)))
