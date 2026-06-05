import json
from pathlib import Path

from backend.services.artifacts import list_paper_artifacts
from backend.services.audit import list_audit_logs
from backend.services.experiments import get_experiment_detail, list_experiments


def _write_server_fixture(root: Path) -> None:
    reports = root / "outputs" / "reports"
    paper = root / "outputs" / "paper"
    audit = root / "outputs" / "pipelines" / "run-001"
    reports.mkdir(parents=True)
    paper.mkdir(parents=True)
    audit.mkdir(parents=True)

    (reports / "experiments.json").write_text(
        json.dumps(
            [
                {
                    "experiment_id": "EXP-SERVER-001",
                    "name": "server_walk_forward_fixture",
                    "status": "completed",
                    "created_at": "2026-06-05T00:00:00Z",
                    "metrics": {"oos": {"sharpe": 0.586}},
                    "artifacts": {"paper": "outputs/paper/paper_main_results.csv"},
                    "notes": "Server fixture.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (paper / "paper_main_results.csv").write_text("metric,value\n", encoding="utf-8")
    (audit / "audit.jsonl").write_text(
        json.dumps({"type": "audit.tool.completed", "run_id": "EXP-SERVER-001"})
        + "\n",
        encoding="utf-8",
    )


def test_list_experiments_reads_server_artifact_root(tmp_path):
    _write_server_fixture(tmp_path)

    payload = list_experiments(artifact_root=tmp_path)

    assert payload["source"] == "server_artifact"
    assert payload["experiments"][0]["experiment_id"] == "EXP-SERVER-001"
    assert payload["experiments"][0]["metric_family_summary"]["oos"] is True


def test_get_experiment_detail_reads_artifact_record(tmp_path):
    _write_server_fixture(tmp_path)

    payload = get_experiment_detail("EXP-SERVER-001", artifact_root=tmp_path)

    assert payload["source"] == "server_artifact"
    assert payload["experiment"]["name"] == "server_walk_forward_fixture"
    assert payload["experiment"]["metrics"]["oos"]["sharpe"] == 0.586


def test_missing_experiment_data_returns_fallback_baseline(tmp_path):
    payload = list_experiments(artifact_root=tmp_path)

    assert payload["source"] == "fallback_baseline"
    assert payload["experiments"][0]["experiment_id"] == "EXP-20260602-008"
    assert payload["experiments"][0]["metric_family_summary"]["oos"] is True


def test_list_paper_artifacts_reads_server_paper_dir(tmp_path):
    _write_server_fixture(tmp_path)

    payload = list_paper_artifacts(artifact_root=tmp_path)

    assert payload["source"] == "server_artifact"
    assert payload["artifacts"][0]["name"] == "paper_main_results.csv"


def test_list_audit_logs_reads_server_jsonl(tmp_path):
    _write_server_fixture(tmp_path)

    payload = list_audit_logs(artifact_root=tmp_path)

    assert payload["source"] == "server_artifact"
    assert payload["events"][0]["type"] == "audit.tool.completed"
