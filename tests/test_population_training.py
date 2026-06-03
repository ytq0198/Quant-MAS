from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from quant_mas.agents import (
    AgentSpec,
    MeanReversionAgent,
    MomentumAgent,
    PopulationManager,
    RiskAgent,
)
from quant_mas.memory import ExperimentMemory
from quant_mas.risk import RiskLimits
from quant_mas.rl import (
    CandidateRun,
    CompetitiveEpisodeRunner,
    CompetitiveRunConfig,
    build_synthetic_ohlcv,
    expected_score,
    rank_candidates_by_group_relative_reward,
    update_pair,
)
from scripts.run_competitive_experiment import run_competitive_experiment


def test_momentum_agent_propose_is_deterministic() -> None:
    agent = MomentumAgent("mom", scale=1.0)
    observation = {"last_return": 0.01}

    first = agent.propose(observation, {})
    second = agent.propose(observation, {})

    assert first == second
    assert first.target_weight > 0.5


def test_mean_reversion_differs_from_momentum() -> None:
    observation = {"last_return": 0.01}

    momentum = MomentumAgent("mom").propose(observation, {})
    mean_reversion = MeanReversionAgent("mr").propose(observation, {})

    assert momentum.target_weight > mean_reversion.target_weight


def test_risk_agent_clips_overweight_proposal() -> None:
    proposal = MomentumAgent("mom", scale=10.0).propose({"last_return": 0.1}, {})
    risk_agent = RiskAgent(RiskLimits(max_position_weight=0.2, require_human_approval=False))

    adjusted = risk_agent.apply(proposal, current_weight=0.0, equity=100_000.0)

    assert adjusted.target_weight == 0.2
    assert "max_position_weight_exceeded" in adjusted.metadata["risk_violations"]


def test_elo_update_stronger_winner_still_rises() -> None:
    strong, weak = update_pair(1600.0, 1400.0, score_a=1.0)

    assert expected_score(1600.0, 1400.0) > 0.5
    assert strong > 1600.0
    assert weak < 1400.0


def test_population_rankings_tie_break_by_agent_id() -> None:
    population = PopulationManager()
    population.register(AgentSpec("b_agent", "momentum"))
    population.register(AgentSpec("a_agent", "momentum"))

    assert [spec.agent_id for spec in population.rankings()] == ["a_agent", "b_agent"]


def test_population_top_k_after_match() -> None:
    population = make_population()

    population.record_match("momentum_1", "mean_rev_1", window_id=0)

    assert population.top_k(1)[0].agent_id == "momentum_1"


def test_next_generation_is_deterministic_and_renames_agents() -> None:
    population = make_population()
    population.record_match("momentum_1", "mean_rev_1", window_id=0)

    generated = population.next_generation(mutate_sigma=0.05)

    assert generated[0].agent_id.startswith("momentum_1_g1_")
    assert generated[0].params["scale"] > 1.0
    assert population.generation == 1


def test_competitive_runner_run_mock_returns_rankings() -> None:
    runner = make_runner()

    summary = runner.run_mock()

    assert summary["simulation_only"] is True
    assert summary["rankings"]
    assert "population" in summary["metrics"]
    assert "simulation" in summary["metrics"]


def test_competitive_experiment_writes_memory(tmp_path: Path) -> None:
    config_path = write_competitive_config(tmp_path)
    memory_path = tmp_path / "experiments.json"

    result = run_competitive_experiment(
        config_path=config_path,
        dry_run=False,
        output_dir=tmp_path / "competitive",
        memory_path=memory_path,
    )

    assert result["experiment_id"]
    latest = ExperimentMemory(memory_path).latest()
    assert latest.params["family"] == "competitive_learning"
    assert latest.metrics["population"]["top_agent"]


def test_competitive_metrics_do_not_contain_oos_sharpe(tmp_path: Path) -> None:
    config_path = write_competitive_config(tmp_path)

    result = run_competitive_experiment(
        config_path=config_path,
        dry_run=True,
        output_dir=tmp_path / "competitive",
    )

    payload = json.dumps(result["metrics"]).lower()
    assert "oos" not in payload


def test_competitive_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_competitive_experiment.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--dry-run" in result.stdout


def test_competitive_cli_dry_run_mock(tmp_path: Path) -> None:
    config_path = write_competitive_config(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_competitive_experiment.py",
            "--config",
            str(config_path),
            "--mode",
            "mock",
            "--dry-run",
            "--output-dir",
            str(tmp_path / "competitive"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "simulation_only" in result.stdout


def test_grpo_ranking_integration_smoke() -> None:
    ranked = rank_candidates_by_group_relative_reward(
        [
            CandidateRun("momentum_1", "momentum", 0, 1.0),
            CandidateRun("mean_rev_1", "mean_reversion", 0, 0.5),
        ]
    )

    assert ranked[0].name == "momentum_1"
    assert ranked[0].relative_reward and ranked[0].relative_reward > 0


def make_population() -> PopulationManager:
    population = PopulationManager(top_k_size=2)
    population.register(
        AgentSpec("momentum_1", "momentum", {"lookback": 5, "scale": 1.0})
    )
    population.register(
        AgentSpec("mean_rev_1", "mean_reversion", {"lookback": 5, "scale": 1.0})
    )
    return population


def make_runner() -> CompetitiveEpisodeRunner:
    return CompetitiveEpisodeRunner(
        agents=[MomentumAgent("momentum_1"), MeanReversionAgent("mean_rev_1")],
        risk_agent=RiskAgent(RiskLimits(max_position_weight=1.0, require_human_approval=False)),
        population=make_population(),
        config=CompetitiveRunConfig(n_windows=2, bars_per_window=16, seed=7),
        market_data=build_synthetic_ohlcv(40),
    )


def write_competitive_config(tmp_path: Path) -> Path:
    config = {
        "competitive": {
            "simulation_only": True,
            "mode": "mock",
            "seed": 7,
            "n_windows": 2,
            "bars_per_window": 16,
            "top_k": 2,
        },
        "population": {"initial_elo": 1500.0, "k_factor": 32.0, "mutate_sigma": 0.05},
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
        "paths": {"market_data": None, "output_dir": str(tmp_path / "competitive")},
        "experiment": {"name": "competitive_test", "family": "competitive_learning"},
        "memory": {"json_path": str(tmp_path / "experiments.json")},
        "baseline": {"oos_reference": "EXP-20260602-008", "oos_sharpe": 0.586},
    }
    path = tmp_path / "competitive.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
