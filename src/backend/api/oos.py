from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.oos import get_oos_summary

router = APIRouter(prefix="/api/oos", tags=["oos"])


@router.get("/{experiment_id}")
def read_oos(experiment_id: str) -> dict[str, Any]:
    """Return walk-forward OOS summary.

    返回 Walk-forward 样本外摘要。
    """
    return get_oos_summary(experiment_id)
