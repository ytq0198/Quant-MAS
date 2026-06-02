"""Run experimental ResearchWorkflow orchestration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from quant_mas.orchestration import initial_state, run_sequential_workflow
from quant_mas.orchestration.langgraph_workflow import (
    LANGGRAPH_AVAILABLE,
    run_langgraph_workflow,
)
from quant_mas.orchestration.registry import create_default_tool_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Quant MAS ResearchWorkflow.")
    parser.add_argument("--config", default="configs/langgraph_workflow.yaml")
    parser.add_argument("--backend", choices=("sequential", "langgraph"), default="sequential")
    parser.add_argument("--task", default="research workflow dry run")
    parser.add_argument("--dry-run", action="store_true", default=None)
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    parser.add_argument("--storage-config")
    parser.add_argument("--features-config")
    parser.add_argument("--train-config")
    parser.add_argument("--ml-backtest-config")
    parser.add_argument("--risk-config")
    parser.add_argument("--raw-path")
    parser.add_argument("--features-path")
    parser.add_argument("--model-path")
    parser.add_argument("--report-output-dir")
    parser.add_argument("--targets-path")
    parser.add_argument("--equity-path")
    parser.add_argument("--output-json")
    parser.add_argument("--stop-on-error", action="store_true", default=None)
    parser.add_argument("--no-stop-on-error", action="store_false", dest="stop_on_error")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        state = run_workflow_from_args(args)
    except Exception as exc:
        print(f"[workflow] ERROR: {exc}", file=sys.stderr)
        return 1
    if args.output_json:
        output = Path(args.output_json).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(_summary(state), indent=2, ensure_ascii=False))
    return 1 if state["errors"] else 0


def run_workflow_from_args(args: argparse.Namespace):
    config = _load_yaml(Path(args.config).expanduser())
    workflow_config = config.get("workflow", {})
    paths = config.get("paths", {})
    dry_run = (
        bool(workflow_config.get("default_dry_run", True))
        if args.dry_run is None
        else bool(args.dry_run)
    )
    stop_on_error = (
        bool(workflow_config.get("stop_on_error", True))
        if args.stop_on_error is None
        else bool(args.stop_on_error)
    )
    state = initial_state(
        task=args.task,
        dry_run=dry_run,
        storage_config=args.storage_config or paths.get("storage_config", "configs/storage.yaml"),
        features_config=args.features_config or paths.get("features_config", "configs/features.yaml"),
        train_config=args.train_config or paths.get("train_config", "configs/train.yaml"),
        ml_backtest_config=args.ml_backtest_config
        or paths.get("ml_backtest_config", "configs/backtest_ml.yaml"),
        risk_config=args.risk_config or paths.get("risk_config", "configs/risk.yaml"),
        raw_path=args.raw_path,
        features_path=args.features_path,
        model_path=args.model_path,
        report_output_dir=args.report_output_dir,
        targets_path=args.targets_path,
        equity_path=args.equity_path,
    )
    tools = create_default_tool_registry(dry_run=dry_run)
    backend = args.backend
    if backend == "langgraph" and not LANGGRAPH_AVAILABLE:
        print("[workflow] warning: langgraph not installed; falling back to sequential")
        backend = "sequential"
    if backend == "langgraph":
        return run_langgraph_workflow(state, tools=tools)
    return run_sequential_workflow(state, tools=tools, stop_on_error=stop_on_error)


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _summary(state) -> dict:
    return {
        "task": state["task"],
        "dry_run": state["dry_run"],
        "completed_nodes": state["completed_nodes"],
        "errors": state["errors"],
        "artifacts": state["artifacts"],
        "metrics": state["metrics"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
