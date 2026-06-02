"""Research baseline registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class BaselineRun:
    """One named research baseline or experiment run."""

    run_id: str
    name: str
    family: str
    metrics: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    notes: str = ""


class BaselineRegistry:
    """In-memory registry for comparing research baselines."""

    def __init__(self, baselines: list[BaselineRun] | None = None) -> None:
        self._baselines: list[BaselineRun] = []
        for baseline in baselines or []:
            self.add_baseline(baseline)

    def add_baseline(self, baseline: BaselineRun) -> BaselineRun:
        if any(item.run_id == baseline.run_id for item in self._baselines):
            raise ValueError(f"Baseline already exists: {baseline.run_id}")
        self._baselines.append(baseline)
        return baseline

    def list_baselines(self) -> list[BaselineRun]:
        return list(self._baselines)

    def compare_runs(
        self,
        metric_paths: list[str] | None = None,
    ) -> pd.DataFrame:
        metric_paths = metric_paths or [
            "total_return",
            "sharpe",
            "max_drawdown",
            "test_auc",
            "oos.sharpe",
        ]
        rows = []
        for baseline in self._baselines:
            row: dict[str, Any] = {
                "run_id": baseline.run_id,
                "name": baseline.name,
                "family": baseline.family,
            }
            for metric_path in metric_paths:
                row[metric_path] = resolve_metric(baseline.metrics, metric_path)
            rows.append(row)
        return pd.DataFrame(rows)

    def get_best(
        self,
        metric_path: str = "oos.sharpe",
        *,
        descending: bool = True,
    ) -> BaselineRun:
        candidates = [
            baseline
            for baseline in self._baselines
            if resolve_metric(baseline.metrics, metric_path) is not None
        ]
        if not candidates:
            raise ValueError(f"No baselines contain metric: {metric_path}")
        return sorted(
            candidates,
            key=lambda baseline: resolve_metric(baseline.metrics, metric_path),
            reverse=descending,
        )[0]


def resolve_metric(metrics: dict[str, Any], metric_path: str) -> Any:
    """Resolve flat or dotted metric paths."""
    if metric_path in metrics:
        return metrics[metric_path]
    current: Any = metrics
    for part in metric_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current
