"""Market data validation helpers."""

from __future__ import annotations

import pandas as pd


OHLCV_COLUMNS = ["date", "symbol", "open", "high", "low", "close", "volume"]
PRICE_COLUMNS = ["open", "high", "low", "close"]
NUMERIC_COLUMNS = [*PRICE_COLUMNS, "volume"]


def validate_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize OHLCV market data.

    Returns a copy with canonical columns:
    date, symbol, open, high, low, close, volume.
    """
    missing_columns = [column for column in OHLCV_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Missing OHLCV columns: {missing_columns}")

    result = frame.loc[:, OHLCV_COLUMNS].copy()
    if result.empty:
        raise ValueError("OHLCV data is empty")

    result["date"] = pd.to_datetime(result["date"], errors="raise")
    result["symbol"] = result["symbol"].astype(str).str.strip().str.upper()

    for column in NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="raise")

    if result[OHLCV_COLUMNS].isna().any().any():
        raise ValueError("OHLCV data contains missing values")
    if (result["symbol"] == "").any():
        raise ValueError("OHLCV data contains empty symbols")
    if result.duplicated(["date", "symbol"]).any():
        raise ValueError("OHLCV data contains duplicate date/symbol rows")
    if (result[PRICE_COLUMNS] <= 0).any().any():
        raise ValueError("OHLCV prices must be positive")
    if (result["volume"] < 0).any():
        raise ValueError("OHLCV volume must be non-negative")
    if (result["high"] < result[["open", "low", "close"]].max(axis=1)).any():
        raise ValueError("OHLCV high is below open, low, or close")
    if (result["low"] > result[["open", "high", "close"]].min(axis=1)).any():
        raise ValueError("OHLCV low is above open, high, or close")

    return result.sort_values(["symbol", "date"]).reset_index(drop=True)

