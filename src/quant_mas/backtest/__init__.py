"""Backtesting package."""

from quant_mas.backtest.costs import CommissionModel, SlippageModel
from quant_mas.backtest.engine import BacktestEngine, BacktestResult
from quant_mas.backtest.metrics import (
    annualized_return,
    calculate_metrics,
    max_drawdown,
    sharpe_ratio,
    total_return,
)
from quant_mas.backtest.report import save_backtest_report

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "CommissionModel",
    "SlippageModel",
    "annualized_return",
    "calculate_metrics",
    "max_drawdown",
    "save_backtest_report",
    "sharpe_ratio",
    "total_return",
]
