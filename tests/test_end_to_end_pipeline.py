from __future__ import annotations

import pandas as pd

from quant_mas.backtest import BacktestEngine, save_backtest_report
from quant_mas.data import ParquetStorage
from quant_mas.features import build_feature_table
from quant_mas.memory import ExperimentMemory
from quant_mas.strategies import MovingAverageCrossStrategy


def make_synthetic_ohlcv() -> pd.DataFrame:
    closes = [10, 10, 10, 20, 40, 50, 45, 48, 52, 55]
    rows = []
    for index, close in enumerate(closes):
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
    return pd.DataFrame(rows)


def test_minimal_quant_pipeline_end_to_end(tmp_path) -> None:
    storage = ParquetStorage()
    raw_path = tmp_path / "raw" / "market_data.parquet"
    features_path = tmp_path / "features" / "features.parquet"
    report_dir = tmp_path / "reports" / "end_to_end"
    memory_path = tmp_path / "reports" / "experiments.json"

    raw_data = make_synthetic_ohlcv()
    storage.save(raw_data, raw_path)

    loaded_raw_data = storage.load(raw_path)
    features = build_feature_table(
        loaded_raw_data,
        moving_average_windows=(2, 3),
        volatility_windows=(2,),
        volume_windows=(2,),
        rsi_window=2,
        label_horizon=1,
    )
    storage.save(features, features_path)

    strategy = MovingAverageCrossStrategy(fast_window=2, slow_window=3)
    result = BacktestEngine(strategy=strategy, initial_cash=1000.0).run(loaded_raw_data)
    artifacts = save_backtest_report(
        result,
        report_dir,
        title="End-to-End Synthetic Backtest",
        params={"strategy": "ma_cross", "data": "synthetic"},
    )
    ExperimentMemory(memory_path).add(
        name="end_to_end_synthetic_pipeline",
        metrics=result.metrics,
        artifacts=artifacts,
        params={
            "raw_path": str(raw_path),
            "features_path": str(features_path),
            "report_dir": str(report_dir),
        },
    )

    assert raw_path.exists()
    assert features_path.exists()
    assert artifacts["metrics"].exists()
    assert artifacts["equity_curve"].exists()
    assert artifacts["trades"].exists()
    assert artifacts["summary"].exists()
    assert memory_path.exists()

    for metric in ("total_return", "sharpe", "max_drawdown", "final_equity"):
        assert metric in result.metrics

    latest = ExperimentMemory(memory_path).latest()
    assert latest.name == "end_to_end_synthetic_pipeline"
    assert latest.artifacts["summary"].endswith("summary.md")

