from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.risk import get_risk_summary

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.get("/{risk_id}")
def read_risk(risk_id: str) -> dict[str, Any]:
    """Return risk review summary.

    返回风险审查摘要。
    """
    return get_risk_summary(risk_id)
