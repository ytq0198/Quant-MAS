"""Run an internal MCP-style research pipeline dry-run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quant_mas.orchestration.langgraph_recipe_workflow import (  # noqa: E402
    run_langgraph_recipe_workflow,
)
from quant_mas.orchestration.mcp_scheduler import MCPScheduler  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run internal MCP-style Quant MAS research pipeline dry-runs.",
    )
    parser.add_argument(
        "--recipe",
        default="mock_research",
        help="Built-in recipe name or path to a YAML recipe (e.g. configs/pipelines/text_enhanced.yaml.example).",
    )
    parser.add_argument(
        "--list-recipes",
        action="store_true",
        help="List built-in dry-run recipes and exit.",
    )
    parser.add_argument(
        "--backend",
        choices=("scheduler", "langgraph"),
        default="scheduler",
        help="Execution backend. LangGraph remains dry-run only and falls back when unavailable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run in dry-run mode. M13.0 only supports dry-run execution.",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Reserved for later M13 stages; M13.0 rejects real execution.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/pipelines"),
        help="Directory where run-specific audit logs are written.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    scheduler = MCPScheduler()

    if args.list_recipes:
        for recipe in scheduler.list_recipes():
            print(recipe)
        return 0

    try:
        if args.backend == "langgraph":
            result = run_langgraph_recipe_workflow(
                args.recipe,
                output_dir=args.output_dir,
                dry_run=args.dry_run,
            )
        else:
            result = scheduler.run(args.recipe, output_dir=args.output_dir, dry_run=args.dry_run)
    except Exception as exc:
        print(f"run_mcp_pipeline failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "pipeline_id": result.pipeline_id,
        "run_id": result.run_id,
        "status": result.status,
        "planned_nodes": result.planned_nodes,
        "audit_path": str(result.audit_path),
        "audit_summary": result.audit_summary,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
