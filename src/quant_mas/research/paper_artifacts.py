"""Export paper-grade result tables and audit summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.memory import ExperimentMemory, ExperimentRecord
from quant_mas.research.baseline import resolve_metric


MAIN_COLUMNS = [
    "experiment_id",
    "name",
    "family",
    "metric_namespace",
    "oos.sharpe",
    "oos.total_return",
    "oos.max_drawdown",
    "notes",
]

TEXT_COLUMNS = [
    "experiment_id",
    "name",
    "text_source",
    "coverage_ratio",
    "aligned_count",
    "dropped_count",
    "oos.sharpe",
    "oos.total_return",
    "notes",
]

POPULATION_COLUMNS = [
    "experiment_id",
    "name",
    "candidate_count",
    "oos.sharpe",
    "oos.total_return",
    "notes",
]

RL_COLUMNS = [
    "experiment_id",
    "name",
    "family",
    "oos.sharpe",
    "oos.total_return",
    "simulation.sharpe_mean",
    "training.policy_step_count",
    "notes",
]


def export_paper_artifacts(
    *,
    memory_path: str | Path,
    output_dir: str | Path,
    audit_dir: str | Path | None = None,
) -> dict[str, str]:
    """Export paper tables from ExperimentMemory and optional audit logs."""
    records = ExperimentMemory(memory_path).list()
    target_dir = Path(output_dir).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "main_results": target_dir / "paper_main_results.csv",
        "text_ablation": target_dir / "paper_text_ablation.csv",
        "population_ablation": target_dir / "paper_population_ablation.csv",
        "rl_ablation": target_dir / "paper_rl_ablation.csv",
        "experiment_index": target_dir / "paper_experiment_index.md",
        "audit_summary": target_dir / "audit_summary.json",
    }

    _main_results(records).to_csv(paths["main_results"], index=False)
    _text_ablation(records).to_csv(paths["text_ablation"], index=False)
    _population_ablation(records).to_csv(paths["population_ablation"], index=False)
    _rl_ablation(records).to_csv(paths["rl_ablation"], index=False)
    paths["experiment_index"].write_text(_experiment_index(records), encoding="utf-8")
    paths["audit_summary"].write_text(
        json.dumps(_audit_summary(audit_dir), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {key: str(value) for key, value in paths.items()}


def _main_results(records: list[ExperimentRecord]) -> pd.DataFrame:
    rows = []
    for record in records:
        if resolve_metric(record.metrics, "oos.sharpe") is None:
            continue
        family = _family(record)
        if family in {"rl_training", "simulation", "population_simulation"}:
            continue
        rows.append(
            {
                "experiment_id": record.experiment_id,
                "name": record.name,
                "family": family,
                "metric_namespace": "oos",
                "oos.sharpe": resolve_metric(record.metrics, "oos.sharpe"),
                "oos.total_return": resolve_metric(record.metrics, "oos.total_return"),
                "oos.max_drawdown": resolve_metric(record.metrics, "oos.max_drawdown"),
                "notes": record.notes,
            }
        )
    return pd.DataFrame(rows, columns=MAIN_COLUMNS)


def _text_ablation(records: list[ExperimentRecord]) -> pd.DataFrame:
    rows = []
    for record in records:
        family = _family(record)
        if "text" not in family and "text" not in record.name.lower():
            continue
        rows.append(
            {
                "experiment_id": record.experiment_id,
                "name": record.name,
                "text_source": record.params.get("text_source"),
                "coverage_ratio": resolve_metric(record.metrics, "coverage_ratio"),
                "aligned_count": resolve_metric(record.metrics, "aligned_count"),
                "dropped_count": resolve_metric(record.metrics, "dropped_count"),
                "oos.sharpe": resolve_metric(record.metrics, "oos.sharpe"),
                "oos.total_return": resolve_metric(record.metrics, "oos.total_return"),
                "notes": record.notes,
            }
        )
    return pd.DataFrame(rows, columns=TEXT_COLUMNS)


def _population_ablation(records: list[ExperimentRecord]) -> pd.DataFrame:
    rows = []
    for record in records:
        family = _family(record)
        if "population" not in family and "candidate" not in record.name.lower():
            continue
        rows.append(
            {
                "experiment_id": record.experiment_id,
                "name": record.name,
                "candidate_count": resolve_metric(record.metrics, "candidate_count"),
                "oos.sharpe": resolve_metric(record.metrics, "oos.sharpe"),
                "oos.total_return": resolve_metric(record.metrics, "oos.total_return"),
                "notes": record.notes,
            }
        )
    return pd.DataFrame(rows, columns=POPULATION_COLUMNS)


def _rl_ablation(records: list[ExperimentRecord]) -> pd.DataFrame:
    rows = []
    for record in records:
        family = _family(record)
        if "rl" not in family and "rl" not in record.name.lower():
            continue
        rows.append(
            {
                "experiment_id": record.experiment_id,
                "name": record.name,
                "family": family,
                "oos.sharpe": resolve_metric(record.metrics, "oos.sharpe"),
                "oos.total_return": resolve_metric(record.metrics, "oos.total_return"),
                "simulation.sharpe_mean": resolve_metric(
                    record.metrics, "simulation.sharpe_mean"
                ),
                "training.policy_step_count": resolve_metric(
                    record.metrics, "training.policy_step_count"
                ),
                "notes": record.notes,
            }
        )
    return pd.DataFrame(rows, columns=RL_COLUMNS)


def _experiment_index(records: list[ExperimentRecord]) -> str:
    lines = ["# Paper Experiment Index", ""]
    if not records:
        lines.append("No experiments found.")
        return "\n".join(lines) + "\n"
    lines.append("| experiment_id | name | family | status | notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    for record in records:
        lines.append(
            " | ".join(
                [
                    "| " + record.experiment_id,
                    record.name,
                    _family(record),
                    record.status,
                    record.notes.replace("\n", " "),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Paper boundary:",
            "",
            "- Main-result tables use walk-forward OOS metrics only.",
            "- Simulation, training, and population metrics are ablation context.",
            "- Missing values are left blank in CSV outputs.",
        ]
    )
    return "\n".join(lines) + "\n"


def _audit_summary(audit_dir: str | Path | None) -> dict[str, Any]:
    if audit_dir is None:
        return {
            "audit_file_count": 0,
            "total_events": 0,
            "metric_families": [],
            "status_counts": {},
        }
    root = Path(audit_dir).expanduser()
    if not root.exists():
        return {
            "audit_file_count": 0,
            "total_events": 0,
            "metric_families": [],
            "status_counts": {},
        }
    files = sorted(root.rglob("audit.jsonl"))
    total_events = 0
    families: set[str] = set()
    status_counts: dict[str, int] = {}
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            total_events += 1
            family = str(payload.get("metric_family", ""))
            if family:
                families.add(family)
            status = str(payload.get("status", "unknown"))
            status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "audit_file_count": len(files),
        "total_events": total_events,
        "metric_families": sorted(families),
        "status_counts": status_counts,
    }


def _family(record: ExperimentRecord) -> str:
    explicit = record.params.get("family")
    if explicit:
        return str(explicit)
    name = record.name.lower()
    if "text" in name:
        return "text_ablation"
    if "candidate" in name or "population" in name:
        return "population_oos"
    if "rl" in name:
        return "rl_ablation"
    if "walk" in name or resolve_metric(record.metrics, "oos.sharpe") is not None:
        return "walk_forward"
    return "other"
