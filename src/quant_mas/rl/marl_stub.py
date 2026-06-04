"""MARL extension point for future Quant MAS milestones."""

from __future__ import annotations

from typing import Any, Protocol


class MultiAgentTrainingProtocol(Protocol):
    """CTDE / league-training extension point."""

    def train_joint(self, agents: list[Any], env: Any) -> dict[str, Any]:
        """Train multiple agents jointly."""


class MARLTrainingStub:
    """Explicit stub for future multi-agent RL training."""

    def train_joint(self, agents: list[Any], env: Any) -> dict[str, Any]:
        del agents, env
        raise NotImplementedError("MARL training is reserved for a future milestone")
