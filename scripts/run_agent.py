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
    MLBacktestTool,
    PipelineTool,
    ReportTool,
    RiskTool,
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
    parser.add_argument("--features-path", help="Feature parquet path for ML tools.")
    parser.add_argument("--model-path", help="Model path for MLBacktestTool.")
    parser.add_argument("--targets-path", help="Target weights parquet path for RiskTool.")
    parser.add_argument("--equity-path", help="Equity curve path for RiskTool.")
    parser.add_argument("--output-dir", help="Output directory for selected tool.")
    parser.add_argument("--output-path", help="Output file path for ReportTool.")
    parser.add_argument("--tool-config", help="Backtest or train config path.")
    parser.add_argument("--risk-config", help="Risk config path for RiskTool.")
    parser.add_argument("--memory-path", help="Experiment memory path for ReportTool.")
    parser.add_argument("--experiment-name", help="Experiment name for run tools.")
    parser.add_argument("--symbols", nargs="*", help="Symbols for PipelineTool.")
    parser.add_argument("--start", help="Pipeline start date.")
    parser.add_argument("--end", help="Pipeline end date.")
    parser.add_argument("--raw-dir", help="Raw data directory for PipelineTool.")
    parser.add_argument("--features-dir", help="Features directory for PipelineTool.")
    parser.add_argument("--features-config", help="Feature config path for PipelineTool.")
    parser.add_argument("--backtest-config", help="Backtest config path for PipelineTool.")
    parser.add_argument("--strategy-name", help="Strategy name for PipelineTool.")
    parser.add_argument("--clip", action="store_true", default=None, help="Clip risk targets.")
    parser.add_argument("--no-clip", action="store_false", dest="clip", help="Reject instead of clipping risk targets.")
    parser.add_argument("--download", action="store_false", dest="skip_download", help="Allow PipelineTool to download data.")
    parser.add_argument("--build-features", action="store_false", dest="skip_features", help="Allow PipelineTool to build features.")
    parser.set_defaults(skip_download=True, skip_features=True)
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
            MLBacktestTool(),
            PipelineTool(),
            RiskTool(),
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
        features_path=args.features_path,
        model_path=args.model_path,
        targets_path=args.targets_path,
        equity_path=args.equity_path,
        output_dir=args.output_dir,
        output_path=args.output_path,
        tool_config=args.tool_config,
        config_path=args.tool_config,
        risk_config_path=args.risk_config,
        memory_path=args.memory_path,
        experiment_name=args.experiment_name,
        symbols=args.symbols,
        start=args.start,
        end=args.end,
        raw_dir=args.raw_dir,
        features_dir=args.features_dir,
        features_config=args.features_config,
        backtest_config=args.backtest_config,
        strategy_name=args.strategy_name,
        clip=args.clip,
        skip_download=args.skip_download,
        skip_features=args.skip_features,
    )
    print(result)
    if args.events:
        print(json.dumps([asdict(event) for event in supervisor.events], indent=2))


if __name__ == "__main__":
    main()
