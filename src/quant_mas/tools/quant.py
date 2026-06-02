"""Quant tools exposed to agents."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from shutil import copyfile
from typing import Any

import pandas as pd
import yaml

from quant_mas.backtest import (
    BacktestEngine,
    CommissionModel,
    SlippageModel,
    save_backtest_report,
)
from quant_mas.data import DataCatalog, ParquetStorage, validate_ohlcv
from quant_mas.memory import ExperimentMemory
from quant_mas.models import (
    BasePredictiveModel,
    LightGBMDirectionModel,
    evaluate_direction_model,
    prepare_supervised_data,
    split_by_time,
)
from quant_mas.strategies import MovingAverageCrossStrategy
from quant_mas.tools.base import BaseTool, ToolResult


class DataSummaryTool(BaseTool):
    """Summarize a parquet data file without returning the full data."""

    def __init__(self) -> None:
        super().__init__(
            name="data_summary",
            description="Summarize OHLCV parquet data by rows, symbols, and date range.",
        )

    def run(self, **kwargs: Any) -> ToolResult:
        path = Path(kwargs["path"]).expanduser()
        frame = ParquetStorage().load(path)
        summary = _summarize_frame(frame)
        return ToolResult(
            content=(
                f"Data summary for {path}: {summary['rows']} rows, "
                f"{summary['symbol_count']} symbols, "
                f"{summary['start_date']} to {summary['end_date']}."
            ),
            metadata={"path": str(path), **summary},
        )


class BacktestTool(BaseTool):
    """Run a deterministic backtest and return artifact paths."""

    def __init__(self) -> None:
        super().__init__(
            name="backtest",
            description="Run moving-average cross backtest and save report artifacts.",
        )

    def run(self, **kwargs: Any) -> ToolResult:
        config_path = kwargs.get("config_path", "configs/backtest.yaml")
        storage_config = kwargs.get("storage_config", "configs/storage.yaml")
        config = _load_yaml(config_path)
        catalog = DataCatalog.from_yaml(storage_config)
        input_path = _resolve_optional_path(
            kwargs.get("input_path"),
            catalog.path_for("raw_data_dir", "market_data.parquet"),
        )
        output_dir = _resolve_optional_path(
            kwargs.get("output_dir"),
            catalog.path_for("reports_dir", "backtest_latest"),
        )
        experiment_name = kwargs.get("experiment_name", "moving_average_cross_backtest")

        strategy_config = config.get("strategy", {})
        if strategy_config.get("name", "moving_average_cross") != "moving_average_cross":
            raise ValueError("Only moving_average_cross is supported")

        strategy = MovingAverageCrossStrategy(
            fast_window=strategy_config.get("fast_window", 5),
            slow_window=strategy_config.get("slow_window", 20),
        )
        engine = BacktestEngine(
            strategy=strategy,
            initial_cash=config.get("portfolio", {}).get("initial_cash", 100_000.0),
            commission_model=CommissionModel(
                config.get("costs", {}).get("commission_bps", 0.0)
            ),
            slippage_model=SlippageModel(config.get("costs", {}).get("slippage_bps", 0.0)),
        )
        result = engine.run(ParquetStorage().load(input_path))
        artifacts = save_backtest_report(
            result,
            output_dir,
            title=experiment_name,
            params=config,
        )
        memory_path = catalog.path_for("reports_dir", "experiments.json")
        ExperimentMemory(memory_path).add(
            name=experiment_name,
            metrics=result.metrics,
            artifacts=artifacts,
            params=config,
        )

        artifact_strings = _stringify_paths(artifacts)
        return ToolResult(
            content=(
                f"Backtest completed. total_return={result.metrics['total_return']:.6g}, "
                f"sharpe={result.metrics['sharpe']:.6g}, "
                f"max_drawdown={result.metrics['max_drawdown']:.6g}. "
                f"Summary: {artifact_strings['summary']}"
            ),
            metadata={
                "metrics": result.metrics,
                "artifacts": artifact_strings,
                "experiment_memory": str(memory_path),
            },
        )


class TrainModelTool(BaseTool):
    """Train a direction model and return metrics plus artifact paths."""

    def __init__(
        self,
        model_factory: Callable[..., BasePredictiveModel] | None = None,
    ) -> None:
        super().__init__(
            name="train_model",
            description="Train a time-split direction model and save artifacts.",
        )
        self.model_factory = model_factory or LightGBMDirectionModel

    def run(self, **kwargs: Any) -> ToolResult:
        config_path = kwargs.get("config_path", "configs/train.yaml")
        storage_config = kwargs.get("storage_config", "configs/storage.yaml")
        config = _load_yaml(config_path)
        catalog = DataCatalog.from_yaml(storage_config)
        input_path = _resolve_optional_path(
            kwargs.get("input_path"),
            catalog.path_for("features_dir", "features.parquet"),
        )
        output_dir = _resolve_optional_path(
            kwargs.get("output_dir"),
            catalog.path_for("models_dir", "lightgbm_direction_latest"),
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        experiment_name = kwargs.get("experiment_name", "lightgbm_direction_training")

        features = ParquetStorage().load(input_path)
        features_with_date, target, feature_columns, target_column = prepare_supervised_data(
            features,
            config.get("target", "future_direction"),
        )
        split_config = config.get("split", {})
        feature_splits, target_splits = split_by_time(
            features_with_date,
            target,
            train_ratio=split_config.get("train", 0.7),
            validation_ratio=split_config.get("validation", 0.15),
            test_ratio=split_config.get("test", 0.15),
        )

        params = config.get("model", {}).get("params", {})
        model = self.model_factory(**params)
        model.fit(feature_splits.train, target_splits.train)

        metrics = {}
        for split_name, split_features, split_target in (
            ("train", feature_splits.train, target_splits.train),
            ("validation", feature_splits.validation, target_splits.validation),
            ("test", feature_splits.test, target_splits.test),
        ):
            metrics.update(
                evaluate_direction_model(model, split_features, split_target, split_name)
            )

        artifacts = _save_model_artifacts(
            model=model,
            output_dir=output_dir,
            metrics=metrics,
            feature_columns=feature_columns,
            target_column=target_column,
            split_config=split_config,
        )
        memory_path = catalog.path_for("reports_dir", "experiments.json")
        ExperimentMemory(memory_path).add(
            name=experiment_name,
            metrics=metrics,
            artifacts=artifacts,
            params=config,
        )
        artifact_strings = _stringify_paths(artifacts)
        return ToolResult(
            content=(
                f"Model training completed. test_accuracy="
                f"{metrics.get('test_accuracy', 0.0):.6g}. "
                f"Model: {artifact_strings['model']}"
            ),
            metadata={
                "metrics": metrics,
                "artifacts": artifact_strings,
                "feature_columns": feature_columns,
                "target_column": target_column,
                "experiment_memory": str(memory_path),
            },
        )


class ReportTool(BaseTool):
    """Return or copy the latest markdown report summary."""

    def __init__(self) -> None:
        super().__init__(
            name="report",
            description="Locate the latest experiment report summary.",
        )

    def run(self, **kwargs: Any) -> ToolResult:
        storage_config = kwargs.get("storage_config", "configs/storage.yaml")
        catalog = DataCatalog.from_yaml(storage_config)
        memory_path = _resolve_optional_path(
            kwargs.get("memory_path"),
            catalog.path_for("reports_dir", "experiments.json"),
        )
        latest = ExperimentMemory(memory_path).latest()
        summary_path = Path(latest.artifacts.get("summary", "")).expanduser()
        if not summary_path.exists():
            raise FileNotFoundError(f"Report summary not found: {summary_path}")

        output_path = kwargs.get("output_path")
        if output_path:
            target = Path(output_path).expanduser()
            target.parent.mkdir(parents=True, exist_ok=True)
            copyfile(summary_path, target)
            summary_path = target

        preview = _preview_text(summary_path)
        return ToolResult(
            content=f"Latest report: {summary_path}\n{preview}",
            metadata={
                "experiment_id": latest.experiment_id,
                "experiment_name": latest.name,
                "summary": str(summary_path),
                "experiment_memory": str(memory_path),
            },
        )


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _resolve_optional_path(value: str | Path | None, default: Path) -> Path:
    return Path(value).expanduser() if value is not None else default


def _summarize_frame(frame: pd.DataFrame) -> dict[str, Any]:
    summary = {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
    }
    if {"date", "symbol", "open", "high", "low", "close", "volume"}.issubset(
        frame.columns
    ):
        validated = validate_ohlcv(frame)
        summary.update(
            {
                "symbols": sorted(validated["symbol"].unique().tolist()),
                "symbol_count": int(validated["symbol"].nunique()),
                "start_date": str(validated["date"].min().date()),
                "end_date": str(validated["date"].max().date()),
            }
        )
    else:
        summary.update(
            {
                "symbols": [],
                "symbol_count": 0,
                "start_date": "",
                "end_date": "",
            }
        )
    return summary


def _save_model_artifacts(
    *,
    model: BasePredictiveModel,
    output_dir: Path,
    metrics: dict[str, Any],
    feature_columns: list[str],
    target_column: str,
    split_config: dict[str, Any],
) -> dict[str, Path]:
    model_path = model.save(output_dir / "model.pkl")
    metrics_path = output_dir / "metrics.json"
    feature_columns_path = output_dir / "feature_columns.json"
    metadata_path = output_dir / "metadata.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    feature_columns_path.write_text(
        json.dumps(feature_columns, indent=2),
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(
            {
                **model.metadata(),
                "target_column": target_column,
                "split": split_config,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return {
        "model": model_path,
        "metrics": metrics_path,
        "feature_columns": feature_columns_path,
        "metadata": metadata_path,
    }


def _stringify_paths(paths: dict[str, Path]) -> dict[str, str]:
    return {key: str(value) for key, value in paths.items()}


def _preview_text(path: Path, max_lines: int = 20) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:max_lines])

