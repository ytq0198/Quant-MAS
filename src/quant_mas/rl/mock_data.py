"""Synthetic data for RL simulation tests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_synthetic_ohlcv(n_bars: int = 64, symbol: str = "SYN") -> pd.DataFrame:
    """Build deterministic OHLCV data for one symbol."""
    if n_bars < 2:
        raise ValueError("n_bars must be at least 2")
    dates = pd.date_range("2024-01-01", periods=n_bars, freq="D")
    trend = np.linspace(0, 6, n_bars)
    seasonal = np.sin(np.arange(n_bars) / 3.0) * 0.5
    close = 100 + trend + seasonal
    open_ = close * (1 + np.cos(np.arange(n_bars)) * 0.001)
    high = np.maximum(open_, close) * 1.01
    low = np.minimum(open_, close) * 0.99
    volume = 1_000_000 + np.arange(n_bars) * 100
    return pd.DataFrame(
        {
            "date": dates,
            "symbol": symbol,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def build_synthetic_ml_signals(
    ohlcv: pd.DataFrame,
    *,
    weight: float = 0.5,
) -> pd.DataFrame:
    """Build deterministic target-weight signals for MLCopyPolicy tests."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(ohlcv["date"]),
            "symbol": ohlcv["symbol"].astype(str),
            "target_weight": float(weight),
        }
    )
