"""Export population winners as strategy candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quant_mas.memory import ExperimentMemory
from quant_mas.research import StrategyCandidate, assert_no_oos_metrics
from quant_mas.rl import (
    extract_top_candidates,
    run_candidate_backtest_smoke,
    walk_forward_stub,
    write_candidates,
)
from scripts.run_population_training import run_population_training_from_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export population Top-K as strategy candidates.")
    parser.add_argument("--config", default="configs/candidate_validation.yaml")
    parser.add_argument("--population-config", default="configs/population_training.yaml")
    parser.add_argument("--input-result", help="Optional population result JSON path.")
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--output-dir")
    parser.add_argument("--run-backtest-smoke", action="store_true")
    parser.add_argument(
        "--run-walk-forward",
        action="store_true",
        help="Stub only in M11.6; does not produce oos metrics.",
    )
    parser.add_argument("--memory-path")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    return parser


def export_population_candidates(
    *,
    config_path: str | Path = "configs/candidate_validation.yaml",
    population_config: str | Path = "configs/population_training.yaml",
    input_result: str | Path | None = None,
    top_k: int | None = None,
    output_dir: str | Path | None = None,
    run_backtest_smoke: bool | None = None,
    run_walk_forward: bool | None = None,
    memory_path: str | Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    validation = config.get("candidate_validation", {})
    selected_top_k = int(top_k or validation.get("top_k", 2))
    selected_output_dir = Path(output_dir or validation.get("output_dir", "outputs/candidates")).expanduser()
    should_backtest = bool(
        validation.get("run_backtest_smoke", False)
        if run_backtest_smoke is None
        else run_backtest_smoke
    )
    should_walk_forward = bool(
        validation.get("run_walk_forward", False)
        if run_walk_forward is None
        else run_walk_forward
    )
    population_result = (
        _load_json(input_result)
        if input_result
        else run_population_training_from_config(
            config_path=population_config or config.get("population", {}).get("config", "configs/population_training.yaml"),
            dry_run=True,
        )
    )
    candidates = extract_top_candidates(population_result, top_k=selected_top_k)
    if should_backtest:
        candidates = [run_candidate_backtest_smoke(candidate) for candidate in candidates]
    walk_forward = []
    if should_walk_forward:
        walk_forward = [walk_forward_stub(candidate) for candidate in candidates]

    for candidate in candidates:
        assert_no_oos_metrics(candidate.selection_metrics)
        assert_no_oos_metrics(candidate.validation_metrics)

    artifacts: dict[str, str] = {}
    if not dry_run:
        artifacts.update(write_candidates(candidates, selected_output_dir))
        summary_path = selected_output_dir / "summary.md"
        summary_path.write_text(
            _summary_markdown(candidates, walk_forward=walk_forward),
            encoding="utf-8",
        )
        artifacts["summary"] = str(summary_path)

    record = None
    if not dry_run:
        metrics = _experiment_metrics(candidates)
        record = ExperimentMemory(
            memory_path or config.get("memory", {}).get("json_path", "outputs/reports/experiments.json")
        ).add(
            name=str(config.get("experiment", {}).get("name", "strategy_candidate_validation_mock_001")),
            metrics=metrics,
            artifacts=artifacts,
            params={
                "family": str(config.get("experiment", {}).get("family", "strategy_candidate_validation")),
                "top_k": selected_top_k,
                "run_backtest_smoke": should_backtest,
                "run_walk_forward": should_walk_forward,
                "simulation_only": True,
            },
            notes="M11.6 candidate bridge; walk-forward hook is stub unless explicitly implemented later.",
        )

    return {
        "candidates": [candidate.to_dict() for candidate in candidates],
        "artifacts": artifacts,
        "walk_forward": walk_forward,
        "experiment_id": record.experiment_id if record else None,
        "dry_run": dry_run,
    }


def main() -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = export_population_candidates(
            config_path=args.config,
            population_config=args.population_config,
            input_result=args.input_result,
            top_k=args.top_k,
            output_dir=args.output_dir,
            run_backtest_smoke=args.run_backtest_smoke or None,
            run_walk_forward=args.run_walk_forward or None,
            memory_path=args.memory_path,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"[candidate-bridge] ERROR: {exc}", file=sys.stderr)
        return 1


def _experiment_metrics(candidates: list[StrategyCandidate]) -> dict[str, Any]:
    if not candidates:
        return {"candidate": {"count": 0.0}, "backtest": {}}
    backtest_sharpes = [
        float(candidate.validation_metrics.get("backtest.sharpe", 0.0))
        for candidate in candidates
    ]
    metrics = {
        "candidate": {
            "count": float(len(candidates)),
            "top_candidate": candidates[0].candidate_id,
        },
        "backtest": {
            "sharpe_mean": float(sum(backtest_sharpes) / len(backtest_sharpes)),
            "sharpe_top": float(backtest_sharpes[0]),
        },
    }
    assert_no_oos_metrics(metrics)
    return metrics


def _summary_markdown(candidates: list[StrategyCandidate], *, walk_forward: list[dict[str, Any]]) -> str:
    lines = [
        "# Strategy Candidate Bridge",
        "",
        "simulation_only: true",
        "",
        "Population metrics and backtest smoke metrics are not walk-forward OOS metrics.",
        "Paper baseline remains EXP-20260602-008 oos.sharpe 0.586.",
        "",
        "## Candidates",
    ]
    for candidate in candidates:
        lines.append(
            f"- {candidate.candidate_id}: agent={candidate.agent_id}, type={candidate.agent_type}, "
            f"backtest.sharpe={candidate.validation_metrics.get('backtest.sharpe', 'not_run')}"
        )
    if walk_forward:
        lines.extend(["", "## Walk-forward Stub"])
        for item in walk_forward:
            lines.append(f"- {item['candidate_id']}: {item['message']}")
    return "\n".join(lines) + "\n"


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
