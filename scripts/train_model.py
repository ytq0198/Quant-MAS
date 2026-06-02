"""Train predictive direction models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import yaml

from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.memory import ExperimentMemory
from quant_mas.models import (
    BasePredictiveModel,
    LightGBMDirectionModel,
    evaluate_direction_model,
    prepare_supervised_data,
    split_by_time_with_metadata,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a predictive model.")
    parser.add_argument("--config", default="configs/train.yaml", help="Training config path.")
    parser.add_argument(
        "--storage-config",
        default="configs/storage.yaml",
        help="Storage config path.",
    )
    parser.add_argument(
        "--input",
        help="Input feature parquet path. Defaults to features_dir/features.parquet.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory. Defaults to models/lightgbm_direction_latest.",
    )
    parser.add_argument(
        "--experiment-name",
        default="lightgbm_direction_training",
        help="Experiment name recorded in experiment memory.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    with Path(args.config).expanduser().open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    input_path = (
        Path(args.input).expanduser()
        if args.input
        else DataCatalog.from_yaml(args.storage_config).path_for("features_dir", "features.parquet")
    )
    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else DataCatalog.from_yaml(args.storage_config).path_for("models_dir", "lightgbm_direction_latest")
    )
    result = train_direction_model(
        feature_path=input_path,
        output_dir=output_dir,
        config=config,
        storage_config=Path(args.storage_config).expanduser(),
        experiment_name=args.experiment_name,
    )

    print(f"Saved model artifacts to {output_dir}")
    print(json.dumps(result["metrics"], indent=2))


def train_direction_model(
    *,
    feature_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any],
    storage_config: str | Path,
    experiment_name: str,
    model_factory: Callable[..., BasePredictiveModel] | None = None,
) -> dict[str, Any]:
    """Train a direction model and write Prompt 15 artifacts."""
    model_config = config.get("model", {})
    if model_config.get("name", "lightgbm_direction") != "lightgbm_direction":
        raise ValueError("Only lightgbm_direction is supported in this phase")

    catalog = DataCatalog.from_yaml(storage_config)
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    features = ParquetStorage().load(feature_path)
    features_with_date, target, feature_columns, target_column = prepare_supervised_data(
        features,
        config.get("target", "future_direction"),
    )
    split_config = config.get("split", {})
    feature_splits, target_splits, split_metadata = split_by_time_with_metadata(
        features_with_date,
        target,
        train_ratio=split_config.get("train", 0.7),
        validation_ratio=split_config.get("validation", 0.15),
        test_ratio=split_config.get("test", 0.15),
    )

    params = model_config.get("params", {})
    model_cls = model_factory or LightGBMDirectionModel
    model = model_cls(**params)
    model.fit(feature_splits.train, target_splits.train)

    metrics = {}
    metrics.update(
        evaluate_direction_model(
            model,
            feature_splits.train,
            target_splits.train,
            "train",
            split_metadata["train"],
        )
    )
    metrics.update(
        evaluate_direction_model(
            model,
            feature_splits.validation,
            target_splits.validation,
            "val",
            split_metadata["validation"],
        )
    )
    metrics.update(
        evaluate_direction_model(
            model,
            feature_splits.test,
            target_splits.test,
            "test",
            split_metadata["test"],
        )
    )
    metrics.update(
        {
            "label_column": target_column,
            "feature_count": len(feature_columns),
            "train_ratio": split_config.get("train", 0.7),
            "val_ratio": split_config.get("validation", 0.15),
            "test_ratio": split_config.get("test", 0.15),
        }
    )

    model_path = model.save(output_path / "model.pkl")
    metrics_path = output_path / "metrics.json"
    feature_columns_path = output_path / "feature_columns.json"
    feature_importance_path = output_path / "feature_importance.csv"
    metadata_path = output_path / "metadata.json"

    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    feature_columns_path.write_text(
        json.dumps(feature_columns, indent=2),
        encoding="utf-8",
    )
    feature_importance = model.feature_importance()
    if feature_importance.empty:
        feature_importance = _zero_feature_importance(feature_columns)
    feature_importance.loc[:, ["feature", "importance"]].to_csv(
        feature_importance_path,
        index=False,
    )
    metadata = {
        **model.metadata(),
        "target_column": target_column,
        "split": split_config,
        "split_metadata": {
            name: split.__dict__ for name, split in split_metadata.items()
        },
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    artifacts = {
        "model": model_path,
        "metrics": metrics_path,
        "feature_columns": feature_columns_path,
        "feature_importance": feature_importance_path,
        "metadata": metadata_path,
    }
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=experiment_name,
        metrics=metrics,
        artifacts=artifacts,
        params=config,
    )
    return {
        "metrics": metrics,
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "experiment_memory": str(memory_path),
        "feature_columns": feature_columns,
        "target_column": target_column,
    }


def _zero_feature_importance(feature_columns: list[str]):
    import pandas as pd

    return pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": [0.0] * len(feature_columns),
        }
    )


if __name__ == "__main__":
    main()
