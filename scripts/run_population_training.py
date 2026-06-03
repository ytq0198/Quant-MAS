"""Run the M11.5 simulation-only population training loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quant_mas.agents import AgentSpec, RiskAgent
from quant_mas.risk import RiskLimits
from quant_mas.rl import PopulationTrainingConfig, PopulationTrainingLoop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run population training loop.")
    parser.add_argument("--config", default="configs/population_training.yaml")
    parser.add_argument("--generations", type=int, help="Override generation count.")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Do not write artifacts or ExperimentMemory; default true.",
    )
    parser.add_argument("--output-dir", help="Override output directory.")
    parser.add_argument("--memory-path", help="Override ExperimentMemory JSON path.")
    parser.add_argument("--seed", type=int, help="Override deterministic seed.")
    return parser


def run_population_training_from_config(
    *,
    config_path: str | Path = "configs/population_training.yaml",
    generations: int | None = None,
    dry_run: bool = True,
    output_dir: str | Path | None = None,
    memory_path: str | Path | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    training_config = dict(config.get("population_training", {}))
    if generations is not None:
        training_config["generations"] = generations
    if seed is not None:
        training_config["seed"] = seed
    if output_dir is not None:
        training_config["output_dir"] = Path(output_dir)
    else:
        training_config["output_dir"] = Path(config.get("paths", {}).get("output_dir", "outputs/population_training"))
    loop_config = PopulationTrainingConfig(
        generations=int(training_config.get("generations", 3)),
        n_windows=int(training_config.get("n_windows", 3)),
        bars_per_window=int(training_config.get("bars_per_window", 32)),
        top_k=int(training_config.get("top_k", 2)),
        mutate_sigma=float(training_config.get("mutate_sigma", 0.05)),
        seed=int(training_config.get("seed", 42)),
        output_dir=Path(training_config.get("output_dir", "outputs/population_training")),
        simulation_only=bool(training_config.get("simulation_only", True)),
    )
    specs = [
        AgentSpec(
            agent_id=str(item["id"]),
            agent_type=str(item["type"]),
            params=dict(item.get("params", {})),
            elo=float(item.get("elo", 1500.0)),
        )
        for item in config.get("agents", [])
    ]
    if len(specs) < 2:
        raise ValueError("population training requires at least two agents")
    risk_agent = RiskAgent(RiskLimits.from_dict(config.get("risk", {})))
    result = PopulationTrainingLoop(
        initial_specs=specs,
        config=loop_config,
        risk_agent=risk_agent,
        market_data=_load_market_data(config.get("paths", {}).get("market_data")),
    ).run(
        dry_run=dry_run,
        memory_path=memory_path or config.get("memory", {}).get("json_path"),
        experiment_name=str(config.get("experiment", {}).get("name", "population_training_mock_001")),
    )
    return result


def main() -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_population_training_from_config(
            config_path=args.config,
            generations=args.generations,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
            memory_path=args.memory_path,
            seed=args.seed,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"[population-training] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _load_market_data(path: str | None) -> pd.DataFrame | None:
    if not path:
        return None
    source = Path(path).expanduser()
    if source.suffix.lower() == ".parquet":
        return pd.read_parquet(source)
    if source.suffix.lower() == ".csv":
        return pd.read_csv(source)
    raise ValueError("market_data must be parquet or csv")


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
