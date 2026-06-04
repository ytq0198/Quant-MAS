"""Trainable GRPO-style policy agent for simulation-only RL experiments."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

from quant_mas.rl.grpo_experiment import CandidateRun


@dataclass
class PolicyState:
    """Serializable trainable policy state."""

    action_logits: list[float]
    step_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class GRPOPolicyAgent:
    """Discrete-action policy trainable via group-relative advantages."""

    def __init__(
        self,
        *,
        agent_id: str,
        action_space_n: int,
        seed: int = 42,
        initial_logits: list[float] | None = None,
    ) -> None:
        if action_space_n <= 0:
            raise ValueError("action_space_n must be positive")
        if initial_logits is not None and len(initial_logits) != action_space_n:
            raise ValueError("initial_logits length must match action_space_n")
        self.agent_id = agent_id
        self.action_space_n = int(action_space_n)
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self._state = PolicyState(
            action_logits=list(initial_logits)
            if initial_logits is not None
            else [0.0 for _ in range(self.action_space_n)],
            metadata={"agent_id": agent_id, "seed": self.seed, "simulation_only": True},
        )

    def act(self, observation: dict[str, float], info: dict[str, Any]) -> int:
        """Return a deterministic legal action index."""
        del observation, info
        maximum = max(self._state.action_logits)
        candidates = [
            index
            for index, value in enumerate(self._state.action_logits)
            if value == maximum
        ]
        if len(candidates) == 1:
            return candidates[0]
        return candidates[self._rng.randrange(len(candidates))]

    def snapshot(self) -> PolicyState:
        """Return a serializable policy state copy."""
        return PolicyState(
            action_logits=list(self._state.action_logits),
            step_count=self._state.step_count,
            metadata=dict(self._state.metadata),
        )

    def load_snapshot(self, state: PolicyState) -> None:
        """Load a previously serialized policy state."""
        if len(state.action_logits) != self.action_space_n:
            raise ValueError("PolicyState action_logits length does not match action_space_n")
        self._state = PolicyState(
            action_logits=[float(value) for value in state.action_logits],
            step_count=int(state.step_count),
            metadata=dict(state.metadata),
        )

    def update_from_group_advantages(
        self,
        trajectories,
        *,
        ranked: list[CandidateRun],
        learning_rate: float = 0.05,
    ) -> dict[str, float]:
        """Nudge action logits using group-relative rewards."""
        if learning_rate < 0:
            raise ValueError("learning_rate must be non-negative")
        advantages = {
            item.name: float(
                item.relative_reward if item.relative_reward is not None else item.reward
            )
            for item in ranked
        }
        before = list(self._state.action_logits)
        for trajectory in trajectories:
            advantage = advantages.get(trajectory.agent_id, trajectory.episode_reward)
            if not trajectory.action_indices:
                continue
            scale = learning_rate * float(advantage) / len(trajectory.action_indices)
            for action_index in trajectory.action_indices:
                if 0 <= int(action_index) < self.action_space_n:
                    self._state.action_logits[int(action_index)] += scale
        self._state.step_count += 1
        delta_norm = math.sqrt(
            sum((after - prior) ** 2 for prior, after in zip(before, self._state.action_logits))
        )
        return {
            "training.policy_step_count": float(self._state.step_count),
            "training.policy_delta_norm": float(delta_norm),
            "training.learning_rate": float(learning_rate),
        }
