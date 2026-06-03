"""Reward and episode metrics for simulation-only RL experiments."""

from __future__ import annotations

import math

import pandas as pd

from quant_mas.backtest.metrics import max_drawdown, sharpe_ratio, total_return
from quant_mas.rl.env_schema import RewardConfig


def compute_step_reward(
    *,
    prev_equity: float,
    equity: float,
    turnover: float,
    drawdown: float,
    config: RewardConfig,
    cost: float = 0.0,
) -> float:
    """Compute scalar reward from return, cost, turnover, and drawdown penalty."""
    if prev_equity <= 0:
        raise ValueError("prev_equity must be positive")
    step_return = equity / prev_equity - 1.0
    reward = (
        config.w_return * step_return
        - config.w_cost * cost
        - config.w_turnover * abs(turnover)
        - config.w_drawdown_penalty * abs(min(drawdown, 0.0))
    )
    if not math.isfinite(reward):
        raise ValueError("reward is not finite")
    return float(reward)


def compute_episode_metrics(
    equity_curve: pd.Series,
    *,
    turnover_sum: float = 0.0,
) -> dict[str, float]:
    """Compute compact episode metrics."""
    curve = equity_curve.astype(float)
    returns = curve.pct_change().fillna(0.0)
    return {
        "total_return": total_return(curve),
        "sharpe": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(curve),
        "final_equity": float(curve.iloc[-1]) if not curve.empty else 0.0,
        "turnover_sum": float(turnover_sum),
        "bars": float(len(curve)),
    }
