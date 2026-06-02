"""Walk-forward out-of-sample evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from quant_mas.backtest.costs import CommissionModel, SlippageModel
from quant_mas.backtest.engine import BacktestEngine
from quant_mas.backtest.metrics import calculate_metrics
from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.memory import ExperimentMemory
from quant_mas.models import (
    BasePredictiveModel,
    LightGBMDirectionModel,
    evaluate_direction_model,
    resolve_target_column,
    select_feature_columns,
)
from quant_mas.strategies import MLSignalStrategy
from quant_mas.utils import resolve_training_device


@dataclass(frozen=True)
class WalkForwardWindow:
    """Date boundaries for one chronological walk-forward window."""

    window_id: int
    train_dates: pd.Index
    validation_dates: pd.Index
    test_dates: pd.Index
    oos_dates: pd.Index


@dataclass(frozen=True)
class WalkForwardResult:
    """Walk-forward evaluation result and report-ready artifacts."""

    metrics: dict[str, Any]
    windows: pd.DataFrame
    oos_equity_curve: pd.DataFrame
    oos_trades: pd.DataFrame
    feature_columns: list[str]
    target_column: str


def run_walk_forward(
    feature_table: pd.DataFrame,
    *,
    config: dict[str, Any],
    model_factory: Callable[..., BasePredictiveModel] | None = None,
) -> WalkForwardResult:
    """Run chronological walk-forward training, prediction, and OOS backtests."""
    clean, feature_columns, target_column = _prepare_walk_forward_frame(
        feature_table,
        target=config.get("target", "future_direction"),
    )
    windows = build_walk_forward_windows(
        clean["date"],
        train_window=config.get("walk_forward", {}).get("train_window", 252),
        validation_window=config.get("walk_forward", {}).get("validation_window", 63),
        test_window=config.get("walk_forward", {}).get("test_window", 63),
        oos_window=config.get("walk_forward", {}).get("oos_window", 21),
        step=config.get("walk_forward", {}).get("step", 21),
        max_windows=config.get("walk_forward", {}).get("max_windows"),
    )
    if not windows:
        raise ValueError("Walk-forward configuration produced no complete windows")

    model_config = config.get("model", {})
    params = dict(model_config.get("params", {}))
    device_requested = model_config.get("device") or params.pop("device", None) or "cpu"
    resolved_device = resolve_training_device(device_requested)
    model_cls = model_factory or LightGBMDirectionModel

    strategy_config = config.get("strategy", {})
    portfolio_config = config.get("portfolio", {})
    costs_config = config.get("costs", {})
    initial_cash = float(portfolio_config.get("initial_cash", 100_000.0))

    window_rows: list[dict[str, Any]] = []
    equity_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []

    for window in windows:
        splits = _slice_window(clean, window)
        model = _build_model(
            model_cls=model_cls,
            params=params,
            device_requested=device_requested,
            resolved_device=resolved_device,
        )
        model.fit(splits["train"].loc[:, feature_columns], splits["train"][target_column].astype(int))

        row = _window_metadata(window, splits)
        for split_name, prefix in (
            ("train", "train"),
            ("validation", "val"),
            ("test", "test"),
            ("oos", "oos"),
        ):
            row.update(
                evaluate_direction_model(
                    model,
                    splits[split_name].loc[:, feature_columns],
                    splits[split_name][target_column].astype(int).reset_index(drop=True),
                    prefix,
                    _split_metadata(splits[split_name]),
                )
            )

        predictions = splits["oos"].loc[:, ["date", "symbol"]].copy()
        predictions["pred_proba"] = model.predict_proba(
            splits["oos"].loc[:, feature_columns]
        ).to_numpy()
        strategy = MLSignalStrategy(
            predictions,
            buy_threshold=strategy_config.get("buy_threshold", 0.6),
            sell_threshold=strategy_config.get("sell_threshold", 0.4),
            max_weight=strategy_config.get("max_weight", 1.0),
        )
        backtest_result = BacktestEngine(
            strategy=strategy,
            initial_cash=initial_cash,
            commission_model=CommissionModel(costs_config.get("commission_bps", 0.0)),
            slippage_model=SlippageModel(costs_config.get("slippage_bps", 0.0)),
        ).run(splits["oos"])
        row.update({f"oos_backtest_{key}": value for key, value in backtest_result.metrics.items()})
        window_rows.append(row)

        equity = backtest_result.equity_curve.copy()
        equity.insert(0, "window_id", window.window_id)
        equity_frames.append(equity)
        trades = backtest_result.trades.copy()
        if not trades.empty:
            trades.insert(0, "window_id", window.window_id)
        trade_frames.append(trades)

    windows_frame = pd.DataFrame(window_rows)
    oos_equity = _combine_oos_equity(equity_frames, initial_cash)
    oos_trades = (
        pd.concat(trade_frames, ignore_index=True)
        if trade_frames
        else pd.DataFrame()
    )
    metrics = _aggregate_metrics(
        windows_frame,
        oos_equity,
        config=config,
        feature_columns=feature_columns,
        target_column=target_column,
        device_requested=resolved_device.requested,
        device_resolved=resolved_device.resolved,
        device_fallback=resolved_device.fallback,
        device_reason=resolved_device.reason,
    )
    return WalkForwardResult(
        metrics=metrics,
        windows=windows_frame,
        oos_equity_curve=oos_equity,
        oos_trades=oos_trades,
        feature_columns=feature_columns,
        target_column=target_column,
    )


def run_walk_forward_from_config(
    *,
    config: dict[str, Any],
    storage_config: str | Path,
    features_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    experiment_name: str | None = None,
    model_factory: Callable[..., BasePredictiveModel] | None = None,
) -> dict[str, Any]:
    """Load feature data, run walk-forward evaluation, save report and memory."""
    from quant_mas.backtest.report import save_walk_forward_report

    catalog = DataCatalog.from_yaml(storage_config)
    feature_path = _resolve_path(
        features_path,
        _path_from_config(
            config,
            "data",
            "features_path",
            catalog.path_for("features_dir", "features.parquet"),
        ),
    )
    report_dir = _resolve_path(
        output_dir,
        _path_from_config(
            config,
            "output",
            "dir",
            catalog.path_for("reports_dir", "walk_forward_latest"),
        ),
    )
    name = experiment_name or config.get("experiment", {}).get("name", "walk_forward")
    features = ParquetStorage().load(feature_path)
    result = run_walk_forward(features, config=config, model_factory=model_factory)
    artifacts = save_walk_forward_report(
        metrics=result.metrics,
        windows=result.windows,
        oos_equity_curve=result.oos_equity_curve,
        oos_trades=result.oos_trades,
        output_dir=report_dir,
        title=name,
        params={
            "features_path": str(feature_path),
            "feature_columns": result.feature_columns,
            "target_column": result.target_column,
            "config": config,
        },
    )
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=name,
        metrics=result.metrics,
        artifacts=artifacts,
        params={
            "config": config,
            "features_path": str(feature_path),
            "feature_columns": result.feature_columns,
            "target_column": result.target_column,
        },
    )
    return {
        "metrics": result.metrics,
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "experiment_memory": str(memory_path),
        "feature_columns": result.feature_columns,
        "target_column": result.target_column,
        "windows": result.windows.to_dict(orient="records"),
    }


def build_walk_forward_windows(
    dates: pd.Series,
    *,
    train_window: int,
    validation_window: int,
    test_window: int,
    oos_window: int,
    step: int,
    max_windows: int | None = None,
) -> list[WalkForwardWindow]:
    """Build non-random chronological windows from unique dates."""
    sizes = {
        "train_window": train_window,
        "validation_window": validation_window,
        "test_window": test_window,
        "oos_window": oos_window,
        "step": step,
    }
    invalid = [name for name, value in sizes.items() if int(value) <= 0]
    if invalid:
        raise ValueError(f"Walk-forward window sizes must be positive: {invalid}")

    unique_dates = pd.Index(pd.to_datetime(dates).drop_duplicates().sort_values())
    total = train_window + validation_window + test_window + oos_window
    windows: list[WalkForwardWindow] = []
    start = 0
    while start + total <= len(unique_dates):
        train_start = start
        validation_start = train_start + train_window
        test_start = validation_start + validation_window
        oos_start = test_start + test_window
        oos_end = oos_start + oos_window
        windows.append(
            WalkForwardWindow(
                window_id=len(windows) + 1,
                train_dates=unique_dates[train_start:validation_start],
                validation_dates=unique_dates[validation_start:test_start],
                test_dates=unique_dates[test_start:oos_start],
                oos_dates=unique_dates[oos_start:oos_end],
            )
        )
        if max_windows is not None and len(windows) >= int(max_windows):
            break
        start += step
    return windows


def _prepare_walk_forward_frame(
    frame: pd.DataFrame,
    *,
    target: str,
) -> tuple[pd.DataFrame, list[str], str]:
    target_column = resolve_target_column(frame, target)
    feature_columns = select_feature_columns(frame, target_column)
    if not feature_columns:
        raise ValueError("No numeric feature columns available for walk-forward")
    required = _unique_preserve_order(
        [
            "date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            target_column,
            *feature_columns,
        ]
    )
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Feature table missing required columns: {missing}")
    clean = frame.loc[:, required].copy()
    clean["date"] = pd.to_datetime(clean["date"], errors="raise")
    clean["symbol"] = clean["symbol"].astype(str).str.upper()
    clean = clean.dropna(subset=[target_column, *feature_columns])
    clean = clean.sort_values(["date", "symbol"]).reset_index(drop=True)
    if clean.empty:
        raise ValueError("No rows remain after dropping missing walk-forward data")
    return clean, feature_columns, target_column


def _slice_window(
    data: pd.DataFrame,
    window: WalkForwardWindow,
) -> dict[str, pd.DataFrame]:
    splits = {
        "train": data[data["date"].isin(window.train_dates)].reset_index(drop=True),
        "validation": data[data["date"].isin(window.validation_dates)].reset_index(drop=True),
        "test": data[data["date"].isin(window.test_dates)].reset_index(drop=True),
        "oos": data[data["date"].isin(window.oos_dates)].reset_index(drop=True),
    }
    empty = [name for name, frame in splits.items() if frame.empty]
    if empty:
        raise ValueError(f"Walk-forward split contains empty frames: {empty}")
    return splits


def _build_model(
    *,
    model_cls: Callable[..., BasePredictiveModel],
    params: dict[str, Any],
    device_requested: str,
    resolved_device,
) -> BasePredictiveModel:
    try:
        return model_cls(
            device=device_requested,
            resolved_device=resolved_device,
            **params,
        )
    except TypeError:
        return model_cls(**params)


def _window_metadata(
    window: WalkForwardWindow,
    splits: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    row: dict[str, Any] = {"window_id": window.window_id}
    for name, frame in splits.items():
        row[f"{name}_start_date"] = str(frame["date"].min().date())
        row[f"{name}_end_date"] = str(frame["date"].max().date())
        row[f"{name}_samples"] = int(len(frame))
    return row


def _split_metadata(frame: pd.DataFrame):
    from quant_mas.models.training import SplitMetadata

    return SplitMetadata(
        start_date=str(frame["date"].min().date()),
        end_date=str(frame["date"].max().date()),
        samples=int(len(frame)),
    )


def _combine_oos_equity(
    frames: list[pd.DataFrame],
    initial_cash: float,
) -> pd.DataFrame:
    if not frames:
        return pd.DataFrame(columns=["date", "window_id", "returns", "equity"])
    returns = pd.concat(
        [
            frame.loc[:, ["date", "window_id", "returns"]]
            for frame in frames
            if not frame.empty
        ],
        ignore_index=True,
    ).sort_values(["date", "window_id"], ignore_index=True)
    returns["returns"] = returns["returns"].fillna(0.0)
    returns["equity"] = initial_cash * (1.0 + returns["returns"]).cumprod()
    return returns


def _aggregate_metrics(
    windows: pd.DataFrame,
    oos_equity: pd.DataFrame,
    *,
    config: dict[str, Any],
    feature_columns: list[str],
    target_column: str,
    device_requested: str,
    device_resolved: str,
    device_fallback: bool,
    device_reason: str | None,
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "summary": {
            "window_count": int(len(windows)),
            "feature_count": int(len(feature_columns)),
            "target_column": target_column,
            "device_requested": device_requested,
            "device_resolved": device_resolved,
            "device_fallback": device_fallback,
            "device_reason": device_reason,
        },
        "train": _aggregate_split_metrics(windows, "train"),
        "val": _aggregate_split_metrics(windows, "val"),
        "test": _aggregate_split_metrics(windows, "test"),
        "oos": {
            **_aggregate_split_metrics(windows, "oos"),
            **calculate_metrics(oos_equity),
        },
        "walk_forward": dict(config.get("walk_forward", {})),
    }
    metrics["oos"]["backtest_total_return_mean"] = _mean_or_none(
        windows.get("oos_backtest_total_return", pd.Series(dtype=float))
    )
    metrics["oos"]["backtest_sharpe_mean"] = _mean_or_none(
        windows.get("oos_backtest_sharpe", pd.Series(dtype=float))
    )
    metrics["oos"]["backtest_max_drawdown_mean"] = _mean_or_none(
        windows.get("oos_backtest_max_drawdown", pd.Series(dtype=float))
    )
    return metrics


def _aggregate_split_metrics(windows: pd.DataFrame, prefix: str) -> dict[str, Any]:
    return {
        "accuracy_mean": _mean_or_none(windows.get(f"{prefix}_accuracy", pd.Series(dtype=float))),
        "auc_mean": _mean_or_none(windows.get(f"{prefix}_auc", pd.Series(dtype=float))),
        "positive_rate_mean": _mean_or_none(
            windows.get(f"{prefix}_positive_rate", pd.Series(dtype=float))
        ),
        "samples": int(windows.get(f"{prefix}_samples", pd.Series(dtype=int)).sum()),
        "start_date": _min_date(windows.get(f"{prefix}_start_date", pd.Series(dtype=str))),
        "end_date": _max_date(windows.get(f"{prefix}_end_date", pd.Series(dtype=str))),
    }


def _mean_or_none(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return None
    return float(clean.mean())


def _min_date(series: pd.Series) -> str | None:
    if series.empty:
        return None
    return str(pd.to_datetime(series).min().date())


def _max_date(series: pd.Series) -> str | None:
    if series.empty:
        return None
    return str(pd.to_datetime(series).max().date())


def _resolve_path(value: str | Path | None, default: Path) -> Path:
    return Path(value).expanduser() if value is not None else default.expanduser()


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _path_from_config(
    config: dict[str, Any],
    section: str,
    key: str,
    default: Path,
) -> Path:
    value = config.get(section, {}).get(key)
    return Path(value).expanduser() if value else default
