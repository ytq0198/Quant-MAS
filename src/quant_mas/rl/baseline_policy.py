"""Baseline policies for simulation-only RL experiments."""

from __future__ import annotations

from typing import Any, Protocol

import numpy as np
import pandas as pd

from quant_mas.rl.env_schema import TradingEnvConfig


class Policy(Protocol):
    """Policy protocol returning a discrete action index."""

    def act(self, observation: Any, info: dict[str, Any]) -> int:
        """Return action index."""


class RandomPolicy:
    """Seeded random discrete policy."""

    def __init__(self, action_space_n: int, *, seed: int = 42) -> None:
        self.action_space_n = action_space_n
        self.rng = np.random.default_rng(seed)

    def act(self, observation: Any, info: dict[str, Any]) -> int:
        return int(self.rng.integers(0, self.action_space_n))


class BuyAndHoldPolicy:
    """Always choose the highest long-only action."""

    def __init__(self, action_space_n: int) -> None:
        self.action_space_n = action_space_n

    def act(self, observation: Any, info: dict[str, Any]) -> int:
        return self.action_space_n - 1


class MLCopyPolicy:
    """Copy precomputed target_weight signals to nearest discrete action."""

    def __init__(
        self,
        signals: pd.DataFrame,
        *,
        config: TradingEnvConfig,
        symbol: str | None = None,
    ) -> None:
        required = {"date", "target_weight"}
        missing = required.difference(signals.columns)
        if missing:
            raise ValueError(f"MLCopyPolicy signals missing columns: {sorted(missing)}")
        frame = signals.copy()
        frame["date"] = pd.to_datetime(frame["date"])
        if symbol is not None and "symbol" in frame.columns:
            frame = frame[frame["symbol"].astype(str) == symbol]
        if frame.duplicated("date").any():
            raise ValueError("MLCopyPolicy signals contain duplicate dates")
        self.signals = frame.set_index("date").sort_index()
        self.config = config

    def act(self, observation: Any, info: dict[str, Any]) -> int:
        date = pd.to_datetime(info["date"])
        if date not in self.signals.index:
            return 0
        weight = float(self.signals.loc[date, "target_weight"])
        distances = [abs(level - weight) for level in self.config.action_levels]
        return int(np.argmin(distances))


def build_policy(
    name: str,
    *,
    config: TradingEnvConfig,
    signals: pd.DataFrame | None = None,
    seed: int = 42,
    symbol: str | None = None,
) -> Policy:
    """Create a baseline policy."""
    normalized = name.lower().strip()
    if normalized in {"random", "random_policy"}:
        return RandomPolicy(len(config.action_levels), seed=seed)
    if normalized in {"buy_hold", "buy_and_hold", "buyandhold"}:
        return BuyAndHoldPolicy(len(config.action_levels))
    if normalized in {"ml_copy", "mlcopy"}:
        if signals is None:
            raise ValueError("ml_copy policy requires signals")
        return MLCopyPolicy(signals, config=config, symbol=symbol)
    raise ValueError("Unknown policy. Use random, buy_hold, or ml_copy.")
