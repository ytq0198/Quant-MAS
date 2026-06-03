"""Simulation-only strategy agents for competitive learning."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class AgentProposal:
    """One target-weight proposal from a strategy agent."""

    agent_id: str
    target_weight: float
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentEvaluation:
    """Episode-level evaluation for one strategy agent."""

    agent_id: str
    metrics: dict[str, float]
    reward: float
    window_id: int = 0


class StrategyAgent(ABC):
    """Base class for deterministic simulation-only strategy agents."""

    def __init__(self, agent_id: str, *, name: str | None = None) -> None:
        self.agent_id = agent_id
        self.name = name or agent_id

    @abstractmethod
    def propose(self, observation: dict[str, float], info: dict[str, Any]) -> AgentProposal:
        """Return a target-weight proposal from current and historical data only."""

    def evaluate_episode(
        self,
        equity_curve: list[float],
        *,
        window_id: int = 0,
    ) -> AgentEvaluation:
        """Evaluate one shadow episode from its equity curve."""
        from quant_mas.rl.reward import compute_episode_metrics

        metrics = {
            f"simulation.{key}": float(value)
            for key, value in compute_episode_metrics(pd.Series(equity_curve, dtype=float)).items()
        }
        reward = float(metrics.get("simulation.sharpe", 0.0))
        return AgentEvaluation(
            agent_id=self.agent_id,
            metrics=metrics,
            reward=reward,
            window_id=window_id,
        )


class MomentumAgent(StrategyAgent):
    """Long more when recent return or moving-average distance is positive."""

    def __init__(self, agent_id: str, *, scale: float = 1.0, lookback: int = 5) -> None:
        super().__init__(agent_id, name="MomentumAgent")
        self.scale = float(scale)
        self.lookback = int(lookback)

    def propose(self, observation: dict[str, float], info: dict[str, Any]) -> AgentProposal:
        signal = _signal_from_observation(observation)
        target = _clip01(0.5 + self.scale * signal * 10.0)
        return AgentProposal(
            agent_id=self.agent_id,
            target_weight=target,
            confidence=min(1.0, abs(signal) * 10.0),
            metadata={"agent_type": "momentum", "lookback": self.lookback, "signal": signal},
        )


class MeanReversionAgent(StrategyAgent):
    """Reduce exposure when recent return or moving-average distance is high."""

    def __init__(self, agent_id: str, *, scale: float = 1.0, lookback: int = 5) -> None:
        super().__init__(agent_id, name="MeanReversionAgent")
        self.scale = float(scale)
        self.lookback = int(lookback)

    def propose(self, observation: dict[str, float], info: dict[str, Any]) -> AgentProposal:
        signal = _signal_from_observation(observation)
        target = _clip01(0.5 - self.scale * signal * 10.0)
        return AgentProposal(
            agent_id=self.agent_id,
            target_weight=target,
            confidence=min(1.0, abs(signal) * 10.0),
            metadata={"agent_type": "mean_reversion", "lookback": self.lookback, "signal": signal},
        )


def build_strategy_agent(agent_id: str, agent_type: str, params: dict[str, Any] | None = None) -> StrategyAgent:
    """Create a deterministic strategy agent from config."""
    values = params or {}
    if agent_type == "momentum":
        return MomentumAgent(
            agent_id,
            lookback=int(values.get("lookback", 5)),
            scale=float(values.get("scale", 1.0)),
        )
    if agent_type == "mean_reversion":
        return MeanReversionAgent(
            agent_id,
            lookback=int(values.get("lookback", 5)),
            scale=float(values.get("scale", 1.0)),
        )
    raise ValueError("Unknown strategy agent type. Use momentum or mean_reversion.")


def _signal_from_observation(observation: dict[str, float]) -> float:
    for key in ("ma_distance_5", "last_return"):
        if key in observation:
            return float(observation[key])
    return 0.0


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
