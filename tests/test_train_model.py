from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.models import (
    BasePredictiveModel,
    evaluate_direction_model,
    prepare_supervised_data,
    split_by_time,
)


class ThresholdModel(BasePredictiveModel):
    def __init__(self) -> None:
        self.threshold = 0.0

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "ThresholdModel":
        self.threshold = float(features["return_1"].median())
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return (features["return_1"] >= self.threshold).astype(int)

    def save(self, path: str | Path) -> Path:
        return Path(path)

    @classmethod
    def load(cls, path: str | Path) -> "ThresholdModel":
        return cls()

    def metadata(self) -> dict[str, Any]:
        return {"model_type": "threshold"}


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

    assert set(metrics) == {"test_accuracy", "test_samples", "test_positive_rate"}
    assert metrics["test_samples"] == 3

