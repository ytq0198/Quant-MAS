"""Backtest report persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.backtest.engine import BacktestResult


def save_backtest_report(
    result: BacktestResult,
    output_dir: str | Path,
    *,
    title: str = "Backtest Report",
    params: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Save metrics, equity curve, trades, and summary markdown."""
    target_dir = Path(output_dir).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = target_dir / "metrics.json"
    equity_path = target_dir / "equity_curve.csv"
    trades_path = target_dir / "trades.csv"
    summary_path = target_dir / "summary.md"

    metrics_path.write_text(
        json.dumps(result.metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    result.equity_curve.to_csv(equity_path, index=False)
    result.trades.to_csv(trades_path, index=False)
    summary_path.write_text(
        _build_summary(title=title, metrics=result.metrics, params=params or {}),
        encoding="utf-8",
    )

    return {
        "metrics": metrics_path,
        "equity_curve": equity_path,
        "trades": trades_path,
        "summary": summary_path,
    }


def save_walk_forward_report(
    *,
    metrics: dict[str, Any],
    windows: pd.DataFrame,
    oos_equity_curve: pd.DataFrame,
    oos_trades: pd.DataFrame,
    output_dir: str | Path,
    title: str = "Walk-forward Report",
    params: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Save train/val/test/oos walk-forward metrics and artifacts."""
    target_dir = Path(output_dir).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = target_dir / "metrics.json"
    windows_path = target_dir / "windows.csv"
    equity_path = target_dir / "oos_equity_curve.csv"
    trades_path = target_dir / "oos_trades.csv"
    summary_path = target_dir / "summary.md"

    metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    windows.to_csv(windows_path, index=False)
    oos_equity_curve.to_csv(equity_path, index=False)
    oos_trades.to_csv(trades_path, index=False)
    summary_path.write_text(
        _build_walk_forward_summary(
            title=title,
            metrics=metrics,
            params=params or {},
        ),
        encoding="utf-8",
    )
    return {
        "metrics": metrics_path,
        "windows": windows_path,
        "oos_equity_curve": equity_path,
        "oos_trades": trades_path,
        "summary": summary_path,
    }


def _build_summary(
    *,
    title: str,
    metrics: dict[str, Any],
    params: dict[str, Any],
) -> str:
    lines = [
        f"# {title}",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key} | {_format_value(value)} |")

    if params:
        lines.extend(["", "## Parameters", "", "| Parameter | Value |", "|-----------|-------|"])
        for key, value in params.items():
            lines.append(f"| {key} | {_format_value(value)} |")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `metrics.json`",
            "- `equity_curve.csv`",
            "- `trades.csv`",
        ]
    )
    return "\n".join(lines) + "\n"


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    if pd.isna(value):
        return ""
    return str(value)


def _build_walk_forward_summary(
    *,
    title: str,
    metrics: dict[str, Any],
    params: dict[str, Any],
) -> str:
    lines = [
        f"# {title}",
        "",
        "## Metrics",
        "",
    ]
    for section in ("summary", "train", "val", "test", "oos", "walk_forward"):
        values = metrics.get(section)
        if not isinstance(values, dict):
            continue
        lines.extend(
            [
                f"### {section}",
                "",
                "| Metric | Value |",
                "|--------|-------|",
            ]
        )
        for key, value in values.items():
            lines.append(f"| {key} | {_format_value(value)} |")
        lines.append("")

    if params:
        lines.extend(["## Parameters", "", "| Parameter | Value |", "|-----------|-------|"])
        for key, value in params.items():
            lines.append(f"| {key} | {_format_value(value)} |")
        lines.append("")

    lines.extend(
        [
            "## Artifacts",
            "",
            "- `metrics.json`",
            "- `windows.csv`",
            "- `oos_equity_curve.csv`",
            "- `oos_trades.csv`",
        ]
    )
    return "\n".join(lines) + "\n"
