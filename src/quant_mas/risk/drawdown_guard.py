"""Drawdown guard checks."""

from __future__ import annotations

import pandas as pd

from quant_mas.risk.decision import RiskDecision, approved_decision, rejected_decision
from quant_mas.risk.limits import RiskLimits


def check_drawdown(equity_curve: pd.DataFrame, limits: RiskLimits) -> RiskDecision:
    """Reject when realized max drawdown breaches the configured limit."""
    if "equity" not in equity_curve.columns:
        raise ValueError("equity_curve must contain an equity column")
    equity = pd.to_numeric(equity_curve["equity"], errors="raise").dropna()
    if equity.empty:
        raise ValueError("equity_curve is empty")
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    max_drawdown = float(drawdown.min())
    audit = {
        "max_drawdown": max_drawdown,
        "max_drawdown_limit": -limits.max_drawdown,
        "final_equity": float(equity.iloc[-1]),
    }
    if max_drawdown < -limits.max_drawdown:
        return rejected_decision(
            reason="drawdown limit breached",
            violations=["max_drawdown_exceeded"],
            audit=audit,
        )
    return approved_decision(reason="drawdown limit passed", audit=audit)
