"""Walk-forward OOS validation for exported strategy candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.backtest import (
    BacktestEngine,
    CommissionModel,
    SlippageModel,
    build_walk_forward_windows,
    calculate_metrics,
)
from quant_mas.research.strategy_candidate import StrategyCandidate
from quant_mas.strategies import Strategy


@dataclass(frozen=True)
class CandidateValidationResult:
    """Walk-forward validation output for one strategy candidate."""

    candidate: StrategyCandidate
    metrics: dict[str, Any]
    windows: pd.DataFrame
    oos_equity_curve: pd.DataFrame
    oos_trades: pd.DataFrame
    artifacts: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CandidateBatchValidationResult:
    """Batch walk-forward validation output for multiple candidates."""

    results: list[CandidateValidationResult]
    comparison: pd.DataFrame
    metrics: dict[str, Any]
    artifacts: dict[str, str] = field(default_factory=dict)


def run_candidate_walk_forward(
    candidate: StrategyCandidate,
    feature_table: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> CandidateValidationResult:
    """Run deterministic walk-forward OOS backtests for a StrategyCandidate."""
    data = _prepare_frame(_signal_safe_frame(feature_table))
    walk_config = config.get("walk_forward", {})
    windows = build_walk_forward_windows(
        data["date"],
        train_window=int(walk_config.get("train_window", 252)),
        validation_window=int(walk_config.get("validation_window", 63)),
        test_window=int(walk_config.get("test_window", 63)),
        oos_window=int(walk_config.get("oos_window", 21)),
        step=int(walk_config.get("step", 21)),
        max_windows=walk_config.get("max_windows"),
    )
    if not windows:
        raise ValueError("Candidate walk-forward configuration produced no complete windows")

    portfolio_config = config.get("portfolio", {})
    costs_config = config.get("costs", {})
    initial_cash = float(portfolio_config.get("initial_cash", 100_000.0))
    engine = lambda: BacktestEngine(
        CandidateStrategyAdapter(candidate),
        initial_cash=initial_cash,
        commission_model=CommissionModel(costs_config.get("commission_bps", 0.0)),
        slippage_model=SlippageModel(costs_config.get("slippage_bps", 0.0)),
    )

    window_rows: list[dict[str, Any]] = []
    equity_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    for window in windows:
        splits = _slice_window(data, window)
        result = engine().run(splits["oos"])
        row = _window_metadata(window, splits)
        row.update({f"oos_backtest_{key}": value for key, value in result.metrics.items()})
        window_rows.append(row)
        equity = result.equity_curve.copy()
        equity.insert(0, "window_id", window.window_id)
        equity_frames.append(equity)
        trades = result.trades.copy()
        if not trades.empty:
            trades.insert(0, "window_id", window.window_id)
        trade_frames.append(trades)

    windows_frame = pd.DataFrame(window_rows)
    oos_equity = _combine_oos_equity(equity_frames, initial_cash)
    oos_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    metrics = _aggregate_candidate_metrics(
        candidate=candidate,
        windows=windows_frame,
        oos_equity=oos_equity,
        config=config,
    )
    return CandidateValidationResult(
        candidate=candidate,
        metrics=metrics,
        windows=windows_frame,
        oos_equity_curve=oos_equity,
        oos_trades=oos_trades,
    )


def run_candidate_batch_walk_forward(
    candidates: list[StrategyCandidate],
    feature_table: pd.DataFrame,
    *,
    config: dict[str, Any],
    top_k: int | None = None,
) -> CandidateBatchValidationResult:
    """Run candidate OOS validation for a ranked candidate list."""
    selected = list(candidates)
    if top_k is not None:
        selected = selected[: int(top_k)]
    if not selected:
        raise ValueError("No StrategyCandidate records provided for batch OOS validation")

    results = [
        run_candidate_walk_forward(candidate, feature_table, config=config)
        for candidate in selected
    ]
    comparison = build_candidate_oos_comparison(results)
    metrics = _aggregate_batch_metrics(comparison, config=config)
    return CandidateBatchValidationResult(
        results=results,
        comparison=comparison,
        metrics=metrics,
    )


class CandidateStrategyAdapter(Strategy):
    """Convert a StrategyCandidate into deterministic target-weight signals."""

    def __init__(self, candidate: StrategyCandidate) -> None:
        self.candidate = candidate

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = _prepare_frame(_signal_safe_frame(data))
        rows = []
        for symbol, group in frame.groupby("symbol", sort=True):
            group = group.sort_values("date").reset_index(drop=True)
            signal = _candidate_signal(group)
            scale = float(self.candidate.params.get("scale", 1.0))
            if self.candidate.agent_type == "momentum":
                weights = (0.5 + scale * signal * 10.0).clip(0.0, 1.0)
            elif self.candidate.agent_type == "mean_reversion":
                weights = (0.5 - scale * signal * 10.0).clip(0.0, 1.0)
            else:
                raise ValueError("Unsupported StrategyCandidate agent_type for OOS validation")
            rows.append(
                pd.DataFrame(
                    {
                        "date": group["date"],
                        "symbol": symbol,
                        "target_weight": weights,
                    }
                )
            )
        return pd.concat(rows, ignore_index=True)


def save_candidate_validation_report(
    result: CandidateValidationResult,
    output_dir: str | Path,
) -> dict[str, str]:
    """Persist candidate OOS metrics and report artifacts."""
    target = Path(output_dir).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    metrics_path = target / "metrics.json"
    windows_path = target / "windows.csv"
    equity_path = target / "oos_equity_curve.csv"
    trades_path = target / "oos_trades.csv"
    summary_path = target / "summary.md"
    metrics_path.write_text(
        json.dumps(result.metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    result.windows.to_csv(windows_path, index=False)
    result.oos_equity_curve.to_csv(equity_path, index=False)
    result.oos_trades.to_csv(trades_path, index=False)
    summary_path.write_text(_summary_markdown(result), encoding="utf-8")
    return {
        "metrics": str(metrics_path),
        "windows": str(windows_path),
        "oos_equity_curve": str(equity_path),
        "oos_trades": str(trades_path),
        "summary": str(summary_path),
    }


def save_candidate_batch_validation_report(
    result: CandidateBatchValidationResult,
    output_dir: str | Path,
) -> dict[str, str]:
    """Persist batch comparison plus per-candidate OOS artifacts."""
    target = Path(output_dir).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    metrics_path = target / "metrics.json"
    comparison_csv = target / "candidate_oos_comparison.csv"
    comparison_md = target / "candidate_oos_comparison.md"
    metrics_path.write_text(
        json.dumps(result.metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    result.comparison.to_csv(comparison_csv, index=False)
    comparison_md.write_text(_comparison_markdown(result), encoding="utf-8")

    artifacts: dict[str, str] = {
        "metrics": str(metrics_path),
        "comparison_csv": str(comparison_csv),
        "comparison_md": str(comparison_md),
    }
    for candidate_result in result.results:
        candidate_dir = target / "candidates" / candidate_result.candidate.candidate_id
        candidate_artifacts = save_candidate_validation_report(candidate_result, candidate_dir)
        for key, value in candidate_artifacts.items():
            artifacts[f"{candidate_result.candidate.candidate_id}.{key}"] = value
    return artifacts


def build_candidate_oos_comparison(
    results: list[CandidateValidationResult],
) -> pd.DataFrame:
    """Build a sorted comparison table from candidate OOS results."""
    rows: list[dict[str, Any]] = []
    for rank, result in enumerate(results, start=1):
        candidate = result.candidate
        summary = result.metrics.get("summary", {})
        oos = result.metrics.get("oos", {})
        baseline = float(summary.get("baseline_oos_sharpe", 0.586))
        sharpe = float(oos.get("sharpe", 0.0))
        rows.append(
            {
                "input_rank": rank,
                "candidate_id": candidate.candidate_id,
                "agent_id": candidate.agent_id,
                "agent_type": candidate.agent_type,
                "oos.sharpe": sharpe,
                "oos.total_return": oos.get("total_return"),
                "oos.max_drawdown": oos.get("max_drawdown"),
                "oos.final_equity": oos.get("final_equity"),
                "summary.window_count": summary.get("window_count"),
                "summary.baseline_oos_sharpe": baseline,
                "summary.vs_baseline_sharpe": summary.get("vs_baseline_sharpe"),
                "exceeds_baseline": sharpe > baseline,
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["oos.sharpe", "candidate_id"], ascending=[False, True], ignore_index=True)
        .assign(oos_rank=lambda frame: range(1, len(frame) + 1))
    )


def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "symbol", "open", "high", "low", "close", "volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Candidate OOS feature table missing columns: {sorted(missing)}")
    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise")
    data["symbol"] = data["symbol"].astype(str).str.upper()
    return data.sort_values(["date", "symbol"]).reset_index(drop=True)


def _signal_safe_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop label/future columns before candidate signal generation.

    Real feature tables (e.g. server ``features.parquet``) may include
    ``future_*`` labels for ML training. Candidate OOS must not read them,
    but their presence in the parquet file is allowed.
    """
    forbidden = [
        column
        for column in frame.columns
        if str(column).startswith("future_") or str(column).lower() in {"label", "target"}
    ]
    if not forbidden:
        return frame
    return frame.drop(columns=forbidden)


def _candidate_signal(group: pd.DataFrame) -> pd.Series:
    if "ma_distance_5" in group.columns:
        return pd.to_numeric(group["ma_distance_5"], errors="raise").fillna(0.0)
    if "last_return" in group.columns:
        return pd.to_numeric(group["last_return"], errors="raise").fillna(0.0)
    return group["close"].astype(float).pct_change().fillna(0.0)


def _slice_window(data, window) -> dict[str, pd.DataFrame]:
    splits = {
        "train": data[data["date"].isin(window.train_dates)].reset_index(drop=True),
        "validation": data[data["date"].isin(window.validation_dates)].reset_index(drop=True),
        "test": data[data["date"].isin(window.test_dates)].reset_index(drop=True),
        "oos": data[data["date"].isin(window.oos_dates)].reset_index(drop=True),
    }
    empty = [name for name, frame in splits.items() if frame.empty]
    if empty:
        raise ValueError(f"Candidate walk-forward split contains empty frames: {empty}")
    return splits


def _window_metadata(window, splits: dict[str, pd.DataFrame]) -> dict[str, Any]:
    row: dict[str, Any] = {"window_id": int(window.window_id)}
    for name, frame in splits.items():
        row[f"{name}_start_date"] = str(frame["date"].min().date())
        row[f"{name}_end_date"] = str(frame["date"].max().date())
        row[f"{name}_samples"] = int(len(frame))
    return row


def _combine_oos_equity(frames: list[pd.DataFrame], initial_cash: float) -> pd.DataFrame:
    if not frames:
        return pd.DataFrame(columns=["date", "window_id", "returns", "equity"])
    returns = pd.concat(
        [frame.loc[:, ["date", "window_id", "returns"]] for frame in frames if not frame.empty],
        ignore_index=True,
    ).sort_values(["date", "window_id"], ignore_index=True)
    returns["returns"] = returns["returns"].fillna(0.0)
    returns["equity"] = initial_cash * (1.0 + returns["returns"]).cumprod()
    return returns


def _aggregate_candidate_metrics(
    *,
    candidate: StrategyCandidate,
    windows: pd.DataFrame,
    oos_equity: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    baseline = float(config.get("candidate_oos", {}).get("baseline_oos_sharpe", 0.586))
    metrics = {
        "summary": {
            "candidate_id": candidate.candidate_id,
            "agent_id": candidate.agent_id,
            "agent_type": candidate.agent_type,
            "window_count": int(len(windows)),
            "baseline_experiment_id": config.get("candidate_oos", {}).get(
                "baseline_experiment_id",
                "EXP-20260602-008",
            ),
            "baseline_oos_sharpe": baseline,
        },
        "oos": {
            **_split_summary(windows, "oos"),
            **calculate_metrics(oos_equity),
        },
        "walk_forward": dict(config.get("walk_forward", {})),
    }
    metrics["summary"]["vs_baseline_sharpe"] = float(metrics["oos"]["sharpe"] - baseline)
    metrics["oos"]["backtest_total_return_mean"] = _mean(windows.get("oos_backtest_total_return", pd.Series(dtype=float)))
    metrics["oos"]["backtest_sharpe_mean"] = _mean(windows.get("oos_backtest_sharpe", pd.Series(dtype=float)))
    metrics["oos"]["backtest_max_drawdown_mean"] = _mean(windows.get("oos_backtest_max_drawdown", pd.Series(dtype=float)))
    return metrics


def _split_summary(windows: pd.DataFrame, prefix: str) -> dict[str, Any]:
    return {
        "samples": int(windows.get(f"{prefix}_samples", pd.Series(dtype=int)).sum()),
        "start_date": _min_date(windows.get(f"{prefix}_start_date", pd.Series(dtype=str))),
        "end_date": _max_date(windows.get(f"{prefix}_end_date", pd.Series(dtype=str))),
    }


def _mean(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    return float(clean.mean()) if not clean.empty else None


def _min_date(series: pd.Series) -> str | None:
    return None if series.empty else str(pd.to_datetime(series).min().date())


def _max_date(series: pd.Series) -> str | None:
    return None if series.empty else str(pd.to_datetime(series).max().date())


def _summary_markdown(result: CandidateValidationResult) -> str:
    metrics = result.metrics
    summary = metrics["summary"]
    oos = metrics["oos"]
    return "\n".join(
        [
            "# StrategyCandidate Walk-forward OOS Validation",
            "",
            f"- candidate_id: {summary['candidate_id']}",
            f"- agent_type: {summary['agent_type']}",
            f"- oos.sharpe: {oos['sharpe']:.6f}",
            f"- baseline_oos_sharpe: {summary['baseline_oos_sharpe']:.6f}",
            f"- vs_baseline_sharpe: {summary['vs_baseline_sharpe']:.6f}",
            "",
            "This OOS result is produced by the candidate walk-forward hook.",
            "It is not a live trading recommendation and does not bypass risk or audit.",
            "",
        ]
    )


def _aggregate_batch_metrics(
    comparison: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    baseline = float(config.get("candidate_oos", {}).get("baseline_oos_sharpe", 0.586))
    best = comparison.iloc[0].to_dict()
    return {
        "summary": {
            "candidate_count": int(len(comparison)),
            "best_candidate_id": best["candidate_id"],
            "best_agent_type": best["agent_type"],
            "best_oos_sharpe": float(best["oos.sharpe"]),
            "baseline_oos_sharpe": baseline,
            "best_vs_baseline_sharpe": float(best["oos.sharpe"] - baseline),
            "exceeds_baseline_count": int(comparison["exceeds_baseline"].sum()),
            "baseline_experiment_id": config.get("candidate_oos", {}).get(
                "baseline_experiment_id",
                "EXP-20260602-008",
            ),
        },
        "comparison": comparison.to_dict(orient="records"),
        "walk_forward": dict(config.get("walk_forward", {})),
    }


def _comparison_markdown(result: CandidateBatchValidationResult) -> str:
    summary = result.metrics["summary"]
    lines = [
        "# StrategyCandidate Batch OOS Comparison",
        "",
        f"- candidate_count: {summary['candidate_count']}",
        f"- best_candidate_id: {summary['best_candidate_id']}",
        f"- best_oos_sharpe: {summary['best_oos_sharpe']:.6f}",
        f"- baseline_oos_sharpe: {summary['baseline_oos_sharpe']:.6f}",
        f"- best_vs_baseline_sharpe: {summary['best_vs_baseline_sharpe']:.6f}",
        "",
        "| Rank | Candidate | Agent Type | OOS Sharpe | vs Baseline | Exceeds Baseline |",
        "|------|-----------|------------|------------|-------------|------------------|",
    ]
    for row in result.comparison.to_dict(orient="records"):
        lines.append(
            "| {rank} | {candidate} | {agent_type} | {sharpe:.6f} | {delta:.6f} | {exceeds} |".format(
                rank=row["oos_rank"],
                candidate=row["candidate_id"],
                agent_type=row["agent_type"],
                sharpe=float(row["oos.sharpe"]),
                delta=float(row["summary.vs_baseline_sharpe"]),
                exceeds=bool(row["exceeds_baseline"]),
            )
        )
    lines.extend(
        [
            "",
            "Only this batch OOS validation hook may compare population candidates using `oos.*` metrics.",
            "These results remain research artifacts and are not trading recommendations.",
            "",
        ]
    )
    return "\n".join(lines)
