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
from quant_mas.backtest.report import save_backtest_report, save_walk_forward_report
from quant_mas.backtest.walk_forward import (
    WalkForwardResult,
    WalkForwardWindow,
    build_walk_forward_windows,
    run_walk_forward,
    run_walk_forward_from_config,
)

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "CommissionModel",
    "SlippageModel",
    "annualized_return",
    "calculate_metrics",
    "max_drawdown",
    "save_backtest_report",
    "save_walk_forward_report",
    "sharpe_ratio",
    "total_return",
    "WalkForwardResult",
    "WalkForwardWindow",
    "build_walk_forward_windows",
    "run_walk_forward",
    "run_walk_forward_from_config",
]
