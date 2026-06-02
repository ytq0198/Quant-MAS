"""Experiment metric collection and comparison tables."""

from __future__ import annotations

from typing import Any

import pandas as pd

from quant_mas.memory import ExperimentRecord
from quant_mas.research.baseline import BaselineRun, resolve_metric


DEFAULT_METRICS = (
    "total_return",
    "sharpe",
    "max_drawdown",
    "final_equity",
    "test_auc",
    "val_auc",
    "train_auc",
    "oos.sharpe",
    "oos.total_return",
    "oos.max_drawdown",
)


def collect_experiment_metrics(
    records: list[ExperimentRecord],
    *,
    metric_paths: tuple[str, ...] = DEFAULT_METRICS,
) -> list[BaselineRun]:
    """Convert ExperimentMemory records into baseline runs."""
    runs = []
    for record in records:
        family = _infer_family(record.name)
        metrics = {
            metric_path: resolve_metric(record.metrics, metric_path)
            for metric_path in metric_paths
            if resolve_metric(record.metrics, metric_path) is not None
        }
        runs.append(
            BaselineRun(
                run_id=record.experiment_id,
                name=record.name,
                family=family,
                metrics={**record.metrics, **metrics},
                params=record.params,
                artifacts=record.artifacts,
                notes=record.notes,
            )
        )
    return runs


def build_comparison_table(
    runs: list[BaselineRun],
    *,
    metric_paths: tuple[str, ...] = DEFAULT_METRICS,
    families: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Build a compact comparison table for research reporting."""
    allowed = set(families) if families else None
    rows: list[dict[str, Any]] = []
    for run in runs:
        if allowed is not None and run.family not in allowed:
            continue
        row: dict[str, Any] = {
            "run_id": run.run_id,
            "name": run.name,
            "family": run.family,
        }
        for metric_path in metric_paths:
            row[metric_path] = resolve_metric(run.metrics, metric_path)
        rows.append(row)
    return pd.DataFrame(rows)


def _infer_family(name: str) -> str:
    normalized = name.lower()
    if "walk" in normalized or "oos" in normalized:
        return "walk_forward"
    if "ml_backtest" in normalized or "ml signal" in normalized or "ml_signal" in normalized:
        return "ml_backtest"
    if "lgbm" in normalized or "lightgbm" in normalized:
        return "lightgbm"
    if "ma_cross" in normalized or "moving_average" in normalized or "ma cross" in normalized:
        return "ma_cross"
    return "other"
