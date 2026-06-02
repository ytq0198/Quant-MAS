"""Run a machine-learning signal backtest."""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quant_mas.backtest import (
    BacktestEngine,
    CommissionModel,
    SlippageModel,
    save_backtest_report,
)
from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.memory import ExperimentMemory
from quant_mas.models import BasePredictiveModel, select_feature_columns
from quant_mas.strategies import MLSignalStrategy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ML signal backtest.")
    parser.add_argument("--config", default="configs/backtest_ml.yaml")
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--features-path", help="Override feature parquet path.")
    parser.add_argument("--model-path", help="Override model path.")
    parser.add_argument("--output-dir", help="Override report output directory.")
    parser.add_argument("--experiment-name", help="Override experiment name.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        with Path(args.config).expanduser().open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        result = run_ml_backtest(
            config=config,
            storage_config=Path(args.storage_config).expanduser(),
            features_path=Path(args.features_path).expanduser()
            if args.features_path
            else None,
            model_path=Path(args.model_path).expanduser() if args.model_path else None,
            output_dir=Path(args.output_dir).expanduser() if args.output_dir else None,
            experiment_name=args.experiment_name,
        )
    except Exception as exc:
        print(f"[ml-backtest] ERROR: {exc}", file=sys.stderr)
        return 1

    print("[ml-backtest] Backtest completed")
    print(json.dumps(result["metrics"], indent=2))
    print(f"[ml-backtest] Summary: {result['artifacts']['summary']}")
    return 0


def run_ml_backtest(
    *,
    config: dict[str, Any],
    storage_config: str | Path,
    features_path: str | Path | None = None,
    model_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    experiment_name: str | None = None,
    model: BasePredictiveModel | None = None,
) -> dict[str, Any]:
    """Run ML probability signal backtest and write report artifacts."""
    catalog = DataCatalog.from_yaml(storage_config)
    feature_table_path = _resolve_path(
        features_path,
        _path_from_config(config, "data", "features_path", catalog.path_for("features_dir", "features.parquet")),
    )
    model_file = _resolve_path(
        model_path,
        _path_from_config(config, "model", "path", catalog.path_for("models_dir", "lightgbm_direction_latest", "model.pkl")),
    )
    report_dir = _resolve_path(
        output_dir,
        _path_from_config(config, "output", "dir", catalog.path_for("reports_dir", "ml_backtest_latest")),
    )
    name = experiment_name or config.get("experiment", {}).get("name", "ml_signal_backtest")

    features = ParquetStorage().load(feature_table_path)
    loaded_model = model or _load_model(model_file)
    feature_columns = _resolve_feature_columns(config, loaded_model, features)
    prediction_features = features.loc[:, feature_columns]
    pred_proba = loaded_model.predict_proba(prediction_features)
    predictions = features.loc[:, ["date", "symbol"]].copy()
    predictions["pred_proba"] = pred_proba.to_numpy()

    strategy_config = config.get("strategy", {})
    if strategy_config.get("name", "ml_signal") != "ml_signal":
        raise ValueError("backtest_ml config must use strategy.name=ml_signal")
    strategy = MLSignalStrategy(
        predictions,
        buy_threshold=strategy_config.get("buy_threshold", 0.6),
        sell_threshold=strategy_config.get("sell_threshold", 0.4),
        max_weight=strategy_config.get("max_weight", 1.0),
    )
    backtest_result = BacktestEngine(
        strategy=strategy,
        initial_cash=config.get("portfolio", {}).get("initial_cash", 100_000.0),
        commission_model=CommissionModel(config.get("costs", {}).get("commission_bps", 0.0)),
        slippage_model=SlippageModel(config.get("costs", {}).get("slippage_bps", 0.0)),
    ).run(features)
    artifacts = save_backtest_report(
        backtest_result,
        report_dir,
        title=name,
        params={
            "strategy": strategy_config,
            "features_path": str(feature_table_path),
            "model_path": str(model_file),
            "feature_columns": feature_columns,
        },
    )
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=name,
        metrics=backtest_result.metrics,
        artifacts=artifacts,
        params={
            "config": config,
            "features_path": str(feature_table_path),
            "model_path": str(model_file),
            "feature_columns": feature_columns,
        },
    )
    return {
        "metrics": backtest_result.metrics,
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "experiment_memory": str(memory_path),
        "feature_columns": feature_columns,
    }


def _load_model(path: Path) -> BasePredictiveModel:
    with path.expanduser().open("rb") as file:
        model = pickle.load(file)
    if not hasattr(model, "predict_proba"):
        raise TypeError("Loaded model must provide predict_proba(features)")
    return model


def _resolve_feature_columns(
    config: dict[str, Any],
    model: BasePredictiveModel,
    features: pd.DataFrame,
) -> list[str]:
    configured_path = config.get("model", {}).get("feature_columns_path")
    if configured_path and Path(configured_path).expanduser().exists():
        columns = json.loads(Path(configured_path).expanduser().read_text(encoding="utf-8"))
    else:
        columns = model.metadata().get("feature_columns", [])
    if not columns:
        target = config.get("target", "future_direction")
        target_column = target if target in features.columns else "__missing_target__"
        columns = select_feature_columns(features, target_column)
    forbidden = [
        column
        for column in columns
        if column in {"date", "symbol"}
        or column.startswith("future_return")
        or column.startswith("future_direction")
    ]
    if forbidden:
        raise ValueError(f"Forbidden columns in ML features: {forbidden}")
    missing = [column for column in columns if column not in features.columns]
    if missing:
        raise ValueError(f"Feature columns missing from feature table: {missing}")
    return list(columns)


def _resolve_path(value: str | Path | None, default: Path) -> Path:
    return Path(value).expanduser() if value is not None else default.expanduser()


def _path_from_config(
    config: dict[str, Any],
    section: str,
    key: str,
    default: Path,
) -> Path:
    value = config.get(section, {}).get(key)
    return Path(value).expanduser() if value else default


if __name__ == "__main__":
    raise SystemExit(main())

