from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.backtests import get_backtest_summary

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


@router.get("/{backtest_id}")
def read_backtest(backtest_id: str) -> dict[str, Any]:
    """Return a research-only backtest summary.

    返回仅用于研究展示的回测摘要。
    """
    return get_backtest_summary(backtest_id)
