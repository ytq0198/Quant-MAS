from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.research import (
    StrategyCandidate,
    run_candidate_batch_walk_forward,
    save_candidate_batch_validation_report,
)
from scripts.batch_validate_candidates import batch_validate_candidates


def test_run_candidate_batch_walk_forward_sorts_by_oos_sharpe() -> None:
    result = run_candidate_batch_walk_forward(
        make_candidates(),
        make_features(days=36),
        config=candidate_oos_config(),
    )

    assert result.metrics["summary"]["candidate_count"] == 3
    assert result.comparison["oos_rank"].tolist() == [1, 2, 3]
    assert result.comparison["oos.sharpe"].is_monotonic_decreasing
    assert "best_vs_baseline_sharpe" in result.metrics["summary"]


def test_run_candidate_batch_walk_forward_respects_top_k() -> None:
    result = run_candidate_batch_walk_forward(
        make_candidates(),
        make_features(days=36),
        config=candidate_oos_config(),
        top_k=2,
    )

    assert len(result.results) == 2
    assert result.metrics["summary"]["candidate_count"] == 2
    assert set(result.comparison["candidate_id"]) <= {"cand_momentum_1", "cand_mean_rev_1"}


def test_run_candidate_batch_walk_forward_ignores_unused_future_columns() -> None:
    frame = make_features(days=36)
    frame["future_return_5"] = 0.01
    frame["future_direction_5"] = 1

    result = run_candidate_batch_walk_forward(
        make_candidates()[:2],
        frame,
        config=candidate_oos_config(),
    )

    assert result.metrics["summary"]["candidate_count"] == 2
    assert "oos.sharpe" in result.comparison.columns


def test_save_candidate_batch_validation_report_writes_artifacts(tmp_path: Path) -> None:
    result = run_candidate_batch_walk_forward(
        make_candidates()[:2],
        make_features(days=36),
        config=candidate_oos_config(),
    )

    artifacts = save_candidate_batch_validation_report(result, tmp_path / "candidate_oos_batch")

    assert Path(artifacts["metrics"]).exists()
    assert Path(artifacts["comparison_csv"]).exists()
    assert Path(artifacts["comparison_md"]).exists()
    assert Path(artifacts["cand_momentum_1.metrics"]).exists()
    comparison = pd.read_csv(artifacts["comparison_csv"])
    assert len(comparison) == 2
    assert "exceeds_baseline" in comparison.columns


def test_batch_validate_candidates_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/batch_validate_candidates.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--top-k" in result.stdout
    assert "--candidate-ids" in result.stdout
    assert "--no-dry-run" in result.stdout


def test_batch_validate_candidates_dry_run(tmp_path: Path) -> None:
    candidate_path = write_candidates(tmp_path)
    feature_path = tmp_path / "features.parquet"
    make_features(days=36).to_parquet(feature_path, index=False)

    result = batch_validate_candidates(
        candidate_json=candidate_path,
        features_path=feature_path,
        config_path=write_candidate_oos_config(tmp_path),
        storage_config=write_storage_config(tmp_path),
        top_k=2,
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["artifacts"] == {}
    assert result["metrics"]["summary"]["candidate_count"] == 2
    assert len(result["comparison"]) == 2


def test_batch_validate_candidates_non_dry_run_writes_memory(tmp_path: Path) -> None:
    candidate_path = write_candidates(tmp_path)
    feature_path = tmp_path / "features.parquet"
    memory_path = tmp_path / "reports" / "experiments.json"
    output_dir = tmp_path / "reports" / "candidate_oos_batch"
    make_features(days=36).to_parquet(feature_path, index=False)

    result = batch_validate_candidates(
        candidate_json=candidate_path,
        features_path=feature_path,
        config_path=write_candidate_oos_config(tmp_path),
        storage_config=write_storage_config(tmp_path),
        output_dir=output_dir,
        memory_path=memory_path,
        experiment_name="candidate_oos_batch_test",
        candidate_ids=["cand_mean_rev_1", "cand_momentum_2"],
        dry_run=False,
    )

    assert Path(result["artifacts"]["comparison_csv"]).exists()
    latest = ExperimentMemory(memory_path).latest()
    assert latest.name == "candidate_oos_batch_test"
    assert latest.params["family"] == "strategy_candidate_oos_batch"
    assert latest.metrics["summary"]["candidate_count"] == 2
    assert latest.metrics["summary"]["best_candidate_id"] in {"cand_mean_rev_1", "cand_momentum_2"}


def make_candidates() -> list[StrategyCandidate]:
    return [
        make_candidate(candidate_id="cand_momentum_1", agent_id="momentum_1", agent_type="momentum", scale=1.0),
        make_candidate(candidate_id="cand_mean_rev_1", agent_id="mean_rev_1", agent_type="mean_reversion", scale=1.0),
        make_candidate(candidate_id="cand_momentum_2", agent_id="momentum_2", agent_type="momentum", scale=0.5),
    ]


def make_candidate(
    *,
    candidate_id: str,
    agent_id: str,
    agent_type: str,
    scale: float,
) -> StrategyCandidate:
    return StrategyCandidate(
        candidate_id=candidate_id,
        source="population_training",
        agent_id=agent_id,
        agent_type=agent_type,
        params={"scale": scale},
        selection_metrics={"population.elo": 1500.0 + scale},
    )


def make_features(days: int = 36) -> pd.DataFrame:
    rows = []
    for index in range(days):
        close = 20.0 + index * 0.3 + (index % 4) * 0.05
        ma_distance = ((index % 7) - 3) / 100.0
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 0.8,
                "low": close - 0.8,
                "close": close + 0.1,
                "volume": 1000 + index,
                "ma_distance_5": ma_distance,
                "last_return": ma_distance / 2.0,
            }
        )
    return pd.DataFrame(rows)


def candidate_oos_config() -> dict[str, Any]:
    return {
        "candidate_oos": {
            "baseline_experiment_id": "EXP-20260602-008",
            "baseline_oos_sharpe": 0.586,
            "batch": {
                "top_k": None,
                "output_dir": "outputs/candidate_oos_batch",
                "experiment_name": "candidate_oos_batch_test",
            },
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
        "experiment": {"name": "candidate_oos_test", "family": "strategy_candidate_oos"},
    }


def write_candidate_oos_config(tmp_path: Path) -> Path:
    path = tmp_path / "candidate_oos.yaml"
    config = candidate_oos_config()
    config["candidate_oos"]["batch"]["output_dir"] = str(tmp_path / "reports" / "candidate_oos_batch")
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def write_candidates(tmp_path: Path) -> Path:
    path = tmp_path / "candidates.json"
    path.write_text(
        json.dumps({"candidates": [candidate.to_dict() for candidate in make_candidates()]}),
        encoding="utf-8",
    )
    return path


def write_storage_config(tmp_path: Path) -> Path:
    config = {
        "project_root": str(tmp_path),
        "raw_data_dir": "data/raw",
        "processed_data_dir": "data/processed",
        "features_dir": "data/features",
        "models_dir": "models",
        "reports_dir": "reports",
        "logs_dir": "logs",
    }
    path = tmp_path / "storage.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
