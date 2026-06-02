"""Run rule-based agent workflows."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

import yaml

from quant_mas.agents import SupervisorAgent
from quant_mas.tools import (
    BacktestTool,
    DataSummaryTool,
    ReportTool,
    ToolRegistry,
    TrainModelTool,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an agent workflow.")
    parser.add_argument("--config", default="configs/agent.yaml", help="Agent config path.")
    parser.add_argument("--task", required=True, help="Task text for rule-based routing.")
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--data-path", help="Path used by DataSummaryTool.")
    parser.add_argument("--input-path", help="Input parquet path for selected tool.")
    parser.add_argument("--output-dir", help="Output directory for selected tool.")
    parser.add_argument("--output-path", help="Output file path for ReportTool.")
    parser.add_argument("--tool-config", help="Backtest or train config path.")
    parser.add_argument("--memory-path", help="Experiment memory path for ReportTool.")
    parser.add_argument("--experiment-name", help="Experiment name for run tools.")
    parser.add_argument(
        "--events",
        action="store_true",
        help="Print emitted agent events as JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    agent_config = config.get("agent", {})
    if agent_config.get("allow_live_trading", False):
        raise ValueError("SupervisorAgent does not support live trading")

    registry = ToolRegistry(
        [
            DataSummaryTool(),
            BacktestTool(),
            TrainModelTool(),
            ReportTool(),
        ]
    )
    supervisor = SupervisorAgent(
        registry,
        max_steps=agent_config.get("max_steps", 4),
    )
    result = supervisor.run(
        args.task,
        storage_config=args.storage_config,
        data_path=args.data_path,
        input_path=args.input_path,
        output_dir=args.output_dir,
        output_path=args.output_path,
        config_path=args.tool_config,
        memory_path=args.memory_path,
        experiment_name=args.experiment_name,
    )
    print(result)
    if args.events:
        print(json.dumps([asdict(event) for event in supervisor.events], indent=2))


if __name__ == "__main__":
    main()
