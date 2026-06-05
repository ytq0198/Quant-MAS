from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.status import get_status_payload

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
def read_status() -> dict[str, Any]:
    """Return current v4 platform status.

    返回当前 v4 平台状态。
    """
    return get_status_payload()
