from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant_mas.memory import ExperimentMemory
from quant_mas.pipeline import run_quant_pipeline


def make_ohlcv(path: Path) -> None:
    rows = []
    closes = [10, 10, 10, 20, 40, 50, 45, 48, 52, 55]
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
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


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
                "reports_dir: outputs/reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_features_config(tmp_path: Path) -> Path:
    path = tmp_path / "features.yaml"
    path.write_text(
        "\n".join(
            [
                "price_column: close",
                "windows:",
                "  moving_average:",
                "    - 2",
                "    - 3",
                "  volatility:",
                "    - 2",
                "  volume:",
                "    - 2",
                "rsi_window: 2",
                "return_periods:",
                "  - 1",
                "label:",
                "  horizon: 1",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_backtest_config(tmp_path: Path) -> Path:
    path = tmp_path / "backtest.yaml"
    path.write_text(
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
    return path


def test_pipeline_runs_from_local_synthetic_parquet(tmp_path) -> None:
    raw_dir = tmp_path / "raw"
    features_dir = tmp_path / "features"
    output_dir = tmp_path / "outputs" / "reports" / "pipeline"
    make_ohlcv(raw_dir / "market_data.parquet")

    result = run_quant_pipeline(
        symbols=["AAA"],
        start="2026-01-01",
        end="2026-01-10",
        raw_dir=raw_dir,
        features_dir=features_dir,
        output_dir=output_dir,
        storage_config=write_storage_config(tmp_path),
        features_config=write_features_config(tmp_path),
        backtest_config=write_backtest_config(tmp_path),
        skip_download=True,
        skip_features=False,
        strategy_name="ma_cross",
        experiment_name="synthetic_pipeline",
        log=lambda message: None,
    )

    assert (features_dir / "features.parquet").exists()
    assert (output_dir / "metrics.json").exists()
    assert (output_dir / "equity_curve.csv").exists()
    assert (output_dir / "trades.csv").exists()
    assert (output_dir / "summary.md").exists()
    assert result.metrics["bars"] == 10
    latest = ExperimentMemory(result.experiment_memory_path).latest()
    assert latest.name == "synthetic_pipeline"
    assert latest.artifacts["summary"].endswith("summary.md")

