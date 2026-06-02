from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.backtest import (
    build_walk_forward_windows,
    run_walk_forward,
    run_walk_forward_from_config,
)
from quant_mas.models import BasePredictiveModel


class RecordingThresholdModel(BasePredictiveModel):
    fit_columns: list[list[str]] = []
    fit_lengths: list[int] = []

    def __init__(self) -> None:
        self.threshold = 0.0
        self.feature_columns: list[str] = []

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "RecordingThresholdModel":
        self.feature_columns = list(features.columns)
        self.threshold = float(features["signal_feature"].median())
        RecordingThresholdModel.fit_columns.append(self.feature_columns)
        RecordingThresholdModel.fit_lengths.append(len(features))
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return (self.predict_proba(features) >= 0.5).astype(int)

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        values = features["signal_feature"].astype(float)
        minimum = float(values.min())
        maximum = float(values.max())
        if maximum == minimum:
            return pd.Series([0.5] * len(values), index=features.index)
        return (values - minimum) / (maximum - minimum)

    def save(self, path: str | Path) -> Path:
        return Path(path)

    @classmethod
    def load(cls, path: str | Path) -> "RecordingThresholdModel":
        return cls()

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "recording_threshold",
            "feature_columns": self.feature_columns,
        }


def make_walk_forward_features(days: int = 36) -> pd.DataFrame:
    rows = []
    for index in range(days):
        close = 20.0 + index * 0.5 + (index % 3) * 0.1
        signal = index / days
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close + 0.2,
                "volume": 1000 + index,
                "signal_feature": signal,
                "noise_feature": (index % 5) / 10.0,
                "future_return_5": 0.01 if index % 2 else -0.01,
                "future_direction_5": 1 if index % 2 else 0,
            }
        )
    return pd.DataFrame(rows)


def write_storage_config(tmp_path: Path) -> Path:
    path = tmp_path / "storage.yaml"
    path.write_text(
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
    return path


def walk_forward_config(output_dir: Path | None = None) -> dict[str, Any]:
    config: dict[str, Any] = {
        "model": {"name": "lightgbm_direction", "device": "cpu", "params": {}},
        "target": "future_direction",
        "walk_forward": {
            "train_window": 12,
            "validation_window": 4,
            "test_window": 4,
            "oos_window": 4,
            "step": 4,
            "max_windows": 2,
        },
        "strategy": {
            "name": "ml_signal",
            "buy_threshold": 0.55,
            "sell_threshold": 0.45,
            "max_weight": 1.0,
        },
        "portfolio": {"initial_cash": 1000},
        "costs": {"commission_bps": 0, "slippage_bps": 0},
        "experiment": {"name": "synthetic_walk_forward"},
    }
    if output_dir is not None:
        config["output"] = {"dir": str(output_dir)}
    return config


def test_build_walk_forward_windows_are_chronological() -> None:
    dates = pd.date_range("2026-01-01", periods=30)

    windows = build_walk_forward_windows(
        pd.Series(dates),
        train_window=10,
        validation_window=3,
        test_window=3,
        oos_window=4,
        step=4,
        max_windows=2,
    )

    assert len(windows) == 2
    first = windows[0]
    assert first.train_dates.max() < first.validation_dates.min()
    assert first.validation_dates.max() < first.test_dates.min()
    assert first.test_dates.max() < first.oos_dates.min()
    assert windows[1].train_dates.min() == dates[4]


def test_run_walk_forward_uses_train_only_and_reports_oos_metrics() -> None:
    RecordingThresholdModel.fit_columns = []
    RecordingThresholdModel.fit_lengths = []

    result = run_walk_forward(
        make_walk_forward_features(),
        config=walk_forward_config(),
        model_factory=RecordingThresholdModel,
    )

    assert set(result.metrics) >= {"summary", "train", "val", "test", "oos"}
    assert result.metrics["summary"]["window_count"] == 2
    assert result.metrics["summary"]["target_column"] == "future_direction_5"
    assert result.metrics["oos"]["samples"] == 8
    assert "total_return" in result.metrics["oos"]
    assert "sharpe" in result.metrics["oos"]
    assert "max_drawdown" in result.metrics["oos"]
    assert "future_direction_5" not in result.feature_columns
    assert "future_return_5" not in result.feature_columns
    assert RecordingThresholdModel.fit_lengths == [12, 12]
    for columns in RecordingThresholdModel.fit_columns:
        assert "date" not in columns
        assert "symbol" not in columns
        assert not any(column.startswith("future_") for column in columns)

    for row in result.windows.to_dict(orient="records"):
        assert pd.Timestamp(row["train_end_date"]) < pd.Timestamp(row["validation_start_date"])
        assert pd.Timestamp(row["validation_end_date"]) < pd.Timestamp(row["test_start_date"])
        assert pd.Timestamp(row["test_end_date"]) < pd.Timestamp(row["oos_start_date"])


def test_run_walk_forward_from_config_writes_report_and_memory(tmp_path: Path) -> None:
    feature_path = tmp_path / "features.parquet"
    output_dir = tmp_path / "reports" / "walk_forward"
    storage_config = write_storage_config(tmp_path)
    make_walk_forward_features().to_parquet(feature_path, index=False)
    config = walk_forward_config(output_dir)
    config["data"] = {"features_path": str(feature_path)}

    result = run_walk_forward_from_config(
        config=config,
        storage_config=storage_config,
        model_factory=RecordingThresholdModel,
    )

    artifacts = {key: Path(value) for key, value in result["artifacts"].items()}
    for key in ("metrics", "windows", "oos_equity_curve", "oos_trades", "summary"):
        assert artifacts[key].exists()
    metrics = json.loads(artifacts["metrics"].read_text(encoding="utf-8"))
    assert set(metrics) >= {"summary", "train", "val", "test", "oos"}
    assert metrics["summary"]["window_count"] == 2
    assert Path(result["experiment_memory"]).exists()
