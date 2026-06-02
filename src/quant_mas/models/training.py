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


@dataclass(frozen=True)
class SplitMetadata:
    """Date range and sample counts for one chronological split."""

    start_date: str
    end_date: str
    samples: int


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


def split_by_time_with_metadata(
    features_with_date: pd.DataFrame,
    target: pd.Series,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> tuple[DatasetSplit, DatasetSplit, dict[str, SplitMetadata]]:
    """Split by time and return split date ranges."""
    feature_splits, target_splits = split_by_time(
        features_with_date,
        target,
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
    )
    dates = pd.to_datetime(features_with_date["date"]).reset_index(drop=True)
    lengths = {
        "train": len(feature_splits.train),
        "validation": len(feature_splits.validation),
        "test": len(feature_splits.test),
    }
    offsets = {
        "train": 0,
        "validation": lengths["train"],
        "test": lengths["train"] + lengths["validation"],
    }
    metadata = {
        split_name: _metadata_for_dates(
            dates.iloc[offsets[split_name] : offsets[split_name] + lengths[split_name]]
        )
        for split_name in ("train", "validation", "test")
    }
    return feature_splits, target_splits, metadata


def evaluate_direction_model(
    model: BasePredictiveModel,
    features: pd.DataFrame,
    target: pd.Series,
    prefix: str,
    split_metadata: SplitMetadata | None = None,
) -> dict[str, Any]:
    predictions = model.predict(features).astype(int)
    truth = target.astype(int).reset_index(drop=True)
    predictions = predictions.reset_index(drop=True)
    probabilities = model.predict_proba(features).reset_index(drop=True)
    accuracy = float((predictions == truth).mean())
    metrics = {
        f"{prefix}_accuracy": accuracy,
        f"{prefix}_auc": _safe_auc(truth, probabilities),
        f"{prefix}_samples": int(len(truth)),
        f"{prefix}_positive_rate": float(predictions.mean()) if len(predictions) else 0.0,
    }
    if split_metadata is not None:
        metrics[f"{prefix}_start_date"] = split_metadata.start_date
        metrics[f"{prefix}_end_date"] = split_metadata.end_date
    return metrics


def _metadata_for_dates(dates: pd.Series) -> SplitMetadata:
    return SplitMetadata(
        start_date=str(dates.min().date()),
        end_date=str(dates.max().date()),
        samples=int(len(dates)),
    )


def _safe_auc(truth: pd.Series, probabilities: pd.Series) -> float | None:
    if truth.nunique() < 2:
        return None
    ranked = probabilities.rank(method="average")
    positive = truth == 1
    negative = truth == 0
    positive_count = int(positive.sum())
    negative_count = int(negative.sum())
    if positive_count == 0 or negative_count == 0:
        return None
    positive_rank_sum = float(ranked[positive].sum())
    auc = (
        positive_rank_sum - positive_count * (positive_count + 1) / 2
    ) / (positive_count * negative_count)
    return float(auc)
