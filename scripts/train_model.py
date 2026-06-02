"""Train predictive direction models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.memory import ExperimentMemory
from quant_mas.models import (
    LightGBMDirectionModel,
    evaluate_direction_model,
    prepare_supervised_data,
    split_by_time,
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

    catalog = DataCatalog.from_yaml(args.storage_config)
    input_path = (
        Path(args.input).expanduser()
        if args.input
        else catalog.path_for("features_dir", "features.parquet")
    )
    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else catalog.path_for("models_dir", "lightgbm_direction_latest")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    model_config = config.get("model", {})
    if model_config.get("name", "lightgbm_direction") != "lightgbm_direction":
        raise ValueError("Only lightgbm_direction is supported in this phase")

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

    params = model_config.get("params", {})
    model = LightGBMDirectionModel(**params)
    model.fit(feature_splits.train, target_splits.train)

    metrics = {}
    metrics.update(
        evaluate_direction_model(
            model,
            feature_splits.train,
            target_splits.train,
            "train",
        )
    )
    metrics.update(
        evaluate_direction_model(
            model,
            feature_splits.validation,
            target_splits.validation,
            "validation",
        )
    )
    metrics.update(
        evaluate_direction_model(
            model,
            feature_splits.test,
            target_splits.test,
            "test",
        )
    )

    model_path = model.save(output_dir / "model.pkl")
    metrics_path = output_dir / "metrics.json"
    features_path = output_dir / "feature_columns.json"
    metadata_path = output_dir / "metadata.json"

    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    features_path.write_text(
        json.dumps(feature_columns, indent=2),
        encoding="utf-8",
    )
    metadata = {
        **model.metadata(),
        "target_column": target_column,
        "split": split_config,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    artifacts = {
        "model": model_path,
        "metrics": metrics_path,
        "feature_columns": features_path,
        "metadata": metadata_path,
    }
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=args.experiment_name,
        metrics=metrics,
        artifacts=artifacts,
        params=config,
    )

    print(f"Saved model artifacts to {output_dir}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
