"""PPO trainer protocol and simulation-only stub."""

from __future__ import annotations

from typing import Protocol


class TrainerProtocol(Protocol):
    """Trainer interface for future RL algorithms."""

    def train_step(self, batch) -> dict[str, float]:
        """Train one step from trajectory records."""


class PPOTrainer:
    """Stub trainer for the M12 PPO extension path."""

    def train_step(self, batch) -> dict[str, float]:
        del batch
        return {"training.ppo_stub": 1.0, "training.loss": 0.0}
