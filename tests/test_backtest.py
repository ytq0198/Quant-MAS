from __future__ import annotations

import pandas as pd
import pytest

from quant_mas.backtest import (
    BacktestEngine,
    CommissionModel,
    SlippageModel,
    calculate_metrics,
    max_drawdown,
)
from quant_mas.strategies import MovingAverageCrossStrategy


def make_ohlcv(closes: list[float], symbol: str = "AAA") -> pd.DataFrame:
    rows = []
    for index, close in enumerate(closes):
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": symbol,
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
            }
        )
    return pd.DataFrame(rows)


def test_moving_average_cross_strategy_generates_target_weight() -> None:
    data = make_ohlcv([10, 10, 10, 20, 30])
    strategy = MovingAverageCrossStrategy(fast_window=2, slow_window=3)

    signals = strategy.generate_signals(data)

    assert list(signals[["date", "symbol", "target_weight"]].columns) == [
        "date",
        "symbol",
        "target_weight",
    ]
    assert signals["target_weight"].tolist() == [0.0, 0.0, 0.0, 1.0, 1.0]


def test_backtest_executes_signal_on_next_bar() -> None:
    data = make_ohlcv([10, 10, 10, 20, 40])
    strategy = MovingAverageCrossStrategy(fast_window=2, slow_window=3)
    engine = BacktestEngine(strategy=strategy, initial_cash=100.0)

    result = engine.run(data)

    trades = result.trades
    assert len(trades) == 1
    assert trades.loc[0, "date"] == pd.Timestamp("2026-01-05")
    assert trades.loc[0, "side"] == "buy"
    assert result.equity_curve.loc[3, "equity"] == pytest.approx(100.0)
    assert result.equity_curve.loc[4, "equity"] == pytest.approx(100.0)


def test_backtest_marks_close_after_next_bar_execution() -> None:
    data = make_ohlcv([10, 10, 10, 20, 40])
    data.loc[4, "open"] = 20.0
    data.loc[4, "high"] = 41.0
    data.loc[4, "low"] = 19.0
    strategy = MovingAverageCrossStrategy(fast_window=2, slow_window=3)
    engine = BacktestEngine(strategy=strategy, initial_cash=100.0)

    result = engine.run(data)

    assert result.trades.loc[0, "price"] == pytest.approx(20.0)
    assert result.equity_curve.loc[4, "equity"] == pytest.approx(200.0)


def test_commission_and_slippage_models() -> None:
    commission = CommissionModel(commission_bps=10)
    slippage = SlippageModel(slippage_bps=5)

    assert commission.calculate(1000.0) == pytest.approx(1.0)
    assert slippage.adjust_price(100.0, "buy") == pytest.approx(100.05)
    assert slippage.adjust_price(100.0, "sell") == pytest.approx(99.95)


def test_metrics_include_drawdown_and_total_return() -> None:
    equity = pd.DataFrame({"equity": [100.0, 120.0, 90.0, 110.0]})

    metrics = calculate_metrics(equity)

    assert metrics["total_return"] == pytest.approx(0.1)
    assert max_drawdown(equity["equity"]) == pytest.approx(-0.25)
    assert "sharpe" in metrics
