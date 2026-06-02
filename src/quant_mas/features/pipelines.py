"""Feature table pipeline."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from quant_mas.data import validate_ohlcv
from quant_mas.features.labels import add_future_return_label
from quant_mas.features.technical import (
    add_ma_distance,
    add_moving_averages,
    add_returns,
    add_rsi,
    add_volatility,
    add_volume_features,
)


def build_feature_table(
    frame: pd.DataFrame,
    *,
    price_column: str = "close",
    return_periods: Iterable[int] = (1,),
    moving_average_windows: Iterable[int] = (5, 20),
    volatility_windows: Iterable[int] = (20,),
    volume_windows: Iterable[int] = (20,),
    rsi_window: int = 14,
    label_horizon: int = 5,
) -> pd.DataFrame:
    """Build features independently for each symbol."""
    validated = validate_ohlcv(frame)
    groups = []

    for _, symbol_frame in validated.groupby("symbol", sort=True):
        group = symbol_frame.sort_values("date").reset_index(drop=True)
        group = add_returns(group, price_column=price_column, periods=return_periods)
        group = add_moving_averages(
            group,
            price_column=price_column,
            windows=moving_average_windows,
        )
        group = add_ma_distance(
            group,
            price_column=price_column,
            windows=moving_average_windows,
        )
        group = add_volatility(
            group,
            price_column=price_column,
            windows=volatility_windows,
        )
        group = add_volume_features(group, windows=volume_windows)
        group = add_rsi(group, price_column=price_column, window=rsi_window)
        group = add_future_return_label(
            group,
            price_column=price_column,
            horizon=label_horizon,
        )
        groups.append(group)

    return pd.concat(groups, ignore_index=True)


def build_feature_table_from_config(
    frame: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    windows = config.get("windows", {})
    label = config.get("label", {})
    return build_feature_table(
        frame,
        price_column=config.get("price_column", "close"),
        return_periods=config.get("return_periods", (1,)),
        moving_average_windows=windows.get("moving_average", (5, 20)),
        volatility_windows=windows.get("volatility", (20,)),
        volume_windows=windows.get("volume", windows.get("volatility", (20,))),
        rsi_window=config.get("rsi_window", 14),
        label_horizon=label.get("horizon", 5),
    )

