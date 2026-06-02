"""Transaction cost models."""

from __future__ import annotations


class CommissionModel:
    """Linear commission model expressed in basis points."""

    def __init__(self, commission_bps: float = 0.0) -> None:
        if commission_bps < 0:
            raise ValueError("commission_bps must be non-negative")
        self.commission_bps = commission_bps

    def calculate(self, trade_value: float) -> float:
        return abs(trade_value) * self.commission_bps / 10_000.0


class SlippageModel:
    """Linear slippage model expressed in basis points."""

    def __init__(self, slippage_bps: float = 0.0) -> None:
        if slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")
        self.slippage_bps = slippage_bps

    def adjust_price(self, price: float, side: str) -> float:
        multiplier = self.slippage_bps / 10_000.0
        if side == "buy":
            return price * (1.0 + multiplier)
        if side == "sell":
            return price * (1.0 - multiplier)
        raise ValueError("side must be 'buy' or 'sell'")

