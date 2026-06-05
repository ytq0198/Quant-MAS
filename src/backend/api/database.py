from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.database import get_database_status

router = APIRouter(prefix="/api/database", tags=["database"])


@router.get("/status")
def read_database_status() -> dict[str, Any]:
    """Return optional database backend status.

    返回可选数据库后端状态。
    """
    return get_database_status()
