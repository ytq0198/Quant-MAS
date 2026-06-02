from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.models import BasePredictiveModel
from quant_mas.tools import (
    BacktestTool,
    DataSummaryTool,
    MLBacktestTool,
    PipelineTool,
    ReportTool,
    TrainModelTool,
)


class ThresholdDirectionModel(BasePredictiveModel):
    def __init__(self, **params: Any) -> None:
        self.threshold = 0.0
        self.feature_columns: list[str] = []

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "ThresholdDirectionModel":
        self.feature_columns = list(features.columns)
        self.threshold = float(features["return_1"].median())
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return (features["return_1"] >= self.threshold).astype(int)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("threshold model", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "ThresholdDirectionModel":
        return cls()

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "threshold_direction",
            "feature_columns": self.feature_columns,
        }


def make_storage_config(tmp_path: Path) -> Path:
    path = tmp_path / "storage.yaml"
    path.write_text(
        "\n".join(
            [
                "project_root: .",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: outputs/reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    return path


def make_ohlcv(path: Path) -> pd.DataFrame:
    rows = []
    for index, close in enumerate([10, 10, 10, 20, 40, 30]):
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
            }
        )
    frame = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


def make_features(path: Path) -> pd.DataFrame:
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
    frame = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


def make_ml_features(path: Path) -> pd.DataFrame:
    rows = []
    for index in range(12):
        close = 10.0 + index
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
                "return_1": index / 100.0,
                "ma_5": close / 2.0,
                "future_return_5": 0.01 if index % 2 else -0.01,
                "future_direction_5": 1 if index % 2 else 0,
            }
        )
    frame = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


def test_data_summary_tool_returns_summary_not_dataframe(tmp_path) -> None:
    data_path = tmp_path / "market_data.parquet"
    make_ohlcv(data_path)

    result = DataSummaryTool().run(path=data_path)

    assert "6 rows" in result.content
    assert result.metadata["rows"] == 6
    assert result.metadata["symbols"] == ["AAA"]
    assert "dataframe" not in result.metadata


def test_backtest_tool_saves_artifacts_and_records_experiment(tmp_path) -> None:
    storage_config = make_storage_config(tmp_path)
    data_path = tmp_path / "input" / "market_data.parquet"
    config_path = tmp_path / "backtest.yaml"
    output_dir = tmp_path / "reports" / "bt"
    make_ohlcv(data_path)
    config_path.write_text(
        "\n".join(
            [
                "strategy:",
                "  name: moving_average_cross",
                "  fast_window: 2",
                "  slow_window: 3",
                "portfolio:",
                "  initial_cash: 1000",
                "costs:",
                "  commission_bps: 0",
                "  slippage_bps: 0",
            ]
        ),
        encoding="utf-8",
    )

    result = BacktestTool().run(
        config_path=config_path,
        storage_config=storage_config,
        input_path=data_path,
        output_dir=output_dir,
    )

    artifacts = result.metadata["artifacts"]
    assert Path(artifacts["metrics"]).exists()
    assert Path(artifacts["equity_curve"]).exists()
    assert Path(artifacts["trades"]).exists()
    assert Path(artifacts["summary"]).exists()
    assert "total_return" in result.metadata["metrics"]
    assert Path(result.metadata["experiment_memory"]).exists()


def test_train_model_tool_excludes_labels_and_saves_artifacts(tmp_path) -> None:
    storage_config = make_storage_config(tmp_path)
    feature_path = tmp_path / "features.parquet"
    config_path = tmp_path / "train.yaml"
    output_dir = tmp_path / "models" / "threshold"
    make_features(feature_path)
    config_path.write_text(
        "\n".join(
            [
                "model:",
                "  name: lightgbm_direction",
                "split:",
                "  train: 0.7",
                "  validation: 0.15",
                "  test: 0.15",
                "target: future_direction",
            ]
        ),
        encoding="utf-8",
    )

    result = TrainModelTool(model_factory=ThresholdDirectionModel).run(
        config_path=config_path,
        storage_config=storage_config,
        input_path=feature_path,
        output_dir=output_dir,
    )

    assert "test_accuracy" in result.metadata["metrics"]
    assert "future_direction_5" not in result.metadata["feature_columns"]
    assert "future_return_5" not in result.metadata["feature_columns"]
    assert Path(result.metadata["artifacts"]["model"]).exists()
    assert Path(result.metadata["artifacts"]["metadata"]).exists()
    assert Path(result.metadata["experiment_memory"]).exists()


def test_report_tool_returns_latest_summary_path(tmp_path) -> None:
    storage_config = make_storage_config(tmp_path)
    data_path = tmp_path / "input" / "market_data.parquet"
    config_path = tmp_path / "backtest.yaml"
    output_dir = tmp_path / "reports" / "bt"
    make_ohlcv(data_path)
    config_path.write_text(
        "\n".join(
            [
                "strategy:",
                "  name: moving_average_cross",
                "  fast_window: 2",
                "  slow_window: 3",
                "portfolio:",
                "  initial_cash: 1000",
                "costs:",
                "  commission_bps: 0",
                "  slippage_bps: 0",
            ]
        ),
        encoding="utf-8",
    )
    BacktestTool().run(
        config_path=config_path,
        storage_config=storage_config,
        input_path=data_path,
        output_dir=output_dir,
        experiment_name="tool_backtest",
    )

    result = ReportTool().run(storage_config=storage_config)

    assert "Latest report" in result.content
    assert result.metadata["experiment_name"] == "tool_backtest"
    assert Path(result.metadata["summary"]).exists()


def test_ml_backtest_tool_runs_with_mock_model(tmp_path) -> None:
    storage_config = make_storage_config(tmp_path)
    feature_path = tmp_path / "features.parquet"
    config_path = tmp_path / "backtest_ml.yaml"
    output_dir = tmp_path / "reports" / "ml"
    make_ml_features(feature_path)
    config_path.write_text(
        "\n".join(
            [
                "model:",
                f"  path: {tmp_path / 'model.pkl'}",
                "data:",
                f"  features_path: {feature_path}",
                "strategy:",
                "  name: ml_signal",
                "  buy_threshold: 0.6",
                "  sell_threshold: 0.4",
                "  max_weight: 1.0",
                "portfolio:",
                "  initial_cash: 1000",
                "costs:",
                "  commission_bps: 0",
                "  slippage_bps: 0",
                "output:",
                f"  dir: {output_dir}",
                "experiment:",
                "  name: tool_ml_backtest",
            ]
        ),
        encoding="utf-8",
    )

    result = MLBacktestTool(model=ThresholdDirectionModel()).run(
        config_path=config_path,
        storage_config=storage_config,
    )

    assert "ML backtest completed" in result.content
    assert "total_return" in result.metadata["metrics"]
    assert Path(result.metadata["artifacts"]["summary"]).exists()
    assert Path(result.metadata["experiment_memory"]).exists()


def test_pipeline_tool_runs_local_sample_without_network(tmp_path) -> None:
    storage_config = make_storage_config(tmp_path)
    raw_dir = tmp_path / "raw"
    features_dir = tmp_path / "features"
    output_dir = tmp_path / "reports" / "pipeline"
    backtest_config = tmp_path / "backtest.yaml"
    features_config = tmp_path / "features.yaml"
    make_ohlcv(raw_dir / "market_data.parquet")
    make_ml_features(features_dir / "features.parquet")
    backtest_config.write_text(
        "\n".join(
            [
                "strategy:",
                "  name: moving_average_cross",
                "  fast_window: 2",
                "  slow_window: 3",
                "portfolio:",
                "  initial_cash: 1000",
                "costs:",
                "  commission_bps: 0",
                "  slippage_bps: 0",
            ]
        ),
        encoding="utf-8",
    )
    features_config.write_text("technical: {}\nlabels: {}\n", encoding="utf-8")

    result = PipelineTool().run(
        storage_config=storage_config,
        raw_dir=raw_dir,
        features_dir=features_dir,
        output_dir=output_dir,
        features_config=features_config,
        backtest_config=backtest_config,
        skip_download=True,
        skip_features=True,
        experiment_name="tool_pipeline",
    )

    assert "Pipeline completed" in result.content
    assert "total_return" in result.metadata["metrics"]
    assert Path(result.metadata["artifacts"]["summary"]).exists()
    assert Path(result.metadata["paths"]["experiment_memory"]).exists()
