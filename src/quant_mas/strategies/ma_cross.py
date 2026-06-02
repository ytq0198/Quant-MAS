"""Moving average cross strategy."""

from __future__ import annotations

import pandas as pd

from quant_mas.data import validate_ohlcv
from quant_mas.strategies.base import Strategy


class MovingAverageCrossStrategy(Strategy):
    """Long-only moving average crossover strategy."""

    def __init__(
        self,
        fast_window: int = 5,
        slow_window: int = 20,
        price_column: str = "close",
        long_weight: float = 1.0,
    ) -> None:
        if fast_window <= 0 or slow_window <= 0:
            raise ValueError("moving average windows must be positive")
        if fast_window >= slow_window:
            raise ValueError("fast_window must be smaller than slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.price_column = price_column
        self.long_weight = long_weight

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        validated = validate_ohlcv(data)
        frames = []
        for _, symbol_frame in validated.groupby("symbol", sort=True):
            group = symbol_frame.sort_values("date").reset_index(drop=True)
            fast_ma = group[self.price_column].rolling(
                window=self.fast_window,
                min_periods=self.fast_window,
            ).mean()
            slow_ma = group[self.price_column].rolling(
                window=self.slow_window,
                min_periods=self.slow_window,
            ).mean()
            signal = group.loc[:, ["date", "symbol"]].copy()
            signal["fast_ma"] = fast_ma
            signal["slow_ma"] = slow_ma
            signal["target_weight"] = (fast_ma > slow_ma).astype(float) * self.long_weight
            signal.loc[slow_ma.isna(), "target_weight"] = 0.0
            frames.append(signal)
        return pd.concat(frames, ignore_index=True)

