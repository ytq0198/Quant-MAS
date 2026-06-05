from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.artifacts import list_paper_artifacts

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


@router.get("/paper")
def read_paper_artifacts() -> dict[str, Any]:
    """List paper artifacts.

    列出论文产物。
    """
    return list_paper_artifacts()
