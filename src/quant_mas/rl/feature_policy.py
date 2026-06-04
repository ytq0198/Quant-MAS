"""Observation-aware linear policy for simulation-only RL experiments."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from quant_mas.rl.grpo_experiment import CandidateRun


DEFAULT_FEATURE_NAMES = [
    "position_weight",
    "last_return",
    "rolling_vol_5",
    "volume",
    "close",
]


@dataclass
class FeaturePolicyState:
    """Serializable feature-linear policy state."""

    feature_names: list[str]
    action_weights: list[list[float]]
    action_bias: list[float]
    step_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureLinearPolicyAgent:
    """Discrete policy using linear scores over observation features."""

    def __init__(
        self,
        *,
        agent_id: str,
        action_space_n: int,
        seed: int = 42,
        feature_names: list[str] | None = None,
        initial_state: FeaturePolicyState | None = None,
    ) -> None:
        if action_space_n <= 0:
            raise ValueError("action_space_n must be positive")
        self.agent_id = agent_id
        self.action_space_n = int(action_space_n)
        self.seed = int(seed)
        if initial_state is not None:
            self._state = _validate_state(initial_state, self.action_space_n)
        else:
            names = list(feature_names or DEFAULT_FEATURE_NAMES)
            self._state = FeaturePolicyState(
                feature_names=names,
                action_weights=_default_action_weights(self.action_space_n, names),
                action_bias=[0.0 for _ in range(self.action_space_n)],
                metadata={
                    "agent_id": agent_id,
                    "seed": self.seed,
                    "simulation_only": True,
                    "policy_type": "feature_linear",
                },
            )

    def act(self, observation: dict[str, float], info: dict[str, Any]) -> int:
        """Return the action with the highest feature-linear score."""
        del info
        features = [
            normalize_observation_feature(name, observation.get(name, 0.0))
            for name in self._state.feature_names
        ]
        scores = []
        for action_index in range(self.action_space_n):
            score = self._state.action_bias[action_index]
            score += sum(
                weight * value
                for weight, value in zip(self._state.action_weights[action_index], features)
            )
            scores.append(score)
        maximum = max(scores)
        for index, score in enumerate(scores):
            if score == maximum:
                return index
        return 0

    def snapshot(self) -> FeaturePolicyState:
        """Return a serializable policy state copy."""
        return FeaturePolicyState(
            feature_names=list(self._state.feature_names),
            action_weights=[list(row) for row in self._state.action_weights],
            action_bias=list(self._state.action_bias),
            step_count=int(self._state.step_count),
            metadata=dict(self._state.metadata),
        )

    def load_snapshot(self, state: FeaturePolicyState) -> None:
        """Load a previously serialized feature policy state."""
        self._state = _validate_state(state, self.action_space_n)

    def update_from_group_advantages(
        self,
        trajectories,
        *,
        ranked: list[CandidateRun],
        learning_rate: float = 0.05,
    ) -> dict[str, float]:
        """Update action bias from group-relative trajectory rewards."""
        if learning_rate < 0:
            raise ValueError("learning_rate must be non-negative")
        advantages = {
            item.name: float(
                item.relative_reward if item.relative_reward is not None else item.reward
            )
            for item in ranked
        }
        before = list(self._state.action_bias)
        for trajectory in trajectories:
            advantage = advantages.get(trajectory.agent_id, trajectory.episode_reward)
            if not trajectory.action_indices:
                continue
            delta = learning_rate * float(advantage) / len(trajectory.action_indices)
            for action_index in trajectory.action_indices:
                if 0 <= int(action_index) < self.action_space_n:
                    self._state.action_bias[int(action_index)] += delta
        self._state.step_count += 1
        delta_norm = math.sqrt(
            sum((after - prior) ** 2 for prior, after in zip(before, self._state.action_bias))
        )
        return {
            "training.policy_step_count": float(self._state.step_count),
            "training.policy_delta_norm": float(delta_norm),
            "training.learning_rate": float(learning_rate),
        }


def normalize_observation_feature(name: str, value: float) -> float:
    """Normalize one TradingEnv observation feature deterministically."""
    numeric = float(value or 0.0)
    if name == "volume":
        return math.log1p(max(numeric, 0.0)) / 20.0
    if name == "close":
        return math.log1p(max(numeric, 0.0)) / 10.0
    return numeric


def _default_action_weights(action_space_n: int, feature_names: list[str]) -> list[list[float]]:
    center = (action_space_n - 1) / 2.0
    weights: list[list[float]] = []
    for action_index in range(action_space_n):
        row = []
        slope = action_index - center
        for name in feature_names:
            if name == "last_return":
                row.append(25.0 * slope)
            elif name == "rolling_vol_5":
                row.append(-2.0 * abs(slope))
            elif name == "position_weight":
                row.append(-0.1 * abs(slope))
            else:
                row.append(0.0)
        weights.append(row)
    return weights


def _validate_state(state: FeaturePolicyState, action_space_n: int) -> FeaturePolicyState:
    if len(state.action_weights) != action_space_n:
        raise ValueError("FeaturePolicyState action_weights length must match action_space_n")
    if len(state.action_bias) != action_space_n:
        raise ValueError("FeaturePolicyState action_bias length must match action_space_n")
    feature_count = len(state.feature_names)
    for row in state.action_weights:
        if len(row) != feature_count:
            raise ValueError("FeaturePolicyState weight rows must match feature_names length")
    return FeaturePolicyState(
        feature_names=list(state.feature_names),
        action_weights=[[float(value) for value in row] for row in state.action_weights],
        action_bias=[float(value) for value in state.action_bias],
        step_count=int(state.step_count),
        metadata=dict(state.metadata),
    )
