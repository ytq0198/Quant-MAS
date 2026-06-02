from __future__ import annotations

import json

import pandas as pd

from quant_mas.backtest import BacktestResult, save_backtest_report
from quant_mas.memory import ExperimentMemory


def make_result() -> BacktestResult:
    return BacktestResult(
        equity_curve=pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "equity": [100.0, 110.0],
                "returns": [0.0, 0.1],
            }
        ),
        trades=pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-02"]),
                "symbol": ["AAA"],
                "side": ["buy"],
                "quantity": [1.0],
                "price": [100.0],
                "trade_value": [100.0],
                "commission": [0.0],
            }
        ),
        metrics={
            "total_return": 0.1,
            "sharpe": 1.2,
            "max_drawdown": 0.0,
            "final_equity": 110.0,
            "bars": 2,
        },
    )


def test_experiment_memory_add_list_latest(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.json")

    record = memory.add(
        name="test_backtest",
        metrics={"total_return": 0.1},
        artifacts={"summary": tmp_path / "summary.md"},
        params={"fast_window": 5},
        notes="synthetic",
    )

    records = memory.list()
    latest = memory.latest()
    assert records == [record]
    assert latest.name == "test_backtest"
    assert latest.metrics["total_return"] == 0.1
    assert latest.artifacts["summary"].endswith("summary.md")


def test_save_backtest_report_writes_expected_artifacts(tmp_path) -> None:
    result = make_result()

    artifacts = save_backtest_report(
        result,
        tmp_path,
        title="Synthetic Backtest",
        params={"strategy": {"name": "test"}},
    )

    assert artifacts["metrics"].exists()
    assert artifacts["equity_curve"].exists()
    assert artifacts["trades"].exists()
    assert artifacts["summary"].exists()
    assert json.loads(artifacts["metrics"].read_text(encoding="utf-8"))[
        "total_return"
    ] == 0.1
    assert "Synthetic Backtest" in artifacts["summary"].read_text(encoding="utf-8")

