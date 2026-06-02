"""Run a moving-average cross backtest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from quant_mas.backtest import (
    BacktestEngine,
    CommissionModel,
    SlippageModel,
    save_backtest_report,
)
from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.memory import ExperimentMemory
from quant_mas.strategies import MovingAverageCrossStrategy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a backtest.")
    parser.add_argument("--config", default="configs/backtest.yaml", help="Backtest config path.")
    parser.add_argument(
        "--storage-config",
        default="configs/storage.yaml",
        help="Storage config path.",
    )
    parser.add_argument(
        "--input",
        help="Input OHLCV parquet path. Defaults to raw_data_dir/market_data.parquet.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for backtest outputs. Defaults to reports_dir/backtest_latest.",
    )
    parser.add_argument(
        "--experiment-name",
        default="moving_average_cross_backtest",
        help="Experiment name recorded in experiment memory.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    with Path(args.config).expanduser().open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    catalog = DataCatalog.from_yaml(args.storage_config)
    input_path = (
        Path(args.input).expanduser()
        if args.input
        else catalog.path_for("raw_data_dir", "market_data.parquet")
    )
    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else catalog.path_for("reports_dir", "backtest_latest")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    strategy_config = config.get("strategy", {})
    if strategy_config.get("name", "moving_average_cross") != "moving_average_cross":
        raise ValueError("Only moving_average_cross is supported in this phase")

    strategy = MovingAverageCrossStrategy(
        fast_window=strategy_config.get("fast_window", 5),
        slow_window=strategy_config.get("slow_window", 20),
    )
    engine = BacktestEngine(
        strategy=strategy,
        initial_cash=config.get("portfolio", {}).get("initial_cash", 100_000.0),
        commission_model=CommissionModel(config.get("costs", {}).get("commission_bps", 0.0)),
        slippage_model=SlippageModel(config.get("costs", {}).get("slippage_bps", 0.0)),
    )

    storage = ParquetStorage()
    result = engine.run(storage.load(input_path))
    artifacts = save_backtest_report(
        result,
        output_dir,
        title=args.experiment_name,
        params=config,
    )
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=args.experiment_name,
        metrics=result.metrics,
        artifacts=artifacts,
        params=config,
    )
    print(f"Saved backtest outputs to {output_dir}")
    print(json.dumps(result.metrics, indent=2))


if __name__ == "__main__":
    main()
