from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from quant_mas.memory import ExperimentMemory
from quant_mas.orchestration.audit_log import AuditEvent, append_audit_event


def seed_memory(path: Path) -> None:
    memory = ExperimentMemory(path)
    memory.add(
        experiment_id="EXP-20260602-008",
        name="server_walk_forward_001",
        metrics={"oos": {"sharpe": 0.586, "total_return": 0.443, "max_drawdown": -0.2}},
        params={"family": "walk_forward", "symbols": ["AAPL", "MSFT", "SPY"]},
        artifacts={"summary": "reports/walk_forward/summary.md"},
        notes="main ML OOS baseline",
    )
    memory.add(
        experiment_id="EXP-TEXT-WF-003",
        name="server_walk_forward_text_003",
        metrics={
            "oos": {"sharpe": 0.565, "total_return": 0.421},
            "coverage_ratio": 0.0242,
            "aligned_count": 5088,
            "dropped_count": 4346,
        },
        params={"family": "text_ablation", "text_source": "Finnhub"},
        notes="exploratory text run",
    )
    memory.add(
        experiment_id="EXP-POP-006",
        name="candidate_oos_batch",
        metrics={"oos": {"sharpe": 1.039}, "candidate_count": 4},
        params={"family": "population_oos"},
    )
    memory.add(
        experiment_id="EXP-POP-010",
        name="rl_feature_linear_oos",
        metrics={"oos": {"sharpe": 0.387}, "simulation": {"sharpe_mean": 12.13}},
        params={"family": "rl_ablation"},
    )
    memory.add(
        experiment_id="EXP-RL-003",
        name="rl_training_simulation",
        metrics={"simulation": {"sharpe_mean": 6.31}, "training": {"policy_step_count": 1}},
        params={"family": "rl_training"},
    )


def seed_audit_logs(root: Path) -> None:
    audit_path = root / "run-a" / "audit.jsonl"
    append_audit_event(
        audit_path,
        AuditEvent(
            pipeline_id="text_enhanced",
            run_id="run-a",
            node_id="audit_text_signals",
            status="success",
            metric_family="audit",
        ),
    )
    append_audit_event(
        audit_path,
        AuditEvent(
            pipeline_id="text_enhanced",
            run_id="run-a",
            node_id="walk_forward_eval",
            status="success",
            metric_family="walk_forward",
        ),
    )


def test_export_paper_artifacts_writes_expected_files(tmp_path: Path) -> None:
    from quant_mas.research.paper_artifacts import export_paper_artifacts

    memory_path = tmp_path / "experiments.json"
    audit_dir = tmp_path / "audits"
    output_dir = tmp_path / "paper"
    seed_memory(memory_path)
    seed_audit_logs(audit_dir)

    result = export_paper_artifacts(
        memory_path=memory_path,
        audit_dir=audit_dir,
        output_dir=output_dir,
    )

    expected = {
        "main_results",
        "text_ablation",
        "population_ablation",
        "rl_ablation",
        "experiment_index",
        "audit_summary",
    }
    assert set(result) == expected
    for path in result.values():
        assert Path(path).exists()


def test_main_results_excludes_simulation_only_runs(tmp_path: Path) -> None:
    from quant_mas.research.paper_artifacts import export_paper_artifacts

    memory_path = tmp_path / "experiments.json"
    seed_memory(memory_path)
    result = export_paper_artifacts(memory_path=memory_path, output_dir=tmp_path / "paper")

    table = pd.read_csv(result["main_results"])

    assert "server_walk_forward_001" in set(table["name"])
    assert "rl_training_simulation" not in set(table["name"])
    assert set(table["metric_namespace"]) == {"oos"}


def test_text_ablation_requires_coverage_columns(tmp_path: Path) -> None:
    from quant_mas.research.paper_artifacts import export_paper_artifacts

    memory_path = tmp_path / "experiments.json"
    seed_memory(memory_path)
    result = export_paper_artifacts(memory_path=memory_path, output_dir=tmp_path / "paper")

    table = pd.read_csv(result["text_ablation"])
    row = table.loc[table["experiment_id"] == "EXP-TEXT-WF-003"].iloc[0]

    assert row["coverage_ratio"] == 0.0242
    assert row["aligned_count"] == 5088
    assert row["dropped_count"] == 4346


def test_rl_ablation_separates_simulation_and_oos(tmp_path: Path) -> None:
    from quant_mas.research.paper_artifacts import export_paper_artifacts

    memory_path = tmp_path / "experiments.json"
    seed_memory(memory_path)
    result = export_paper_artifacts(memory_path=memory_path, output_dir=tmp_path / "paper")

    table = pd.read_csv(result["rl_ablation"])
    oos_row = table.loc[table["experiment_id"] == "EXP-POP-010"].iloc[0]
    sim_row = table.loc[table["experiment_id"] == "EXP-RL-003"].iloc[0]

    assert oos_row["oos.sharpe"] == 0.387
    assert oos_row["simulation.sharpe_mean"] == 12.13
    assert pd.isna(sim_row["oos.sharpe"])
    assert sim_row["simulation.sharpe_mean"] == 6.31


def test_audit_summary_collects_jsonl_logs(tmp_path: Path) -> None:
    from quant_mas.research.paper_artifacts import export_paper_artifacts

    memory_path = tmp_path / "experiments.json"
    audit_dir = tmp_path / "audits"
    seed_memory(memory_path)
    seed_audit_logs(audit_dir)

    result = export_paper_artifacts(
        memory_path=memory_path,
        audit_dir=audit_dir,
        output_dir=tmp_path / "paper",
    )
    payload = json.loads(Path(result["audit_summary"]).read_text(encoding="utf-8"))

    assert payload["audit_file_count"] == 1
    assert payload["total_events"] == 2
    assert payload["metric_families"] == ["audit", "walk_forward"]


def test_export_paper_artifacts_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/export_paper_artifacts.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--memory-path" in result.stdout
    assert "--audit-dir" in result.stdout


def test_export_paper_artifacts_cli_writes_outputs(tmp_path: Path) -> None:
    memory_path = tmp_path / "experiments.json"
    output_dir = tmp_path / "paper"
    seed_memory(memory_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_paper_artifacts.py",
            "--memory-path",
            str(memory_path),
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (output_dir / "paper_main_results.csv").exists()
    assert (output_dir / "paper_experiment_index.md").exists()
