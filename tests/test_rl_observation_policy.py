from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.research import StrategyCandidate, run_candidate_walk_forward
from quant_mas.research.candidate_validation import CandidateStrategyAdapter
from quant_mas.rl import (
    FeatureLinearPolicyAgent,
    FeaturePolicyState,
    RLTrainingLoop,
    RewardConfig,
    TradingEnv,
    TradingEnvConfig,
    build_synthetic_ohlcv,
    export_policy_candidate,
)


def test_feature_policy_changes_action_with_observation() -> None:
    agent = FeatureLinearPolicyAgent(agent_id="feature", action_space_n=4)

    down = agent.act({"last_return": -0.02}, {})
    up = agent.act({"last_return": 0.02}, {})

    assert down != up
    assert down < up


def test_feature_policy_snapshot_round_trip() -> None:
    agent = FeatureLinearPolicyAgent(agent_id="feature", action_space_n=3)
    state = agent.snapshot()
    restored = FeatureLinearPolicyAgent(agent_id="restored", action_space_n=3)

    restored.load_snapshot(state)

    assert restored.snapshot() == state


def test_feature_policy_update_increments_step_count() -> None:
    from quant_mas.rl import TrajectoryRecord, rank_candidates_by_group_relative_reward
    from quant_mas.rl.grpo_experiment import CandidateRun

    agent = FeatureLinearPolicyAgent(agent_id="feature", action_space_n=3)
    trajectories = [TrajectoryRecord("good", 1, [2, 2], [1.0], 1.0)]
    ranked = rank_candidates_by_group_relative_reward([CandidateRun("good", "feature", 1, 1.0)])

    metrics = agent.update_from_group_advantages(trajectories, ranked=ranked)

    assert agent.snapshot().step_count == 1
    assert "training.policy_step_count" in metrics


def test_training_loop_supports_feature_linear_policy() -> None:
    env = TradingEnv(
        build_synthetic_ohlcv(n_bars=32),
        config=TradingEnvConfig(max_steps=16),
        reward_config=RewardConfig(),
    )
    policy = FeatureLinearPolicyAgent(agent_id="feature", action_space_n=env.action_space_n)
    loop = RLTrainingLoop(env=env, policy=policy, config=training_config("feature_linear"))

    result = loop.run(max_steps=10, n_groups=1, rollouts_per_group=2)

    assert result.policy_state.metadata["policy_type"] == "feature_linear"
    assert result.metrics["summary"]["simulation_only"] is True


def test_training_loop_feature_metrics_do_not_contain_oos() -> None:
    env = TradingEnv(build_synthetic_ohlcv(n_bars=32), config=TradingEnvConfig(max_steps=16))
    policy = FeatureLinearPolicyAgent(agent_id="feature", action_space_n=env.action_space_n)

    result = RLTrainingLoop(env=env, policy=policy, config=training_config("feature_linear")).run(max_steps=5)

    assert "oos" not in result.metrics
    assert "oos." not in json.dumps(result.metrics)


def test_run_rl_experiment_feature_linear_dry_run() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_rl_experiment.py",
            "--config",
            "configs/rl_training.yaml",
            "--policy-type",
            "feature_linear",
            "--max-steps",
            "10",
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "feature_names" in result.stdout


def test_export_supports_feature_policy_state(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_feature_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
    )

    assert candidate.agent_type == "feature_linear_policy"
    assert candidate.params["policy_type"] == "feature_linear"


def test_export_feature_policy_ignores_stale_grpo_agent_type(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_feature_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
        agent_type="grpo_policy",
    )

    assert candidate.agent_type == "feature_linear_policy"


def test_feature_linear_adapter_works_when_agent_type_mislabeled() -> None:
    candidate = make_feature_candidate()
    mislabeled = StrategyCandidate(
        candidate_id=candidate.candidate_id,
        source=candidate.source,
        agent_id=candidate.agent_id,
        agent_type="grpo_policy",
        params=candidate.params,
        selection_metrics=candidate.selection_metrics,
    )

    signals = CandidateStrategyAdapter(mislabeled).generate_signals(make_features())

    assert signals["target_weight"].nunique() > 1


def test_exported_feature_candidate_contains_weights(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_feature_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
    )

    assert candidate.params["feature_names"] == ["last_return"]
    assert candidate.params["action_weights"] == [[-100.0], [100.0]]
    assert candidate.params["action_levels"] == [0.0, 0.25, 0.5, 1.0]


def test_feature_linear_candidate_adapter_generates_non_constant_weights() -> None:
    candidate = make_feature_candidate()

    signals = CandidateStrategyAdapter(candidate).generate_signals(make_features())

    assert signals["target_weight"].nunique() > 1


def test_feature_linear_candidate_adapter_ignores_future_labels() -> None:
    frame = make_features()
    frame["future_direction_5"] = 1
    frame["future_return_5"] = 0.01

    signals = CandidateStrategyAdapter(make_feature_candidate()).generate_signals(frame)

    assert signals["target_weight"].between(0.0, 1.0).all()
    assert signals["target_weight"].nunique() > 1


def test_feature_linear_candidate_walk_forward_runs() -> None:
    result = run_candidate_walk_forward(
        make_feature_candidate(),
        make_features(days=36),
        config=candidate_oos_config(),
    )

    assert result.metrics["summary"]["agent_type"] == "feature_linear_policy"
    assert "sharpe" in result.metrics["oos"]


def test_feature_policy_state_round_trip_json(tmp_path: Path) -> None:
    state = FeaturePolicyState(
        feature_names=["last_return"],
        action_weights=[[-1.0], [1.0]],
        action_bias=[0.0, 0.0],
        step_count=2,
        metadata={"agent_id": "feature"},
    )
    path = tmp_path / "state.json"
    path.write_text(json.dumps(state.__dict__), encoding="utf-8")

    candidate = export_policy_candidate(policy_state_path=path, metrics_path=write_metrics(tmp_path))

    assert candidate.agent_id == "feature"


def make_feature_candidate() -> StrategyCandidate:
    return StrategyCandidate(
        candidate_id="feature_candidate",
        source="rl_training",
        agent_id="feature_policy",
        agent_type="feature_linear_policy",
        params={
            "policy_type": "feature_linear",
            "feature_names": ["last_return"],
            "action_weights": [[-100.0], [100.0]],
            "action_bias": [0.0, 0.0],
            "action_levels": [0.0, 1.0],
            "step_count": 1,
        },
        selection_metrics={"training.policy_step_count": 1.0},
    )


def make_features(days: int = 12) -> pd.DataFrame:
    rows = []
    close = 100.0
    for index in range(days):
        close *= 1.02 if index % 2 else 0.98
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close * 0.999,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "volume": 1000 + index,
            }
        )
    return pd.DataFrame(rows)


def candidate_oos_config() -> dict[str, Any]:
    return {
        "candidate_oos": {
            "baseline_experiment_id": "EXP-20260602-008",
            "baseline_oos_sharpe": 0.586,
        },
        "walk_forward": {
            "train_window": 12,
            "validation_window": 4,
            "test_window": 4,
            "oos_window": 4,
            "step": 4,
            "max_windows": 2,
        },
        "portfolio": {"initial_cash": 1000.0},
        "costs": {"commission_bps": 0.0, "slippage_bps": 0.0},
    }


def training_config(policy_type: str) -> dict[str, Any]:
    return {
        "rl_training": {
            "algorithm": "grpo",
            "learning_rate": 0.05,
            "baseline_experiment_id": "EXP-20260602-008",
            "baseline_oos_sharpe": 0.586,
        },
        "policy": {"type": policy_type},
    }


def write_feature_policy_state(tmp_path: Path) -> Path:
    path = tmp_path / "policy_state.json"
    path.write_text(
        json.dumps(
            {
                "feature_names": ["last_return"],
                "action_weights": [[-100.0], [100.0]],
                "action_bias": [0.0, 0.0],
                "step_count": 2,
                "metadata": {"agent_id": "feature_policy", "simulation_only": True},
            }
        ),
        encoding="utf-8",
    )
    return path


def write_metrics(tmp_path: Path) -> Path:
    path = tmp_path / "metrics.json"
    path.write_text(
        json.dumps(
            {
                "summary": {
                    "algorithm": "grpo",
                    "simulation_only": True,
                    "baseline_experiment_id": "EXP-20260602-008",
                    "baseline_oos_sharpe": 0.586,
                },
                "training": {"policy_step_count": 2, "policy_delta_norm": 0.1},
                "simulation": {"sharpe_mean": 1.0, "total_return_mean": 0.1},
            }
        ),
        encoding="utf-8",
    )
    return path
