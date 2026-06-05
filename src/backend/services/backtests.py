from __future__ import annotations

from typing import Any


def get_backtest_summary(backtest_id: str) -> dict[str, Any]:
    """Return a research-only backtest summary fixture.

    返回仅用于研究展示的回测摘要夹具。
    """
    return {
        "id": backtest_id,
        "title": "Demo deterministic backtest summary",
        "中文": "演示用确定性回测摘要",
        "metric_family": "backtest.summary",
        "is_oos": False,
        "research_only": True,
        "strategy": "MLSignalStrategy candidate",
        "time_range": "local fixture",
        "metrics": {
            "total_return": None,
            "annualized_return": None,
            "max_drawdown": None,
            "sharpe": None,
        },
        "chart": [
            {"label": "start", "equity": 1.0},
            {"label": "mid", "equity": 1.03},
            {"label": "end", "equity": 1.01},
        ],
        "notes": [
            "Backtest summaries are not paper-grade OOS conclusions.",
            "Use walk-forward OOS for paper-grade baseline comparison.",
        ],
        "disclaimer": "Research only; not financial advice; not a live-trading signal.",
    }
