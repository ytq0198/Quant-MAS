from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.rl import (
    GRPOPolicyAgent,
    MARLTrainingStub,
    PPOTrainer,
    PolicyState,
    RLTrainingLoop,
    RewardConfig,
    TradingEnv,
    TradingEnvConfig,
    TrajectoryRecord,
    build_synthetic_ohlcv,
    rank_candidates_by_group_relative_reward,
    schedule_walk_forward_eval_stub,
)
from quant_mas.rl.grpo_experiment import CandidateRun
from scripts.run_rl_experiment import run_rl_experiment


def test_grpo_policy_agent_returns_legal_action_index() -> None:
    agent = GRPOPolicyAgent(agent_id="agent", action_space_n=4, seed=42)

    action = agent.act({"last_return": 0.01}, {"date": "2026-01-01"})

    assert 0 <= action < 4


def test_grpo_policy_agent_is_seed_deterministic() -> None:
    first = GRPOPolicyAgent(agent_id="agent", action_space_n=4, seed=7)
    second = GRPOPolicyAgent(agent_id="agent", action_space_n=4, seed=7)

    assert first.act({}, {}) == second.act({}, {})


def test_update_from_group_advantages_updates_policy_state() -> None:
    agent = GRPOPolicyAgent(agent_id="agent", action_space_n=3, seed=42)
    trajectories = [
        TrajectoryRecord("agent_good", 1, [2, 2, 1], [1.0], 1.0),
        TrajectoryRecord("agent_bad", 1, [0, 0, 1], [-1.0], -1.0),
    ]
    ranked = rank_candidates_by_group_relative_reward(
        [
            CandidateRun("agent_good", "agent", 1, 1.0),
            CandidateRun("agent_bad", "agent", 1, -1.0),
        ]
    )

    metrics = agent.update_from_group_advantages(trajectories, ranked=ranked, learning_rate=0.1)

    assert agent.snapshot().step_count == 1
    assert metrics["training.policy_delta_norm"] > 0
    assert agent.snapshot().action_logits[2] > agent.snapshot().action_logits[0]


def test_policy_state_snapshot_round_trip() -> None:
    agent = GRPOPolicyAgent(agent_id="agent", action_space_n=3, initial_logits=[0.1, 0.2, 0.3])
    state = agent.snapshot()
    restored = GRPOPolicyAgent(agent_id="restored", action_space_n=3)

    restored.load_snapshot(PolicyState(**state.__dict__))

    assert restored.snapshot().action_logits == [0.1, 0.2, 0.3]


def test_rl_training_loop_run_completes() -> None:
    result = make_loop().run(max_steps=10, n_groups=2, rollouts_per_group=2, seed=42)

    assert result.algorithm == "grpo"
    assert result.metrics["summary"]["simulation_only"] is True
    assert result.metrics["summary"]["trajectory_count"] == 4


def test_rl_training_loop_metrics_are_simulation_and_training_only() -> None:
    result = make_loop().run(max_steps=10, n_groups=2, rollouts_per_group=2, seed=42)
    payload = json.dumps(result.metrics)

    assert "policy_step_count" in result.metrics["training"]
    assert "sharpe_mean" in result.metrics["simulation"]
    assert '"oos.sharpe"' not in payload
    assert '"oos.total_return"' not in payload
    assert '"oos"' not in result.metrics


def test_grpo_ranking_integration_is_used_for_trajectories() -> None:
    result = make_loop().run(max_steps=10, n_groups=2, rollouts_per_group=2, seed=42)

    assert result.metrics["summary"]["ranked_count"] == 4
    assert result.metrics["ranking"]["top_candidate"] is not None


def test_save_checkpoint_writes_expected_files(tmp_path: Path) -> None:
    loop = make_loop()
    result = loop.run(max_steps=5, n_groups=1, rollouts_per_group=2)

    artifacts = loop.save_checkpoint(tmp_path / "rl_training", result)

    for key in ("policy_state", "metrics", "summary"):
        assert Path(artifacts[key]).exists()
    metrics = json.loads(Path(artifacts["metrics"]).read_text(encoding="utf-8"))
    assert metrics["summary"]["simulation_only"] is True


def test_ppo_trainer_stub_returns_metrics() -> None:
    metrics = PPOTrainer().train_step([])

    assert metrics == {"training.ppo_stub": 1.0, "training.loss": 0.0}


def test_rl_training_loop_ppo_path_uses_stub() -> None:
    config = training_config()
    config["rl_training"]["algorithm"] = "ppo"

    result = make_loop(config=config).run(max_steps=5, n_groups=1, rollouts_per_group=2)

    assert result.algorithm == "ppo"
    assert result.metrics["training"]["ppo_stub"] == 1.0


def test_marl_training_stub_is_explicit() -> None:
    with pytest.raises(NotImplementedError, match="future milestone"):
        MARLTrainingStub().train_joint([], None)


def test_walk_forward_eval_stub_does_not_write_oos() -> None:
    result = schedule_walk_forward_eval_stub(candidate_id="candidate")

    assert result["status"] == "stub"
    assert result["artifacts"] == {}
    assert "oos." not in json.dumps(result)


def test_export_strategy_candidate_stub_does_not_write_oos() -> None:
    result = make_loop().export_strategy_candidate_stub()

    assert result["status"] == "stub"
    assert result["artifacts"] == {}
    assert "metrics" not in result


def test_run_rl_experiment_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_rl_experiment.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--algorithm" in result.stdout
    assert "--no-dry-run" in result.stdout


def test_run_rl_experiment_dry_run(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)

    result = run_rl_experiment(
        config_path=config_path,
        algorithm="grpo",
        max_steps=5,
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["artifacts"] == {}
    assert result["metrics"]["summary"]["algorithm"] == "grpo"


def test_run_rl_experiment_non_dry_run_writes_memory(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    memory_path = tmp_path / "experiments.json"
    output_dir = tmp_path / "outputs"

    result = run_rl_experiment(
        config_path=config_path,
        algorithm="grpo",
        max_steps=5,
        output_dir=output_dir,
        memory_path=memory_path,
        dry_run=False,
    )

    assert Path(result["artifacts"]["policy_state"]).exists()
    latest = ExperimentMemory(memory_path).latest()
    assert latest.params["family"] == "rl_training"
    assert latest.metrics["summary"]["simulation_only"] is True
    assert "oos" not in latest.metrics


def make_loop(config: dict | None = None) -> RLTrainingLoop:
    env_config = TradingEnvConfig(max_steps=16)
    env = TradingEnv(
        build_synthetic_ohlcv(n_bars=32),
        config=env_config,
        reward_config=RewardConfig(),
    )
    policy = GRPOPolicyAgent(agent_id="grpo_policy", action_space_n=env.action_space_n, seed=42)
    return RLTrainingLoop(env=env, policy=policy, config=config or training_config())


def training_config() -> dict:
    return {
        "rl_training": {
            "simulation_only": True,
            "algorithm": "grpo",
            "max_steps": 10,
            "n_groups": 2,
            "rollouts_per_group": 2,
            "learning_rate": 0.05,
            "seed": 42,
            "baseline_experiment_id": "EXP-20260602-008",
            "baseline_oos_sharpe": 0.586,
        },
        "experiment": {"name": "rl_training_test", "family": "rl_training"},
    }


def write_config(tmp_path: Path) -> Path:
    config = training_config()
    config["env"] = {
        "initial_cash": 100000.0,
        "action_levels": [0.0, 0.25, 0.5, 1.0],
        "commission_rate": 0.0005,
        "slippage_bps": 1.0,
        "max_steps": 16,
    }
    config["reward"] = {}
    config["paths"] = {"market_data": None, "output_dir": str(tmp_path / "outputs")}
    path = tmp_path / "rl_training.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
