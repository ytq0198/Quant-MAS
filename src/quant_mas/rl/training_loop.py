"""Simulation-only RL training loop for Quant MAS M12."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.rl.grpo_agent import GRPOPolicyAgent, PolicyState
from quant_mas.rl.grpo_experiment import (
    CandidateRun,
    rank_candidates_by_group_relative_reward,
)
from quant_mas.rl.ppo_trainer import PPOTrainer
from quant_mas.rl.trading_env import TradingEnv


@dataclass(frozen=True)
class TrajectoryRecord:
    """One simulation rollout collected from TradingEnv."""

    agent_id: str
    window_id: int
    action_indices: list[int]
    rewards: list[float]
    episode_reward: float
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingRunResult:
    """RL training result and optional artifacts."""

    algorithm: str
    metrics: dict[str, Any]
    policy_state: PolicyState
    artifacts: dict[str, str] = field(default_factory=dict)


class RLTrainingLoop:
    """Short, deterministic, simulation-only RL training loop."""

    def __init__(
        self,
        *,
        env: TradingEnv,
        policy: GRPOPolicyAgent,
        config: dict[str, Any],
        risk_agent: Any | None = None,
    ) -> None:
        self.env = env
        self.policy = policy
        self.config = config
        self.risk_agent = risk_agent
        self._latest_result: TrainingRunResult | None = None

    def run(
        self,
        *,
        max_steps: int = 10,
        n_groups: int = 2,
        rollouts_per_group: int = 2,
        seed: int = 42,
    ) -> TrainingRunResult:
        """Collect rollouts, rank group-relative rewards, and update policy."""
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if n_groups <= 0 or rollouts_per_group <= 0:
            raise ValueError("n_groups and rollouts_per_group must be positive")

        algorithm = str(self.config.get("rl_training", {}).get("algorithm", "grpo")).lower()
        learning_rate = float(self.config.get("rl_training", {}).get("learning_rate", 0.05))
        baseline_id = self.config.get("rl_training", {}).get(
            "baseline_experiment_id",
            "EXP-20260602-008",
        )
        baseline_sharpe = float(self.config.get("rl_training", {}).get("baseline_oos_sharpe", 0.586))

        trajectories: list[TrajectoryRecord] = []
        candidates: list[CandidateRun] = []
        for group_index in range(n_groups):
            for rollout_index in range(rollouts_per_group):
                trajectory = self._collect_rollout(
                    window_id=group_index + 1,
                    rollout_index=rollout_index,
                    max_steps=max_steps,
                    seed=seed + group_index * 100 + rollout_index,
                )
                trajectories.append(trajectory)
                candidates.append(
                    CandidateRun(
                        name=trajectory.agent_id,
                        policy=self.policy.agent_id,
                        window_id=trajectory.window_id,
                        reward=trajectory.episode_reward,
                        metrics=trajectory.metrics,
                    )
                )

        ranked = rank_candidates_by_group_relative_reward(candidates)
        if algorithm == "ppo":
            update_metrics = PPOTrainer().train_step(trajectories)
            update_metrics["training.policy_step_count"] = float(self.policy.snapshot().step_count)
            update_metrics["training.policy_delta_norm"] = 0.0
        elif algorithm == "grpo":
            update_metrics = self.policy.update_from_group_advantages(
                trajectories,
                ranked=ranked,
                learning_rate=learning_rate,
            )
        else:
            raise ValueError("algorithm must be grpo or ppo")

        metrics = {
            "summary": {
                "algorithm": algorithm,
                "simulation_only": True,
                "baseline_experiment_id": baseline_id,
                "baseline_oos_sharpe": baseline_sharpe,
                "trajectory_count": len(trajectories),
                "ranked_count": len(ranked),
                "seed": int(seed),
            },
            "training": _strip_prefix(update_metrics, "training."),
            "simulation": _aggregate_simulation_metrics(trajectories),
            "ranking": {
                "top_candidate": ranked[0].name if ranked else None,
                "top_relative_reward": float(ranked[0].relative_reward) if ranked else None,
            },
        }
        result = TrainingRunResult(
            algorithm=algorithm,
            metrics=metrics,
            policy_state=self.policy.snapshot(),
        )
        self._latest_result = result
        return result

    def save_checkpoint(
        self,
        output_dir: str | Path,
        result: TrainingRunResult | None = None,
    ) -> dict[str, str]:
        """Write policy state, metrics, and summary markdown."""
        selected = result or self._latest_result
        if selected is None:
            raise ValueError("No training result available to save")
        target = Path(output_dir).expanduser()
        target.mkdir(parents=True, exist_ok=True)
        policy_path = target / "policy_state.json"
        metrics_path = target / "metrics.json"
        summary_path = target / "summary.md"
        policy_path.write_text(
            json.dumps(asdict(selected.policy_state), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        metrics_path.write_text(
            json.dumps(selected.metrics, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        summary_path.write_text(_summary_markdown(selected), encoding="utf-8")
        artifacts = {
            "policy_state": str(policy_path),
            "metrics": str(metrics_path),
            "summary": str(summary_path),
        }
        self._latest_result = TrainingRunResult(
            algorithm=selected.algorithm,
            metrics=selected.metrics,
            policy_state=selected.policy_state,
            artifacts=artifacts,
        )
        return artifacts

    def export_strategy_candidate_stub(self) -> dict[str, Any]:
        """Return a documented bridge stub; no OOS metrics are produced."""
        return {
            "status": "stub",
            "simulation_only": True,
            "message": "Export trained policy to StrategyCandidate, then validate with M11.7/M11.8.",
            "next_scripts": [
                "scripts/validate_candidate_oos.py",
                "scripts/batch_validate_candidates.py",
            ],
            "artifacts": {},
        }

    def _collect_rollout(
        self,
        *,
        window_id: int,
        rollout_index: int,
        max_steps: int,
        seed: int,
    ) -> TrajectoryRecord:
        observation, info = self.env.reset(seed=seed)
        actions: list[int] = []
        rewards: list[float] = []
        while len(actions) < max_steps:
            base_action = self.policy.act(observation, info)
            action = int((base_action + rollout_index) % self.env.action_space_n)
            step = self.env.step(action)
            actions.append(action)
            rewards.append(float(step.reward))
            observation = step.observation
            info = step.info
            if step.terminated or step.truncated:
                break
        summary = self.env.render_episode_summary()
        metrics = {
            "simulation.total_return": float(summary["total_return"]),
            "simulation.sharpe": float(summary["sharpe"]),
            "simulation.max_drawdown": float(summary["max_drawdown"]),
            "simulation.final_equity": float(summary["final_equity"]),
        }
        return TrajectoryRecord(
            agent_id=f"{self.policy.agent_id}_g{window_id}_r{rollout_index + 1}",
            window_id=int(window_id),
            action_indices=actions,
            rewards=rewards,
            episode_reward=float(sum(rewards)),
            metrics=metrics,
        )


def schedule_walk_forward_eval_stub(**kwargs) -> dict[str, Any]:
    """Document-only hook pointing to M11.7/M11.8 OOS validation."""
    return {
        "status": "stub",
        "simulation_only": True,
        "message": "Use M11.7/M11.8 scripts for OOS validation after policy export.",
        "kwargs": {key: str(value) for key, value in kwargs.items()},
        "artifacts": {},
    }


def _aggregate_simulation_metrics(trajectories: list[TrajectoryRecord]) -> dict[str, float]:
    if not trajectories:
        return {
            "episode_reward_mean": 0.0,
            "sharpe_mean": 0.0,
            "total_return_mean": 0.0,
            "max_drawdown_mean": 0.0,
        }
    frame = pd.DataFrame([trajectory.metrics for trajectory in trajectories])
    return {
        "episode_reward_mean": float(
            sum(trajectory.episode_reward for trajectory in trajectories) / len(trajectories)
        ),
        "sharpe_mean": float(frame["simulation.sharpe"].mean()),
        "total_return_mean": float(frame["simulation.total_return"].mean()),
        "max_drawdown_mean": float(frame["simulation.max_drawdown"].mean()),
    }


def _strip_prefix(metrics: dict[str, float], prefix: str) -> dict[str, float]:
    return {
        key.removeprefix(prefix): float(value)
        for key, value in metrics.items()
        if key.startswith(prefix)
    }


def _summary_markdown(result: TrainingRunResult) -> str:
    summary = result.metrics["summary"]
    simulation = result.metrics["simulation"]
    training = result.metrics["training"]
    return "\n".join(
        [
            "# RL Training Experiment",
            "",
            "**simulation_only:** true",
            "",
            f"- algorithm: {summary['algorithm']}",
            f"- baseline_experiment_id: {summary['baseline_experiment_id']}",
            f"- baseline_oos_sharpe: {summary['baseline_oos_sharpe']}",
            f"- training.policy_step_count: {training.get('policy_step_count')}",
            f"- simulation.sharpe_mean: {simulation.get('sharpe_mean')}",
            f"- simulation.total_return_mean: {simulation.get('total_return_mean')}",
            "",
            "This is a simulation-only RL training artifact. OOS validation must use M11.7/M11.8.",
            "",
        ]
    )
