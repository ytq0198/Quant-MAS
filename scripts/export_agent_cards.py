"""Export static Agent Cards and optional MCP tool specs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from quant_mas.protocols import (
    agent_card_to_dict,
    build_report_card,
    build_research_card,
    build_supervisor_card,
    registry_to_mcp_specs,
)
from quant_mas.tools import (
    BacktestTool,
    DataSummaryTool,
    MLBacktestTool,
    PipelineTool,
    ReportTool,
    RiskTool,
    ToolRegistry,
    TrainModelTool,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export static Quant MAS Agent Cards.")
    parser.add_argument("--config", default="configs/protocols.yaml")
    parser.add_argument("--output-dir", help="Output directory for exported JSON files.")
    parser.add_argument(
        "--include-mcp-specs",
        action="store_true",
        help="Also export mcp_tools.json from the selected registry.",
    )
    parser.add_argument(
        "--registry",
        choices=["default", "supervisor"],
        default="default",
        help="Tool registry profile to export.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = _load_config(args.config)
    protocols = config.get("protocols", {})
    version = protocols.get("a2a", {}).get("version", "0.1.0")
    output_dir = Path(
        args.output_dir or config.get("paths", {}).get("output_dir", "outputs/protocols")
    ).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    cards = [
        ("supervisor_agent_card.json", build_supervisor_card(version)),
        ("research_agent_card.json", build_research_card(version)),
        ("report_agent_card.json", build_report_card(version)),
    ]
    written = []
    for filename, card in cards:
        path = output_dir / filename
        path.write_text(
            json.dumps(agent_card_to_dict(card), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(str(path))

    if args.include_mcp_specs:
        registry = _build_registry(args.registry)
        spec_path = output_dir / "mcp_tools.json"
        spec_path.write_text(
            json.dumps(
                [spec.to_dict() for spec in registry_to_mcp_specs(registry)],
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(str(spec_path))

    print(json.dumps({"written": written}, indent=2, ensure_ascii=False))
    return 0


def _load_config(path: str | Path) -> dict:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _build_registry(profile: str) -> ToolRegistry:
    tools = [
        DataSummaryTool(),
        BacktestTool(),
        TrainModelTool(),
        MLBacktestTool(),
        PipelineTool(),
        RiskTool(),
        ReportTool(),
    ]
    return ToolRegistry(tools)


if __name__ == "__main__":
    raise SystemExit(main())
