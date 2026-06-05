from __future__ import annotations

from typing import Any


def get_risk_summary(risk_id: str) -> dict[str, Any]:
    """Return a risk review fixture for the human review UI.

    返回用于人工审查 UI 的风险审查夹具。
    """
    return {
        "id": risk_id,
        "status": "review_required",
        "live_trading_enabled": False,
        "human_confirmation_required": True,
        "checks": [
            {"name": "Backtest completed", "status": "required"},
            {"name": "Risk limits checked", "status": "required"},
            {"name": "Audit log written", "status": "required"},
            {"name": "Human confirmation", "status": "required"},
        ],
        "required_gates": [
            "backtest",
            "risk check",
            "audit log",
            "human confirmation",
        ],
        "decision": "No candidate can move to live trading from this UI.",
        "中文": "任何候选策略都不能从该 UI 直接进入实盘交易。",
    }
