"""Strategy package."""

from quant_mas.strategies.base import Strategy
from quant_mas.strategies.ma_cross import MovingAverageCrossStrategy
from quant_mas.strategies.ml_signal import MLSignalStrategy

__all__ = ["MLSignalStrategy", "MovingAverageCrossStrategy", "Strategy"]
