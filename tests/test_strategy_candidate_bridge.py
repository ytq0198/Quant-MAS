from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.research import StrategyCandidate, assert_no_oos_metrics
from quant_mas.rl import (
    extract_top_candidates,
    run_candidate_backtest_smoke,
    walk_forward_stub,
    write_candidates,
)
from scripts.export_population_candidates import export_population_candidates


def test_strategy_candidate_round_trip() -> None:
    candidate = StrategyCandidate(
        candidate_id="cand_mom",
        source="population_training",
        agent_id="mom",
        agent_type="momentum",
        params={"scale": 1.0},
        selection_metrics={"population.elo": 1500.0},
    )

    restored = StrategyCandidate.from_dict(candidate.to_dict())

    assert restored == candidate


def test_assert_no_oos_metrics_rejects_oos() -> None:
    with pytest.raises(ValueError, match="oos"):
        assert_no_oos_metrics({"oos": {"sharpe": 0.5}})
    with pytest.raises(ValueError, match="oos"):
        StrategyCandidate(
            candidate_id="bad",
            source="test",
            agent_id="bad",
            agent_type="momentum",
            validation_metrics={"oos.sharpe": 0.5},
        )


def test_extract_top_candidates_from_population_result() -> None:
    candidates = extract_top_candidates(make_population_result(), top_k=2)

    assert [candidate.agent_id for candidate in candidates] == ["mean_rev_1", "momentum_1"]
    assert candidates[0].selection_metrics["population.rank"] == 1.0
    assert candidates[0].selection_metrics["simulation.reward_mean"] == 7.0


def test_write_candidates_writes_json_and_csv(tmp_path: Path) -> None:
    candidates = extract_top_candidates(make_population_result(), top_k=1)

    artifacts = write_candidates(candidates, tmp_path)

    assert Path(artifacts["candidates_json"]).exists()
    assert Path(artifacts["candidates_csv"]).exists()
    assert "cand_mean_rev_1" in Path(artifacts["candidates_json"]).read_text(encoding="utf-8")


def test_candidate_backtest_smoke_returns_backtest_metrics() -> None:
    candidate = extract_top_candidates(make_population_result(), top_k=1)[0]

    validated = run_candidate_backtest_smoke(candidate)

    assert "backtest.total_return" in validated.validation_metrics
    assert "backtest.sharpe" in validated.validation_metrics
    assert "backtest.max_drawdown" in validated.validation_metrics


def test_candidate_backtest_smoke_does_not_write_oos() -> None:
    candidate = extract_top_candidates(make_population_result(), top_k=1)[0]
    validated = run_candidate_backtest_smoke(candidate)

    assert "oos" not in json.dumps(validated.validation_metrics).lower()


def test_walk_forward_stub_has_no_oos_metrics() -> None:
    candidate = extract_top_candidates(make_population_result(), top_k=1)[0]

    payload = walk_forward_stub(candidate)

    assert payload["status"] == "stub"
    assert "oos" not in json.dumps({"metrics": {}}).lower()
    assert "no oos metrics" in payload["message"].lower()


def test_export_population_candidates_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/export_population_candidates.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--run-backtest-smoke" in result.stdout


def test_export_population_candidates_cli_dry_run(tmp_path: Path) -> None:
    input_path = tmp_path / "population.json"
    input_path.write_text(json.dumps(make_population_result()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_population_candidates.py",
            "--input-result",
            str(input_path),
            "--top-k",
            "1",
            "--run-backtest-smoke",
            "--dry-run",
            "--output-dir",
            str(tmp_path / "candidates"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "cand_mean_rev_1" in result.stdout
    assert not (tmp_path / "candidates" / "candidates.json").exists()


def test_export_population_candidates_non_dry_run_writes_memory(tmp_path: Path) -> None:
    config_path = write_candidate_config(tmp_path)
    input_path = tmp_path / "population.json"
    input_path.write_text(json.dumps(make_population_result()), encoding="utf-8")

    result = export_population_candidates(
        config_path=config_path,
        input_result=input_path,
        top_k=2,
        output_dir=tmp_path / "candidates",
        run_backtest_smoke=True,
        memory_path=tmp_path / "experiments.json",
        dry_run=False,
    )

    latest = ExperimentMemory(tmp_path / "experiments.json").latest()
    assert result["experiment_id"] == latest.experiment_id
    assert latest.params["family"] == "strategy_candidate_validation"
    assert Path(result["artifacts"]["candidates_json"]).exists()
    assert "oos" not in json.dumps(latest.metrics).lower()


def test_export_population_candidates_walk_forward_stub_does_not_write_oos(tmp_path: Path) -> None:
    input_path = tmp_path / "population.json"
    input_path.write_text(json.dumps(make_population_result()), encoding="utf-8")

    result = export_population_candidates(
        input_result=input_path,
        top_k=1,
        run_walk_forward=True,
        dry_run=True,
    )

    assert result["walk_forward"][0]["status"] == "stub"
    assert "oos" not in json.dumps(result["candidates"][0]["validation_metrics"]).lower()


def make_population_result() -> dict:
    return {
        "metrics": {
            "population": {"generations": 3.0, "final_top_agent": "mean_rev_1"},
            "simulation": {"reward_mean": 7.0, "sharpe_mean": 7.1},
        },
        "final_rankings": [
            {
                "agent_id": "mean_rev_1",
                "agent_type": "mean_reversion",
                "params": {"lookback": 5, "scale": 1.0},
                "elo": 1516.0,
            },
            {
                "agent_id": "momentum_1",
                "agent_type": "momentum",
                "params": {"lookback": 5, "scale": 1.0},
                "elo": 1484.0,
            },
        ],
        "generations": [
            {
                "metrics": {
                    "population": {"generation": 3.0},
                    "simulation": {"reward_mean": 7.0, "sharpe_mean": 7.1},
                }
            }
        ],
    }


def write_candidate_config(tmp_path: Path) -> Path:
    config = {
        "candidate_validation": {
            "top_k": 2,
            "output_dir": str(tmp_path / "candidates"),
            "run_backtest_smoke": True,
            "run_walk_forward": False,
        },
        "experiment": {
            "name": "candidate_validation_test",
            "family": "strategy_candidate_validation",
        },
        "memory": {"json_path": str(tmp_path / "experiments.json")},
        "baseline": {"oos_reference": "EXP-20260602-008", "oos_sharpe": 0.586},
    }
    path = tmp_path / "candidate_validation.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
