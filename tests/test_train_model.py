from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from scripts.train_model import train_direction_model
from quant_mas.models import (
    BasePredictiveModel,
    evaluate_direction_model,
    prepare_supervised_data,
    split_by_time,
)
from quant_mas.memory import ExperimentMemory
from quant_mas.utils import ResolvedDevice


class ThresholdModel(BasePredictiveModel):
    def __init__(self) -> None:
        self.threshold = 0.0
        self.feature_columns: list[str] = []

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "ThresholdModel":
        self.feature_columns = list(features.columns)
        self.threshold = float(features["return_1"].median())
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return (features["return_1"] >= self.threshold).astype(int)

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        values = features["return_1"].astype(float)
        minimum = values.min()
        maximum = values.max()
        if maximum == minimum:
            return pd.Series([0.5] * len(values), index=features.index)
        return (values - minimum) / (maximum - minimum)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("threshold model", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "ThresholdModel":
        return cls()

    def metadata(self) -> dict[str, Any]:
        return {"model_type": "threshold", "feature_columns": self.feature_columns}

    def feature_importance(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "feature": self.feature_columns,
                "importance": list(range(len(self.feature_columns), 0, -1)),
            }
        )


def make_features() -> pd.DataFrame:
    rows = []
    for index in range(20):
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "close": 10.0 + index,
                "return_1": index / 100.0,
                "ma_5": 10.0 + index / 2.0,
                "future_return_5": 0.01 if index % 2 else -0.01,
                "future_direction_5": 1 if index % 2 else 0,
            }
        )
    return pd.DataFrame(rows)


def test_prepare_supervised_data_excludes_labels_and_identifiers() -> None:
    dated_features, target, feature_columns, target_column = prepare_supervised_data(
        make_features(),
        "future_direction",
    )

    assert target_column == "future_direction_5"
    assert "future_direction_5" not in feature_columns
    assert "future_return_5" not in feature_columns
    assert "date" not in feature_columns
    assert "symbol" not in feature_columns
    assert feature_columns == ["close", "return_1", "ma_5"]
    assert "date" in dated_features.columns
    assert target.tolist()[:3] == [0, 1, 0]


def test_split_by_time_uses_chronological_order() -> None:
    dated_features, target, _, _ = prepare_supervised_data(
        make_features(),
        "future_direction",
    )

    feature_splits, target_splits = split_by_time(dated_features, target)

    assert len(feature_splits.train) == 14
    assert len(feature_splits.validation) == 3
    assert len(feature_splits.test) == 3
    assert target_splits.train.tolist() == target.iloc[:14].tolist()
    assert target_splits.validation.tolist() == target.iloc[14:17].tolist()
    assert target_splits.test.tolist() == target.iloc[17:].tolist()


def test_evaluate_direction_model_returns_metrics() -> None:
    dated_features, target, _, _ = prepare_supervised_data(
        make_features(),
        "future_direction",
    )
    feature_splits, target_splits = split_by_time(dated_features, target)
    model = ThresholdModel().fit(feature_splits.train, target_splits.train)

    metrics = evaluate_direction_model(
        model,
        feature_splits.test,
        target_splits.test,
        "test",
    )

    assert {
        "test_accuracy",
        "test_auc",
        "test_samples",
        "test_positive_rate",
    }.issubset(metrics)
    assert metrics["test_samples"] == 3


def test_train_direction_model_writes_prompt_15_artifacts(tmp_path) -> None:
    feature_path = tmp_path / "features.parquet"
    output_dir = tmp_path / "models" / "threshold"
    storage_config = tmp_path / "storage.yaml"
    make_features().to_parquet(feature_path, index=False)
    storage_config.write_text(
        "\n".join(
            [
                "project_root: .",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    config = {
        "model": {"name": "lightgbm_direction", "device": "cpu", "params": {}},
        "split": {"train": 0.7, "validation": 0.15, "test": 0.15},
        "target": "future_direction",
    }

    result = train_direction_model(
        feature_path=feature_path,
        output_dir=output_dir,
        config=config,
        storage_config=storage_config,
        experiment_name="synthetic_threshold_training",
        model_factory=ThresholdModel,
    )

    metrics_path = Path(result["artifacts"]["metrics"])
    importance_path = Path(result["artifacts"]["feature_importance"])
    model_path = Path(result["artifacts"]["model"])
    metadata_path = Path(result["artifacts"]["metadata"])
    memory_path = Path(result["experiment_memory"])

    assert metrics_path.exists()
    assert importance_path.exists()
    assert model_path.exists()
    assert metadata_path.exists()
    assert memory_path.exists()

    metrics = pd.io.json.read_json(metrics_path, typ="series").to_dict()
    for key in (
        "train_accuracy",
        "train_auc",
        "train_start_date",
        "train_end_date",
        "train_samples",
        "val_accuracy",
        "val_auc",
        "val_start_date",
        "val_end_date",
        "val_samples",
        "test_accuracy",
        "test_auc",
        "test_start_date",
        "test_end_date",
        "test_samples",
        "label_column",
        "feature_count",
    ):
        assert key in metrics
    assert metrics["label_column"] == "future_direction_5"
    assert metrics["feature_count"] == 3

    feature_importance = pd.read_csv(importance_path)
    assert list(feature_importance.columns) == ["feature", "importance"]
    assert "future_direction_5" not in feature_importance["feature"].tolist()
    assert "future_return_5" not in feature_importance["feature"].tolist()
    assert "date" not in feature_importance["feature"].tolist()
    assert "symbol" not in feature_importance["feature"].tolist()

    latest = ExperimentMemory(memory_path).latest()
    assert latest.name == "synthetic_threshold_training"
    assert latest.metrics["feature_count"] == 3
    assert "feature_importance" in latest.artifacts


def test_train_direction_model_writes_device_fields_with_mock_resolution(
    tmp_path,
    monkeypatch,
) -> None:
    feature_path = tmp_path / "features.parquet"
    output_dir = tmp_path / "models" / "threshold"
    storage_config = tmp_path / "storage.yaml"
    make_features().to_parquet(feature_path, index=False)
    storage_config.write_text(
        "\n".join(
            [
                "project_root: .",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    config = {
        "model": {"name": "lightgbm_direction", "device": "auto", "params": {}},
        "split": {"train": 0.7, "validation": 0.15, "test": 0.15},
        "target": "future_direction",
    }

    monkeypatch.setattr(
        "scripts.train_model.resolve_training_device",
        lambda requested: ResolvedDevice(
            requested=requested,
            resolved="cuda",
            fallback=False,
            reason=None,
        ),
    )

    result = train_direction_model(
        feature_path=feature_path,
        output_dir=output_dir,
        config=config,
        storage_config=storage_config,
        experiment_name="synthetic_cuda_training",
        model_factory=ThresholdModel,
        device="cuda",
    )

    metrics = pd.io.json.read_json(
        Path(result["artifacts"]["metrics"]),
        typ="series",
    ).to_dict()
    metadata = pd.io.json.read_json(
        Path(result["artifacts"]["metadata"]),
        typ="series",
    ).to_dict()

    assert metrics["device_requested"] == "cuda"
    assert metrics["device_resolved"] == "cuda"
    assert metrics["device_fallback"] is False
    assert metadata["device_requested"] == "cuda"
    assert metadata["device_resolved"] == "cuda"
