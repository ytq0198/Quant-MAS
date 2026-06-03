from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from quant_mas.agents import AgentSpec, RiskAgent
from quant_mas.memory import ExperimentMemory
from quant_mas.risk import RiskLimits
from quant_mas.rl import (
    PopulationTrainingConfig,
    PopulationTrainingLoop,
    build_synthetic_ohlcv,
)
from scripts.run_population_training import run_population_training_from_config


def test_population_training_config_validates() -> None:
    with pytest.raises(ValueError, match="generations"):
        PopulationTrainingConfig(generations=0)
    with pytest.raises(ValueError, match="top_k"):
        PopulationTrainingConfig(top_k=0)
    with pytest.raises(ValueError, match="simulation-only"):
        PopulationTrainingConfig(simulation_only=False)


def test_population_training_single_generation_runs() -> None:
    result = make_loop(generations=1).run(dry_run=True)

    assert len(result["generations"]) == 1
    assert result["best_agent"]
    assert result["metrics"]["population"]["generations"] == 1.0


def test_population_training_multi_generation_runs() -> None:
    result = make_loop(generations=3).run(dry_run=True)

    assert len(result["generations"]) == 3
    assert result["metrics"]["population"]["generations"] == 3.0


def test_each_generation_has_rankings() -> None:
    result = make_loop(generations=2).run(dry_run=True)

    assert all(generation["rankings"] for generation in result["generations"])


def test_next_generation_produces_new_agent_ids() -> None:
    result = make_loop(generations=2).run(dry_run=True)
    second_generation_ids = {
        item["agent_id"] for item in result["generations"][1]["rankings"]
    }

    assert any("_g1_" in agent_id for agent_id in second_generation_ids)


def test_population_training_metrics_do_not_contain_oos() -> None:
    result = make_loop(generations=2).run(dry_run=True)

    assert "oos" not in json.dumps(result["metrics"]).lower()


def test_dry_run_does_not_write_experiment_memory(tmp_path: Path) -> None:
    memory_path = tmp_path / "experiments.json"

    result = make_loop(generations=1, output_dir=tmp_path / "out").run(
        dry_run=True,
        memory_path=memory_path,
    )

    assert result["experiment_id"] is None
    assert not memory_path.exists()


def test_non_dry_run_writes_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "population"

    result = make_loop(generations=2, output_dir=output_dir).run(
        dry_run=False,
        memory_path=tmp_path / "experiments.json",
    )

    assert (output_dir / "generation_001_metrics.json").exists()
    assert (output_dir / "generation_002_metrics.json").exists()
    assert (output_dir / "rankings.csv").exists()
    assert (output_dir / "summary.md").exists()
    assert "summary" in result["artifacts"]


def test_non_dry_run_writes_experiment_memory(tmp_path: Path) -> None:
    memory_path = tmp_path / "experiments.json"

    result = make_loop(generations=2, output_dir=tmp_path / "population").run(
        dry_run=False,
        memory_path=memory_path,
        experiment_name="population_training_test",
    )

    latest = ExperimentMemory(memory_path).latest()
    assert result["experiment_id"] == latest.experiment_id
    assert latest.name == "population_training_test"
    assert latest.params["family"] == "competitive_learning"
    assert "oos" not in json.dumps(latest.metrics).lower()


def test_population_training_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_population_training.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--generations" in result.stdout


def test_population_training_cli_dry_run(tmp_path: Path) -> None:
    config_path = write_population_training_config(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_population_training.py",
            "--config",
            str(config_path),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "simulation_only" in result.stdout
    assert not (tmp_path / "experiments.json").exists()


def test_run_population_training_from_config_writes_memory(tmp_path: Path) -> None:
    config_path = write_population_training_config(tmp_path)

    result = run_population_training_from_config(
        config_path=config_path,
        dry_run=False,
        output_dir=tmp_path / "population",
        memory_path=tmp_path / "experiments.json",
        generations=2,
    )

    assert result["experiment_id"]
    assert (tmp_path / "population" / "summary.md").exists()


def make_loop(
    *,
    generations: int,
    output_dir: Path | None = None,
) -> PopulationTrainingLoop:
    return PopulationTrainingLoop(
        initial_specs=make_specs(),
        config=PopulationTrainingConfig(
            generations=generations,
            n_windows=2,
            bars_per_window=16,
            top_k=2,
            seed=7,
            output_dir=output_dir or Path("outputs/test_population_training"),
        ),
        risk_agent=RiskAgent(RiskLimits(max_position_weight=1.0, require_human_approval=False)),
        market_data=build_synthetic_ohlcv(40),
    )


def make_specs() -> list[AgentSpec]:
    return [
        AgentSpec("momentum_1", "momentum", {"lookback": 5, "scale": 1.0}),
        AgentSpec("mean_rev_1", "mean_reversion", {"lookback": 5, "scale": 1.0}),
    ]


def write_population_training_config(tmp_path: Path) -> Path:
    config = {
        "population_training": {
            "simulation_only": True,
            "generations": 2,
            "n_windows": 2,
            "bars_per_window": 16,
            "top_k": 2,
            "mutate_sigma": 0.05,
            "seed": 7,
        },
        "agents": [
            {"id": "momentum_1", "type": "momentum", "params": {"lookback": 5, "scale": 1.0}},
            {
                "id": "mean_rev_1",
                "type": "mean_reversion",
                "params": {"lookback": 5, "scale": 1.0},
            },
        ],
        "risk": {
            "max_position_weight": 1.0,
            "max_total_exposure": 1.0,
            "max_drawdown": 0.2,
            "allow_short": False,
            "require_human_approval": False,
        },
        "paths": {"market_data": None, "output_dir": str(tmp_path / "population")},
        "experiment": {"name": "population_training_test", "family": "competitive_learning"},
        "memory": {"json_path": str(tmp_path / "experiments.json")},
        "baseline": {"oos_reference": "EXP-20260602-008", "oos_sharpe": 0.586},
    }
    path = tmp_path / "population_training.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
