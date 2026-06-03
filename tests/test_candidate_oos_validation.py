from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.research import (
    CandidateStrategyAdapter,
    StrategyCandidate,
    run_candidate_walk_forward,
    save_candidate_validation_report,
)
from scripts.validate_candidate_oos import validate_candidate_oos


def test_candidate_strategy_adapter_generates_momentum_signals() -> None:
    candidate = make_candidate(agent_type="momentum", params={"scale": 1.0})

    signals = CandidateStrategyAdapter(candidate).generate_signals(make_features(days=8))

    assert set(signals.columns) == {"date", "symbol", "target_weight"}
    assert signals["target_weight"].between(0.0, 1.0).all()
    assert signals["target_weight"].nunique() > 1


def test_candidate_strategy_adapter_generates_mean_reversion_signals() -> None:
    momentum = CandidateStrategyAdapter(make_candidate(agent_type="momentum")).generate_signals(
        make_features(days=8)
    )
    mean_reversion = CandidateStrategyAdapter(
        make_candidate(agent_type="mean_reversion")
    ).generate_signals(make_features(days=8))

    assert not momentum["target_weight"].equals(mean_reversion["target_weight"])
    assert mean_reversion["target_weight"].between(0.0, 1.0).all()


def test_candidate_strategy_adapter_rejects_future_columns() -> None:
    frame = make_features(days=8)
    frame["future_direction_5"] = [0, 1] * 4

    with pytest.raises(ValueError, match="future"):
        CandidateStrategyAdapter(make_candidate()).generate_signals(frame)


def test_run_candidate_walk_forward_reports_oos_metrics() -> None:
    result = run_candidate_walk_forward(
        make_candidate(),
        make_features(days=36),
        config=candidate_oos_config(),
    )

    assert result.metrics["summary"]["candidate_id"] == "cand_momentum_1"
    assert result.metrics["summary"]["baseline_experiment_id"] == "EXP-20260602-008"
    assert result.metrics["summary"]["window_count"] == 2
    assert "vs_baseline_sharpe" in result.metrics["summary"]
    assert result.metrics["oos"]["samples"] == 8
    assert {"total_return", "sharpe", "max_drawdown", "final_equity"} <= set(result.metrics["oos"])
    assert not result.oos_equity_curve.empty


def test_candidate_walk_forward_windows_are_chronological() -> None:
    result = run_candidate_walk_forward(
        make_candidate(),
        make_features(days=36),
        config=candidate_oos_config(),
    )

    for row in result.windows.to_dict(orient="records"):
        assert pd.Timestamp(row["train_end_date"]) < pd.Timestamp(row["validation_start_date"])
        assert pd.Timestamp(row["validation_end_date"]) < pd.Timestamp(row["test_start_date"])
        assert pd.Timestamp(row["test_end_date"]) < pd.Timestamp(row["oos_start_date"])


def test_run_candidate_walk_forward_rejects_future_signal_columns() -> None:
    frame = make_features(days=36)
    frame["future_return_5"] = 0.01

    with pytest.raises(ValueError, match="future"):
        run_candidate_walk_forward(make_candidate(), frame, config=candidate_oos_config())


def test_save_candidate_validation_report_writes_artifacts(tmp_path: Path) -> None:
    result = run_candidate_walk_forward(
        make_candidate(),
        make_features(days=36),
        config=candidate_oos_config(),
    )

    artifacts = save_candidate_validation_report(result, tmp_path / "candidate_oos")

    for key in ("metrics", "windows", "oos_equity_curve", "oos_trades", "summary"):
        assert Path(artifacts[key]).exists()
    metrics = json.loads(Path(artifacts["metrics"]).read_text(encoding="utf-8"))
    assert metrics["summary"]["candidate_id"] == "cand_momentum_1"


def test_validate_candidate_oos_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_candidate_oos.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--candidate-json" in result.stdout
    assert "--no-dry-run" in result.stdout


def test_validate_candidate_oos_dry_run(tmp_path: Path) -> None:
    candidate_path = write_candidates(tmp_path)
    feature_path = tmp_path / "features.parquet"
    make_features(days=36).to_parquet(feature_path, index=False)
    config_path = write_candidate_oos_config(tmp_path)

    result = validate_candidate_oos(
        candidate_json=candidate_path,
        features_path=feature_path,
        config_path=config_path,
        storage_config=write_storage_config(tmp_path),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["artifacts"] == {}
    assert result["metrics"]["summary"]["candidate_id"] == "cand_momentum_1"


def test_validate_candidate_oos_non_dry_run_writes_memory(tmp_path: Path) -> None:
    candidate_path = write_candidates(tmp_path)
    feature_path = tmp_path / "features.parquet"
    output_dir = tmp_path / "reports" / "candidate_oos"
    memory_path = tmp_path / "reports" / "experiments.json"
    make_features(days=36).to_parquet(feature_path, index=False)

    result = validate_candidate_oos(
        candidate_json=candidate_path,
        features_path=feature_path,
        config_path=write_candidate_oos_config(tmp_path),
        storage_config=write_storage_config(tmp_path),
        output_dir=output_dir,
        memory_path=memory_path,
        experiment_name="candidate_oos_test",
        dry_run=False,
    )

    assert Path(result["artifacts"]["metrics"]).exists()
    latest = ExperimentMemory(memory_path).latest()
    assert latest.name == "candidate_oos_test"
    assert latest.params["family"] == "strategy_candidate_oos"
    assert latest.metrics["summary"]["candidate_id"] == "cand_momentum_1"
    assert "oos" in latest.metrics


def test_validate_candidate_oos_selects_candidate_id(tmp_path: Path) -> None:
    candidates = {
        "candidates": [
            make_candidate(candidate_id="cand_first").to_dict(),
            make_candidate(candidate_id="cand_second", agent_id="mean_rev_1", agent_type="mean_reversion").to_dict(),
        ]
    }
    candidate_path = tmp_path / "candidates.json"
    candidate_path.write_text(json.dumps(candidates), encoding="utf-8")
    feature_path = tmp_path / "features.parquet"
    make_features(days=36).to_parquet(feature_path, index=False)

    result = validate_candidate_oos(
        candidate_json=candidate_path,
        candidate_id="cand_second",
        features_path=feature_path,
        config_path=write_candidate_oos_config(tmp_path),
        storage_config=write_storage_config(tmp_path),
        dry_run=True,
    )

    assert result["candidate"]["candidate_id"] == "cand_second"
    assert result["metrics"]["summary"]["agent_type"] == "mean_reversion"


def make_candidate(
    *,
    candidate_id: str = "cand_momentum_1",
    agent_id: str = "momentum_1",
    agent_type: str = "momentum",
    params: dict[str, Any] | None = None,
) -> StrategyCandidate:
    return StrategyCandidate(
        candidate_id=candidate_id,
        source="population_training",
        agent_id=agent_id,
        agent_type=agent_type,
        params=params or {"scale": 1.0},
        selection_metrics={"population.elo": 1510.0},
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
        "experiment": {
            "name": "candidate_oos_test",
            "family": "strategy_candidate_oos",
        },
    }


def write_candidate_oos_config(tmp_path: Path) -> Path:
    path = tmp_path / "candidate_oos.yaml"
    config = candidate_oos_config()
    config["output"] = {"dir": str(tmp_path / "reports" / "candidate_oos")}
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def write_candidates(tmp_path: Path) -> Path:
    path = tmp_path / "candidates.json"
    path.write_text(
        json.dumps({"candidates": [make_candidate().to_dict()]}),
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
