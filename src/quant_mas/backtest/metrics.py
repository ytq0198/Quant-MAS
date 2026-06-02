"""Backtest performance metrics."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def total_return(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    return float(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0)


def annualized_return(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    if len(equity_curve) < 2:
        return 0.0
    cumulative = equity_curve.iloc[-1] / equity_curve.iloc[0]
    years = len(equity_curve) / periods_per_year
    return float(cumulative ** (1.0 / years) - 1.0)


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    clean_returns = returns.dropna()
    if clean_returns.empty or clean_returns.std(ddof=0) == 0:
        return 0.0
    return float(clean_returns.mean() / clean_returns.std(ddof=0) * math.sqrt(periods_per_year))


def max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1.0
    return float(drawdown.min())


def calculate_metrics(equity: pd.DataFrame) -> dict[str, Any]:
    curve = equity["equity"]
    returns = curve.pct_change().fillna(0.0)
    return {
        "total_return": total_return(curve),
        "annualized_return": annualized_return(curve),
        "sharpe": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(curve),
        "final_equity": float(curve.iloc[-1]) if not curve.empty else 0.0,
        "bars": int(len(equity)),
    }

