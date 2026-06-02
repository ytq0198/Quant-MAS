"""Machine-learning probability signal strategy."""

from __future__ import annotations

import pandas as pd

from quant_mas.strategies.base import Strategy


class MLSignalStrategy(Strategy):
    """Convert model predicted probabilities into target weights.

    The strategy consumes a precomputed prediction table. It does not inspect
    future labels and does not call the model itself.
    """

    def __init__(
        self,
        predictions: pd.DataFrame,
        *,
        buy_threshold: float = 0.6,
        sell_threshold: float = 0.4,
        max_weight: float = 1.0,
        probability_column: str = "pred_proba",
    ) -> None:
        if not 0.0 <= sell_threshold <= buy_threshold <= 1.0:
            raise ValueError("thresholds must satisfy 0 <= sell <= buy <= 1")
        if max_weight < 0:
            raise ValueError("max_weight must be non-negative")
        self.predictions = self._validate_predictions(predictions, probability_column)
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.max_weight = max_weight
        self.probability_column = probability_column

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        required = data.loc[:, ["date", "symbol"]].copy()
        required["date"] = pd.to_datetime(required["date"], errors="raise")
        required["symbol"] = required["symbol"].astype(str).str.upper()
        merged = required.merge(
            self.predictions,
            on=["date", "symbol"],
            how="left",
        )
        if merged[self.probability_column].isna().any():
            raise ValueError("Missing pred_proba for one or more backtest rows")

        frames = []
        for _, group in merged.groupby("symbol", sort=True):
            group = group.sort_values("date").reset_index(drop=True)
            current_weight = 0.0
            signals = []
            weights = []
            for probability in group[self.probability_column]:
                if probability >= self.buy_threshold:
                    signal = 1
                    current_weight = self.max_weight
                elif probability <= self.sell_threshold:
                    signal = -1
                    current_weight = 0.0
                else:
                    signal = 0
                signals.append(signal)
                weights.append(current_weight)
            output = group.loc[:, ["date", "symbol", self.probability_column]].copy()
            output["signal"] = signals
            output["target_weight"] = weights
            frames.append(output)
        return pd.concat(frames, ignore_index=True)

    @staticmethod
    def _validate_predictions(
        predictions: pd.DataFrame,
        probability_column: str,
    ) -> pd.DataFrame:
        required = {"date", "symbol", probability_column}
        missing = required.difference(predictions.columns)
        if missing:
            raise ValueError(f"ML predictions missing columns: {sorted(missing)}")
        result = predictions.loc[:, ["date", "symbol", probability_column]].copy()
        result["date"] = pd.to_datetime(result["date"], errors="raise")
        result["symbol"] = result["symbol"].astype(str).str.upper()
        result[probability_column] = pd.to_numeric(
            result[probability_column],
            errors="raise",
        )
        if result.duplicated(["date", "symbol"]).any():
            raise ValueError("ML predictions contain duplicate date/symbol rows")
        if result[probability_column].isna().any():
            raise ValueError("ML predictions contain missing probabilities")
        if not result[probability_column].between(0.0, 1.0).all():
            raise ValueError("pred_proba must be between 0 and 1")
        return result.sort_values(["symbol", "date"]).reset_index(drop=True)

