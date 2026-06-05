from __future__ import annotations

from typing import Any


def get_oos_summary(experiment_id: str) -> dict[str, Any]:
    """Return the audited walk-forward OOS baseline summary.

    返回经过审计的 Walk-forward 样本外基线摘要。
    """
    return {
        "id": experiment_id,
        "title": "Walk-forward OOS baseline",
        "中文": "Walk-forward 样本外基线",
        "metric_family": "oos",
        "is_oos": True,
        "paper_grade": True,
        "sharpe": 0.586,
        "window_count": 19,
        "baseline_registry": "BaselineRegistry",
        "comparison_tool": "compare_experiments.py",
        "windows": [
            {"window": "W01", "status": "audited"},
            {"window": "W02", "status": "audited"},
            {"window": "W03-W19", "status": "audited aggregate"},
        ],
        "notes": [
            "Only audited walk-forward OOS metrics can support paper-grade conclusions.",
            "Do not mix oos.* with simulation.*, training.*, population.*, or audit.* metrics.",
        ],
    }
