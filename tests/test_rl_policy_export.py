from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.research import StrategyCandidate
from quant_mas.rl import (
    export_policy_candidate,
    load_policy_state,
    load_training_metrics,
    write_rl_candidates,
)
from scripts.export_rl_policy_candidate import export_rl_policy_candidate


def test_load_policy_state_round_trip(tmp_path: Path) -> None:
    policy_path = write_policy_state(tmp_path)

    state = load_policy_state(policy_path)

    assert state.action_logits == [0.1, -0.2, 0.3]
    assert state.step_count == 3
    assert state.metadata["agent_id"] == "grpo_policy_001"


def test_load_training_metrics(tmp_path: Path) -> None:
    metrics_path = write_metrics(tmp_path)

    metrics = load_training_metrics(metrics_path)

    assert metrics["training"]["policy_step_count"] == 3
    assert metrics["simulation"]["sharpe_mean"] == 1.23


def test_export_policy_candidate_fields(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
    )

    assert candidate.source == "rl_training"
    assert candidate.agent_id == "grpo_policy_001"
    assert candidate.agent_type == "grpo_policy"
    assert candidate.candidate_id == "rl_grpo_policy_001_3"


def test_export_policy_candidate_params_include_policy_state(tmp_path: Path) -> None:
    policy_path = write_policy_state(tmp_path)

    candidate = export_policy_candidate(
        policy_state_path=policy_path,
        metrics_path=write_metrics(tmp_path),
    )

    assert candidate.params["policy_state_path"] == str(policy_path)
    assert candidate.params["action_logits"] == [0.1, -0.2, 0.3]
    assert candidate.params["step_count"] == 3
    assert candidate.params["action_policy"] == "discrete_logits"


def test_export_policy_candidate_selection_metrics(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
    )

    assert candidate.selection_metrics["training.policy_step_count"] == 3
    assert candidate.selection_metrics["simulation.sharpe_mean"] == 1.23
    assert candidate.selection_metrics["summary.baseline_oos_sharpe"] == 0.586
    assert "oos" not in candidate.selection_metrics


def test_export_rejects_top_level_oos(tmp_path: Path) -> None:
    metrics_path = write_metrics(tmp_path, extra={"oos": {"sharpe": 9.0}})

    with pytest.raises(ValueError, match="oos"):
        export_policy_candidate(
            policy_state_path=write_policy_state(tmp_path),
            metrics_path=metrics_path,
        )


def test_export_rejects_dotted_oos_metric(tmp_path: Path) -> None:
    metrics_path = write_metrics(tmp_path, extra={"oos.sharpe": 9.0})

    with pytest.raises(ValueError, match="oos"):
        load_training_metrics(metrics_path)


def test_write_rl_candidates_writes_artifacts(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
    )

    artifacts = write_rl_candidates([candidate], tmp_path / "rl_candidates")

    for key in ("candidates_json", "candidates_csv", "summary"):
        assert Path(artifacts[key]).exists()
    payload = json.loads(Path(artifacts["candidates_json"]).read_text(encoding="utf-8"))
    restored = StrategyCandidate.from_dict(payload[0])
    assert restored.candidate_id == candidate.candidate_id


def test_export_rl_policy_candidate_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/export_rl_policy_candidate.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--policy-state" in result.stdout
    assert "--no-dry-run" in result.stdout


def test_export_rl_policy_candidate_dry_run_writes_nothing(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    output_dir = tmp_path / "rl_candidates"

    result = export_rl_policy_candidate(
        config_path=config_path,
        output_dir=output_dir,
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["artifacts"] == {}
    assert result["candidate"]["source"] == "rl_training"
    assert not output_dir.exists()


def test_export_rl_policy_candidate_non_dry_run_writes_memory(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    output_dir = tmp_path / "rl_candidates"
    memory_path = tmp_path / "experiments.json"

    result = export_rl_policy_candidate(
        config_path=config_path,
        output_dir=output_dir,
        memory_path=memory_path,
        experiment_name="rl_policy_export_test",
        dry_run=False,
    )

    assert Path(result["artifacts"]["candidates_json"]).exists()
    latest = ExperimentMemory(memory_path).latest()
    assert latest.name == "rl_policy_export_test"
    assert latest.params["family"] == "rl_policy_export"
    assert latest.metrics["summary"]["simulation_only"] is True
    assert "oos" not in latest.metrics


def test_output_candidate_can_round_trip_from_json(tmp_path: Path) -> None:
    candidate = export_policy_candidate(
        policy_state_path=write_policy_state(tmp_path),
        metrics_path=write_metrics(tmp_path),
        candidate_id="custom_rl_candidate",
    )

    restored = StrategyCandidate.from_dict(candidate.to_dict())

    assert restored == candidate


def write_policy_state(tmp_path: Path) -> Path:
    path = tmp_path / "policy_state.json"
    path.write_text(
        json.dumps(
            {
                "action_logits": [0.1, -0.2, 0.3],
                "step_count": 3,
                "metadata": {
                    "agent_id": "grpo_policy_001",
                    "seed": 42,
                    "simulation_only": True,
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def write_metrics(tmp_path: Path, *, extra: dict | None = None) -> Path:
    metrics = {
        "summary": {
            "algorithm": "grpo",
            "simulation_only": True,
            "baseline_experiment_id": "EXP-20260602-008",
            "baseline_oos_sharpe": 0.586,
        },
        "training": {
            "policy_step_count": 3,
            "policy_delta_norm": 0.4,
        },
        "simulation": {
            "sharpe_mean": 1.23,
            "total_return_mean": 0.04,
            "max_drawdown_mean": -0.02,
        },
    }
    metrics.update(extra or {})
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")
    return path


def write_config(tmp_path: Path) -> Path:
    config = {
        "rl_policy_export": {
            "policy_state": str(write_policy_state(tmp_path)),
            "metrics": str(write_metrics(tmp_path)),
            "output_dir": str(tmp_path / "rl_candidates"),
            "agent_type": "grpo_policy",
        },
        "experiment": {
            "name": "rl_policy_export_test",
            "family": "rl_policy_export",
            "memory_path": None,
        },
    }
    path = tmp_path / "rl_policy_export.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
