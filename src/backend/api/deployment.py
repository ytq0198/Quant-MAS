from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.deployment import get_deployment_status

router = APIRouter(prefix="/api/deployment", tags=["deployment"])


@router.get("/status")
def read_deployment_status() -> dict[str, Any]:
    """Return deployment skeleton status.

    返回部署骨架状态。
    """
    return get_deployment_status()
