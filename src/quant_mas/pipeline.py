"""End-to-end quant research pipeline."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from quant_mas.backtest import (
    BacktestEngine,
    CommissionModel,
    SlippageModel,
    save_backtest_report,
)
from quant_mas.data import DataCatalog, ParquetStorage, YFinanceFetcher
from quant_mas.features import build_feature_table_from_config
from quant_mas.memory import ExperimentMemory
from quant_mas.strategies import MovingAverageCrossStrategy, Strategy


LogFn = Callable[[str], None]


@dataclass(frozen=True)
class PipelineResult:
    """Artifacts and metrics produced by one pipeline run."""

    raw_path: Path
    features_path: Path
    output_dir: Path
    experiment_memory_path: Path
    artifacts: dict[str, Path]
    metrics: dict[str, Any]


def run_quant_pipeline(
    *,
    symbols: list[str],
    start: str,
    end: str,
    raw_dir: str | Path | None,
    features_dir: str | Path | None,
    output_dir: str | Path | None,
    storage_config: str | Path,
    features_config: str | Path,
    backtest_config: str | Path,
    skip_download: bool,
    skip_features: bool,
    strategy_name: str,
    experiment_name: str,
    log: LogFn = print,
) -> PipelineResult:
    """Run download, feature building, backtest, report, and memory recording."""
    catalog = DataCatalog.from_yaml(storage_config)
    storage = ParquetStorage()
    raw_directory = _resolve_dir(raw_dir, catalog.raw_data_dir)
    feature_directory = _resolve_dir(features_dir, catalog.features_dir)
    report_directory = _resolve_dir(
        output_dir,
        catalog.path_for("reports_dir", experiment_name),
    )
    raw_path = raw_directory / "market_data.parquet"
    features_path = feature_directory / "features.parquet"

    _log_step(log, "Pipeline started")
    _log_step(log, f"Raw data path: {raw_path}")
    _log_step(log, f"Feature path: {features_path}")
    _log_step(log, f"Output directory: {report_directory}")

    if skip_download:
        _log_step(log, "Skipping download; using local raw parquet")
        if not storage.exists(raw_path):
            raise FileNotFoundError(f"Raw parquet not found: {raw_path}")
    else:
        if not symbols:
            raise ValueError("--symbols is required when download is enabled")
        _log_step(log, f"Downloading data for {', '.join(symbols)} from {start} to {end}")
        raw_data = YFinanceFetcher().fetch(symbols, start, end)
        storage.save(raw_data, raw_path)
        _log_step(log, f"Saved {len(raw_data)} raw rows")

    if skip_features:
        _log_step(log, "Skipping feature build; using local feature parquet")
        if not storage.exists(features_path):
            raise FileNotFoundError(f"Feature parquet not found: {features_path}")
    else:
        _log_step(log, "Building features")
        feature_config = _load_yaml(features_config)
        raw_data = storage.load(raw_path)
        feature_table = build_feature_table_from_config(raw_data, feature_config)
        storage.save(feature_table, features_path)
        _log_step(log, f"Saved {len(feature_table)} feature rows")

    _log_step(log, f"Running backtest with strategy: {strategy_name}")
    backtest_settings = _load_yaml(backtest_config)
    strategy = _build_strategy(strategy_name, backtest_settings)
    result = BacktestEngine(
        strategy=strategy,
        initial_cash=backtest_settings.get("portfolio", {}).get("initial_cash", 100_000.0),
        commission_model=CommissionModel(
            backtest_settings.get("costs", {}).get("commission_bps", 0.0)
        ),
        slippage_model=SlippageModel(
            backtest_settings.get("costs", {}).get("slippage_bps", 0.0)
        ),
    ).run(storage.load(raw_path))

    _log_step(log, "Saving report artifacts")
    artifacts = save_backtest_report(
        result,
        report_directory,
        title=experiment_name,
        params={
            "symbols": symbols,
            "start": start,
            "end": end,
            "strategy": strategy_name,
            "features_config": str(Path(features_config).expanduser()),
            "backtest_config": str(Path(backtest_config).expanduser()),
            "backtest": backtest_settings,
        },
    )

    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=experiment_name,
        metrics=result.metrics,
        artifacts=artifacts,
        params={
            "symbols": symbols,
            "start": start,
            "end": end,
            "raw_path": str(raw_path),
            "features_path": str(features_path),
            "output_dir": str(report_directory),
            "strategy": strategy_name,
            "skip_download": skip_download,
            "skip_features": skip_features,
        },
    )
    _log_step(log, f"Recorded experiment memory: {memory_path}")
    _log_step(log, "Pipeline completed")

    return PipelineResult(
        raw_path=raw_path,
        features_path=features_path,
        output_dir=report_directory,
        experiment_memory_path=memory_path,
        artifacts=artifacts,
        metrics=result.metrics,
    )


def _build_strategy(strategy_name: str, config: dict[str, Any]) -> Strategy:
    if strategy_name != "ma_cross":
        raise ValueError("Only --strategy ma_cross is supported in this phase")
    strategy_config = config.get("strategy", {})
    configured_name = strategy_config.get("name", "moving_average_cross")
    if configured_name != "moving_average_cross":
        raise ValueError("backtest config must use strategy.name=moving_average_cross")
    return MovingAverageCrossStrategy(
        fast_window=strategy_config.get("fast_window", 5),
        slow_window=strategy_config.get("slow_window", 20),
    )


def _resolve_dir(value: str | Path | None, default: Path) -> Path:
    path = Path(value).expanduser() if value else default
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _log_step(log: LogFn, message: str) -> None:
    log(f"[pipeline] {message}")
