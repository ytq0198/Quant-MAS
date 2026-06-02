"""Technical feature builders.

All functions assume input has already been sorted by symbol/date inside the
pipeline. Rolling operations are backward-looking only.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def add_returns(
    frame: pd.DataFrame,
    price_column: str = "close",
    periods: Iterable[int] = (1,),
) -> pd.DataFrame:
    result = frame.copy()
    for period in periods:
        result[f"return_{period}"] = result[price_column].pct_change(periods=period)
    return result


def add_moving_averages(
    frame: pd.DataFrame,
    price_column: str = "close",
    windows: Iterable[int] = (5, 20),
) -> pd.DataFrame:
    result = frame.copy()
    for window in windows:
        result[f"ma_{window}"] = (
            result[price_column].rolling(window=window, min_periods=window).mean()
        )
    return result


def add_ma_distance(
    frame: pd.DataFrame,
    price_column: str = "close",
    windows: Iterable[int] = (5, 20),
) -> pd.DataFrame:
    result = frame.copy()
    for window in windows:
        ma_column = f"ma_{window}"
        if ma_column not in result.columns:
            result[ma_column] = (
                result[price_column].rolling(window=window, min_periods=window).mean()
            )
        result[f"ma_distance_{window}"] = result[price_column] / result[ma_column] - 1.0
    return result


def add_volatility(
    frame: pd.DataFrame,
    price_column: str = "close",
    windows: Iterable[int] = (20,),
) -> pd.DataFrame:
    result = frame.copy()
    returns = result[price_column].pct_change()
    for window in windows:
        result[f"volatility_{window}"] = returns.rolling(
            window=window,
            min_periods=window,
        ).std()
    return result


def add_volume_features(
    frame: pd.DataFrame,
    windows: Iterable[int] = (20,),
    volume_column: str = "volume",
) -> pd.DataFrame:
    result = frame.copy()
    result["volume_change_1"] = result[volume_column].pct_change()
    for window in windows:
        ma_column = f"volume_ma_{window}"
        result[ma_column] = (
            result[volume_column].rolling(window=window, min_periods=window).mean()
        )
        result[f"volume_ratio_{window}"] = result[volume_column] / result[ma_column]
    return result


def add_rsi(
    frame: pd.DataFrame,
    price_column: str = "close",
    window: int = 14,
) -> pd.DataFrame:
    result = frame.copy()
    delta = result[price_column].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    relative_strength = avg_gain / avg_loss
    result[f"rsi_{window}"] = 100.0 - (100.0 / (1.0 + relative_strength))
    result.loc[avg_loss == 0, f"rsi_{window}"] = 100.0
    return result

