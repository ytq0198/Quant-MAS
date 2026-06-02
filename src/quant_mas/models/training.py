"""Training helpers for time-series predictive models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from quant_mas.models.base import BasePredictiveModel


IDENTIFIER_COLUMNS = {"date", "symbol"}
LABEL_PREFIXES = ("future_return", "future_direction")


@dataclass(frozen=True)
class DatasetSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def resolve_target_column(frame: pd.DataFrame, target: str) -> str:
    """Resolve exact target name or a unique label-prefix match."""
    if target in frame.columns:
        return target
    matches = [column for column in frame.columns if column.startswith(f"{target}_")]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise KeyError(f"Target column not found: {target}")
    raise ValueError(f"Ambiguous target column {target!r}: {matches}")


def select_feature_columns(frame: pd.DataFrame, target_column: str) -> list[str]:
    """Select numeric feature columns and exclude labels/identifiers."""
    excluded = set(IDENTIFIER_COLUMNS)
    excluded.add(target_column)
    excluded.update(
        column
        for column in frame.columns
        if column.startswith(LABEL_PREFIXES)
    )
    return [
        column
        for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]


def prepare_supervised_data(
    frame: pd.DataFrame,
    target: str,
) -> tuple[pd.DataFrame, pd.Series, list[str], str]:
    target_column = resolve_target_column(frame, target)
    feature_columns = select_feature_columns(frame, target_column)
    if not feature_columns:
        raise ValueError("No numeric feature columns available for training")

    required_columns = ["date", target_column, *feature_columns]
    data = frame.loc[:, required_columns].copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise")
    data = data.dropna(subset=[target_column, *feature_columns])
    data = data.sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError("No rows remain after dropping missing features/target")

    features = data.loc[:, feature_columns]
    target_series = data[target_column].astype(int)
    target_series.name = target_column
    dated = data.loc[:, ["date"]].join(features)
    return dated, target_series, feature_columns, target_column


def split_by_time(
    features_with_date: pd.DataFrame,
    target: pd.Series,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> tuple[DatasetSplit, DatasetSplit]:
    """Split by chronological unique dates, never randomly."""
    total_ratio = train_ratio + validation_ratio + test_ratio
    if abs(total_ratio - 1.0) > 1e-9:
        raise ValueError("Split ratios must sum to 1.0")

    dates = pd.Index(features_with_date["date"].drop_duplicates().sort_values())
    if len(dates) < 3:
        raise ValueError("At least 3 unique dates are required for train/validation/test")

    train_end = max(1, int(len(dates) * train_ratio))
    validation_end = max(train_end + 1, int(len(dates) * (train_ratio + validation_ratio)))
    validation_end = min(validation_end, len(dates) - 1)

    train_dates = dates[:train_end]
    validation_dates = dates[train_end:validation_end]
    test_dates = dates[validation_end:]
    if len(validation_dates) == 0 or len(test_dates) == 0:
        raise ValueError("Split ratios produced an empty validation or test split")

    masks = {
        "train": features_with_date["date"].isin(train_dates),
        "validation": features_with_date["date"].isin(validation_dates),
        "test": features_with_date["date"].isin(test_dates),
    }
    feature_splits = DatasetSplit(
        train=features_with_date.loc[masks["train"]].drop(columns=["date"]),
        validation=features_with_date.loc[masks["validation"]].drop(columns=["date"]),
        test=features_with_date.loc[masks["test"]].drop(columns=["date"]),
    )
    target_splits = DatasetSplit(
        train=target.loc[masks["train"]].reset_index(drop=True),
        validation=target.loc[masks["validation"]].reset_index(drop=True),
        test=target.loc[masks["test"]].reset_index(drop=True),
    )
    feature_splits = DatasetSplit(
        train=feature_splits.train.reset_index(drop=True),
        validation=feature_splits.validation.reset_index(drop=True),
        test=feature_splits.test.reset_index(drop=True),
    )
    return feature_splits, target_splits


def evaluate_direction_model(
    model: BasePredictiveModel,
    features: pd.DataFrame,
    target: pd.Series,
    prefix: str,
) -> dict[str, Any]:
    predictions = model.predict(features).astype(int)
    truth = target.astype(int).reset_index(drop=True)
    predictions = predictions.reset_index(drop=True)
    accuracy = float((predictions == truth).mean())
    return {
        f"{prefix}_accuracy": accuracy,
        f"{prefix}_samples": int(len(truth)),
        f"{prefix}_positive_rate": float(predictions.mean()) if len(predictions) else 0.0,
    }

