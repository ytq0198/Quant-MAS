from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from quant_mas.backtest import BacktestEngine
from quant_mas.models import BasePredictiveModel
from quant_mas.strategies import MLSignalStrategy
from scripts.run_ml_backtest import run_ml_backtest


class MockProbabilityModel(BasePredictiveModel):
    def __init__(self, feature_columns: list[str] | None = None) -> None:
        self.feature_columns = feature_columns or ["return_1", "ma_3"]

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "MockProbabilityModel":
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return (self.predict_proba(features) >= 0.6).astype(int)

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        values = features["return_1"].astype(float)
        minimum = values.min()
        maximum = values.max()
        if minimum == maximum:
            return pd.Series([0.5] * len(values), index=features.index)
        return (values - minimum) / (maximum - minimum)

    def save(self, path: str | Path) -> Path:
        return Path(path)

    @classmethod
    def load(cls, path: str | Path) -> "MockProbabilityModel":
        return cls()

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "mock_probability",
            "feature_columns": self.feature_columns,
        }


def make_feature_table() -> pd.DataFrame:
    rows = []
    closes = [10, 10, 10, 20, 40, 50, 45, 48]
    returns = [0.0, 0.1, 0.2, 0.9, 1.0, 0.2, 0.1, 0.0]
    for index, (close, return_1) in enumerate(zip(closes, returns, strict=True)):
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
                "return_1": return_1,
                "ma_3": close / 2.0,
                "future_return_1": 0.01,
                "future_direction_1": 1,
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


def test_ml_signal_strategy_converts_probabilities_to_weights() -> None:
    predictions = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=5),
            "symbol": ["AAA"] * 5,
            "pred_proba": [0.2, 0.7, 0.5, 0.3, 0.8],
        }
    )
    strategy = MLSignalStrategy(
        predictions,
        buy_threshold=0.6,
        sell_threshold=0.4,
        max_weight=0.8,
    )

    signals = strategy.generate_signals(make_feature_table().iloc[:5])

    assert signals["signal"].tolist() == [-1, 1, 0, -1, 1]
    assert signals["target_weight"].tolist() == [0.0, 0.8, 0.8, 0.0, 0.8]
    assert "pred_proba" in signals.columns


def test_ml_backtest_keeps_next_bar_execution() -> None:
    data = make_feature_table().iloc[:5].copy()
    predictions = pd.DataFrame(
        {
            "date": data["date"],
            "symbol": data["symbol"],
            "pred_proba": [0.2, 0.2, 0.7, 0.7, 0.7],
        }
    )
    strategy = MLSignalStrategy(predictions, buy_threshold=0.6, sell_threshold=0.4)

    result = BacktestEngine(strategy=strategy, initial_cash=100.0).run(data)

    assert len(result.trades) == 1
    assert result.trades.loc[0, "date"] == pd.Timestamp("2026-01-04")


def test_run_ml_backtest_with_mock_model_writes_report(tmp_path) -> None:
    features_path = tmp_path / "features.parquet"
    output_dir = tmp_path / "reports" / "ml"
    storage_config = write_storage_config(tmp_path)
    make_feature_table().to_parquet(features_path, index=False)
    config = {
        "model": {"path": str(tmp_path / "model.pkl")},
        "data": {"features_path": str(features_path)},
        "strategy": {
            "name": "ml_signal",
            "buy_threshold": 0.6,
            "sell_threshold": 0.4,
            "max_weight": 1.0,
        },
        "portfolio": {"initial_cash": 1000},
        "costs": {"commission_bps": 0, "slippage_bps": 0},
        "output": {"dir": str(output_dir)},
        "experiment": {"name": "mock_ml_backtest"},
    }

    result = run_ml_backtest(
        config=config,
        storage_config=storage_config,
        model=MockProbabilityModel(),
    )

    assert Path(result["artifacts"]["metrics"]).exists()
    assert Path(result["artifacts"]["equity_curve"]).exists()
    assert Path(result["artifacts"]["trades"]).exists()
    assert Path(result["artifacts"]["summary"]).exists()
    assert Path(result["experiment_memory"]).exists()
    assert "future_direction_1" not in result["feature_columns"]
    assert "future_return_1" not in result["feature_columns"]


def test_run_ml_backtest_rejects_future_label_features(tmp_path) -> None:
    features_path = tmp_path / "features.parquet"
    storage_config = write_storage_config(tmp_path)
    make_feature_table().to_parquet(features_path, index=False)
    config = {
        "model": {"path": str(tmp_path / "model.pkl")},
        "data": {"features_path": str(features_path)},
        "strategy": {"name": "ml_signal"},
    }

    with pytest.raises(ValueError, match="Forbidden columns"):
        run_ml_backtest(
            config=config,
            storage_config=storage_config,
            model=MockProbabilityModel(feature_columns=["return_1", "future_direction_1"]),
        )

