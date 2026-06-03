"""Validate a StrategyCandidate with walk-forward OOS backtests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.memory import ExperimentMemory
from quant_mas.research import (
    StrategyCandidate,
    run_candidate_walk_forward,
    save_candidate_validation_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate StrategyCandidate with walk-forward OOS.")
    parser.add_argument("--candidate-json", required=True)
    parser.add_argument("--candidate-id")
    parser.add_argument("--features-path", required=True)
    parser.add_argument("--config", default="configs/candidate_oos.yaml")
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--output-dir")
    parser.add_argument("--memory-path")
    parser.add_argument("--experiment-name")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    return parser


def validate_candidate_oos(
    *,
    candidate_json: str | Path,
    features_path: str | Path,
    config_path: str | Path = "configs/candidate_oos.yaml",
    storage_config: str | Path = "configs/storage.yaml",
    candidate_id: str | None = None,
    output_dir: str | Path | None = None,
    memory_path: str | Path | None = None,
    experiment_name: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    candidate = _load_candidate(candidate_json, candidate_id=candidate_id)
    features = ParquetStorage().load(features_path)
    result = run_candidate_walk_forward(candidate, features, config=config)
    artifacts: dict[str, str] = {}
    if not dry_run:
        catalog = DataCatalog.from_yaml(storage_config)
        report_dir = Path(
            output_dir
            or config.get("output", {}).get(
                "dir",
                catalog.path_for("reports_dir", "candidate_oos_latest"),
            )
        ).expanduser()
        artifacts = save_candidate_validation_report(result, report_dir)
        memory = ExperimentMemory(
            memory_path or catalog.path_for("reports_dir", "experiments.json")
        )
        memory.add(
            name=experiment_name or config.get("experiment", {}).get("name", "candidate_oos_validation_001"),
            metrics=result.metrics,
            artifacts=artifacts,
            params={
                "family": config.get("experiment", {}).get("family", "strategy_candidate_oos"),
                "candidate": candidate.to_dict(),
                "features_path": str(Path(features_path).expanduser()),
                "config": config,
            },
            notes="StrategyCandidate walk-forward OOS validation; not investment advice.",
        )
    return {
        "candidate": candidate.to_dict(),
        "metrics": result.metrics,
        "artifacts": artifacts,
        "dry_run": dry_run,
    }


def main() -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = validate_candidate_oos(
            candidate_json=args.candidate_json,
            candidate_id=args.candidate_id,
            features_path=args.features_path,
            config_path=args.config,
            storage_config=args.storage_config,
            output_dir=args.output_dir,
            memory_path=args.memory_path,
            experiment_name=args.experiment_name,
            dry_run=args.dry_run,
        )
        print(json.dumps(result["metrics"], indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"[candidate-oos] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_candidate(path: str | Path, *, candidate_id: str | None) -> StrategyCandidate:
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else payload.get("candidates", [])
    candidates = [StrategyCandidate.from_dict(item) for item in items]
    if not candidates:
        raise ValueError("candidate JSON contains no candidates")
    if candidate_id is None:
        return candidates[0]
    for candidate in candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    raise ValueError(f"candidate_id not found: {candidate_id}")


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
