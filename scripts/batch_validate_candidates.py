"""Batch-validate StrategyCandidates with walk-forward OOS backtests."""

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
    run_candidate_batch_walk_forward,
    save_candidate_batch_validation_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch-validate StrategyCandidates with OOS.")
    parser.add_argument("--candidate-json", required=True)
    parser.add_argument("--candidate-ids", nargs="*")
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--features-path", required=True)
    parser.add_argument("--config", default="configs/candidate_oos.yaml")
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--output-dir")
    parser.add_argument("--memory-path")
    parser.add_argument("--experiment-name")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    return parser


def batch_validate_candidates(
    *,
    candidate_json: str | Path,
    features_path: str | Path,
    config_path: str | Path = "configs/candidate_oos.yaml",
    storage_config: str | Path = "configs/storage.yaml",
    candidate_ids: list[str] | None = None,
    top_k: int | None = None,
    output_dir: str | Path | None = None,
    memory_path: str | Path | None = None,
    experiment_name: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    selected_top_k = top_k
    if selected_top_k is None:
        selected_top_k = config.get("candidate_oos", {}).get("batch", {}).get("top_k")
    candidates = _load_candidates(candidate_json, candidate_ids=candidate_ids)
    features = ParquetStorage().load(features_path)
    result = run_candidate_batch_walk_forward(
        candidates,
        features,
        config=config,
        top_k=selected_top_k,
    )

    artifacts: dict[str, str] = {}
    experiment_id: str | None = None
    if not dry_run:
        catalog = DataCatalog.from_yaml(storage_config)
        report_dir = Path(
            output_dir
            or config.get("candidate_oos", {}).get("batch", {}).get("output_dir")
            or catalog.path_for("reports_dir", "candidate_oos_batch_latest")
        ).expanduser()
        artifacts = save_candidate_batch_validation_report(result, report_dir)
        memory = ExperimentMemory(
            memory_path or catalog.path_for("reports_dir", "experiments.json")
        )
        record = memory.add(
            name=experiment_name
            or config.get("candidate_oos", {}).get("batch", {}).get("experiment_name")
            or "candidate_oos_batch_001",
            metrics=result.metrics,
            artifacts=artifacts,
            params={
                "family": "strategy_candidate_oos_batch",
                "candidate_json": str(Path(candidate_json).expanduser()),
                "features_path": str(Path(features_path).expanduser()),
                "candidate_ids": candidate_ids,
                "top_k": selected_top_k,
                "config": config,
            },
            notes="Batch StrategyCandidate walk-forward OOS comparison; not investment advice.",
        )
        experiment_id = record.experiment_id

    return {
        "metrics": result.metrics,
        "comparison": result.comparison.to_dict(orient="records"),
        "artifacts": artifacts,
        "experiment_id": experiment_id,
        "dry_run": dry_run,
    }


def main() -> int:
    _configure_stdout()
    args = build_parser().parse_args()
    try:
        result = batch_validate_candidates(
            candidate_json=args.candidate_json,
            candidate_ids=args.candidate_ids,
            top_k=args.top_k,
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
        print(f"[candidate-oos-batch] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_candidates(
    path: str | Path,
    *,
    candidate_ids: list[str] | None,
) -> list[StrategyCandidate]:
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else payload.get("candidates", [])
    candidates = [StrategyCandidate.from_dict(item) for item in items]
    if not candidates:
        raise ValueError("candidate JSON contains no candidates")
    if not candidate_ids:
        return candidates
    wanted = set(candidate_ids)
    selected = [candidate for candidate in candidates if candidate.candidate_id in wanted]
    missing = sorted(wanted.difference({candidate.candidate_id for candidate in selected}))
    if missing:
        raise ValueError(f"candidate_id not found: {missing}")
    return selected


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
