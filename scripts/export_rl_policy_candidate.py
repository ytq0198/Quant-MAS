"""Export an RL policy checkpoint as a StrategyCandidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.rl import export_policy_candidate, write_rl_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export RL policy as StrategyCandidate.")
    parser.add_argument("--config", default="configs/rl_policy_export.yaml")
    parser.add_argument("--policy-state")
    parser.add_argument("--metrics")
    parser.add_argument("--output-dir")
    parser.add_argument("--candidate-id")
    parser.add_argument("--agent-type")
    parser.add_argument("--memory-path")
    parser.add_argument("--experiment-name")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    return parser


def export_rl_policy_candidate(
    *,
    config_path: str | Path = "configs/rl_policy_export.yaml",
    policy_state: str | Path | None = None,
    metrics: str | Path | None = None,
    output_dir: str | Path | None = None,
    candidate_id: str | None = None,
    agent_type: str | None = None,
    memory_path: str | Path | None = None,
    experiment_name: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    export_config = config.get("rl_policy_export", {})
    experiment = config.get("experiment", {})
    policy_path = Path(policy_state or export_config.get("policy_state", "")).expanduser()
    metrics_path = Path(metrics or export_config.get("metrics", "")).expanduser()
    if not policy_path:
        raise ValueError("policy_state path is required")
    if not metrics_path:
        raise ValueError("metrics path is required")

    candidate = export_policy_candidate(
        policy_state_path=policy_path,
        metrics_path=metrics_path,
        candidate_id=candidate_id,
        agent_type=agent_type or export_config.get("agent_type", "grpo_policy"),
    )
    artifacts: dict[str, str] = {}
    experiment_id: str | None = None
    if not dry_run:
        target_dir = Path(output_dir or export_config.get("output_dir", "outputs/rl_candidates")).expanduser()
        artifacts = write_rl_candidates([candidate], target_dir)
        memory_target = memory_path or experiment.get("memory_path") or target_dir / "experiments.json"
        record = ExperimentMemory(memory_target).add(
            name=experiment_name or experiment.get("name", "rl_policy_export_001"),
            metrics={
                "summary": {
                    "candidate_count": 1,
                    "simulation_only": True,
                    "source": "rl_training",
                },
                "selection": candidate.selection_metrics,
            },
            artifacts=artifacts,
            params={
                "family": experiment.get("family", "rl_policy_export"),
                "candidate": candidate.to_dict(),
                "config": config,
            },
            notes="RL policy exported as StrategyCandidate; OOS validation must use M11.7/M11.8.",
        )
        experiment_id = record.experiment_id
    return {
        "candidate": candidate.to_dict(),
        "artifacts": artifacts,
        "experiment_id": experiment_id,
        "dry_run": dry_run,
    }


def main() -> int:
    _configure_stdout()
    args = build_parser().parse_args()
    try:
        result = export_rl_policy_candidate(
            config_path=args.config,
            policy_state=args.policy_state,
            metrics=args.metrics,
            output_dir=args.output_dir,
            candidate_id=args.candidate_id,
            agent_type=args.agent_type,
            memory_path=args.memory_path,
            experiment_name=args.experiment_name,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"[rl-policy-export] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
