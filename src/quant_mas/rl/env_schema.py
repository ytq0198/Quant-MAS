"""Schemas for simulation-only RL trading environments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class TradingEnvConfig:
    """Configuration for a long-only discrete target-weight environment."""

    initial_cash: float = 100_000.0
    action_levels: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0)
    commission_rate: float = 0.0005
    slippage_bps: float = 1.0
    max_steps: int | None = None

    def __post_init__(self) -> None:
        if self.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if not self.action_levels:
            raise ValueError("action_levels must not be empty")
        if tuple(sorted(self.action_levels)) != tuple(self.action_levels):
            raise ValueError("action_levels must be sorted")
        if min(self.action_levels) < 0 or max(self.action_levels) > 1:
            raise ValueError("action_levels must be long-only weights in [0, 1]")
        if len(set(self.action_levels)) != len(self.action_levels):
            raise ValueError("action_levels must be unique")
        if self.commission_rate < 0:
            raise ValueError("commission_rate must be non-negative")
        if self.slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")
        if self.max_steps is not None and self.max_steps <= 0:
            raise ValueError("max_steps must be positive when provided")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradingEnvConfig":
        values = data.get("rl", data)
        return cls(
            initial_cash=float(values.get("initial_cash", 100_000.0)),
            action_levels=tuple(float(item) for item in values.get("action_levels", [0.0, 0.25, 0.5, 1.0])),
            commission_rate=float(values.get("commission_rate", 0.0005)),
            slippage_bps=float(values.get("slippage_bps", 1.0)),
            max_steps=values.get("max_steps"),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["action_levels"] = list(self.action_levels)
        return payload

    def validate_action_index(self, action_index: int) -> float:
        if not isinstance(action_index, int):
            raise ValueError("action_index must be an integer")
        if action_index < 0 or action_index >= len(self.action_levels):
            raise ValueError(f"action_index out of range: {action_index}")
        return float(self.action_levels[action_index])


@dataclass(frozen=True)
class RewardConfig:
    """Reward weights for simulation-only RL experiments."""

    w_return: float = 1.0
    w_cost: float = 0.1
    w_turnover: float = 0.05
    w_drawdown_penalty: float = 0.2

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RewardConfig":
        values = data.get("reward", data)
        return cls(
            w_return=float(values.get("w_return", 1.0)),
            w_cost=float(values.get("w_cost", 0.1)),
            w_turnover=float(values.get("w_turnover", 0.05)),
            w_drawdown_penalty=float(values.get("w_drawdown_penalty", 0.2)),
        )


@dataclass(frozen=True)
class StepResult:
    """Gymnasium-like step return container."""

    observation: dict[str, float]
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
