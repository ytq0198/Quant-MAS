"""Run simulation-only competitive learning experiments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quant_mas.agents import (
    AgentSpec,
    PopulationManager,
    RiskAgent,
    build_strategy_agent,
)
from quant_mas.memory import ExperimentMemory
from quant_mas.risk import RiskLimits
from quant_mas.rl import CompetitiveEpisodeRunner, CompetitiveRunConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simulation-only competitive experiment.")
    parser.add_argument("--config", default="configs/competitive.yaml")
    parser.add_argument(
        "--mode",
        choices=["mock", "walk_forward"],
        help="Run mode. walk_forward is a stub in M11 and does not fabricate OOS metrics.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write ExperimentMemory.")
    parser.add_argument("--output-dir", help="Override output directory.")
    parser.add_argument("--seed", type=int, help="Override deterministic seed.")
    parser.add_argument("--memory-path", help="Override ExperimentMemory JSON path.")
    return parser


def run_competitive_experiment(
    *,
    config_path: str | Path = "configs/competitive.yaml",
    mode: str | None = None,
    dry_run: bool = False,
    output_dir: str | Path | None = None,
    seed: int | None = None,
    memory_path: str | Path | None = None,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    competitive_config = dict(config.get("competitive", {}))
    selected_mode = mode or str(competitive_config.get("mode", "mock"))
    if selected_mode == "walk_forward":
        raise NotImplementedError(
            "walk_forward competitive mode is a future hook; M11 only supports mock simulation."
        )
    if selected_mode != "mock":
        raise ValueError("mode must be mock or walk_forward")
    if seed is not None:
        competitive_config["seed"] = seed
    run_config = CompetitiveRunConfig(
        n_windows=int(competitive_config.get("n_windows", 3)),
        bars_per_window=int(competitive_config.get("bars_per_window", 32)),
        seed=int(competitive_config.get("seed", 42)),
        aggregation=str(competitive_config.get("aggregation", "mean")),
    )
    top_k = int(competitive_config.get("top_k", 2))
    population_config = config.get("population", {})
    population = PopulationManager(
        initial_elo=float(population_config.get("initial_elo", 1500.0)),
        k_factor=float(population_config.get("k_factor", 32.0)),
        top_k_size=top_k,
    )
    agents = []
    for item in config.get("agents", []):
        spec = AgentSpec(
            agent_id=str(item["id"]),
            agent_type=str(item["type"]),
            params=dict(item.get("params", {})),
            elo=float(item.get("elo", population.initial_elo)),
        )
        population.register(spec)
        agents.append(build_strategy_agent(spec.agent_id, spec.agent_type, spec.params))
    if len(agents) < 2:
        raise ValueError("competitive experiment requires at least two agents")
    paths = config.get("paths", {})
    market_data = _load_market_data(paths.get("market_data"))
    risk_agent = RiskAgent(RiskLimits.from_dict(config.get("risk", {})))
    summary = CompetitiveEpisodeRunner(
        agents=agents,
        risk_agent=risk_agent,
        population=population,
        config=run_config,
        market_data=market_data,
    ).run_mock()
    artifacts: dict[str, str] = {}
    if not dry_run:
        destination = Path(output_dir or paths.get("output_dir", "outputs/competitive")).expanduser()
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        summary_path = destination / "summary.md"
        metrics_path.write_text(
            json.dumps(summary["metrics"], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        summary_path.write_text(_summary_markdown(config=config, summary=summary), encoding="utf-8")
        artifacts = {"metrics": str(metrics_path), "summary": str(summary_path)}
    record = None
    if not dry_run:
        record = ExperimentMemory(
            memory_path or config.get("memory", {}).get("json_path", "outputs/reports/experiments.json")
        ).add(
            name=str(config.get("experiment", {}).get("name", "competitive_mock_001")),
            metrics=summary["metrics"],
            artifacts=artifacts,
            params={
                "family": str(config.get("experiment", {}).get("family", "competitive_learning")),
                "competitive": run_config.__dict__,
                "simulation_only": True,
            },
            notes="M11 competitive learning mock simulation; not a walk-forward OOS result.",
        )
    return {
        **summary,
        "artifacts": artifacts,
        "experiment_id": record.experiment_id if record else None,
        "dry_run": dry_run,
    }


def main() -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_competitive_experiment(
            config_path=args.config,
            mode=args.mode,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
            seed=args.seed,
            memory_path=args.memory_path,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"[competitive] ERROR: {exc}", file=sys.stderr)
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


def _summary_markdown(*, config: dict[str, Any], summary: dict[str, Any]) -> str:
    baseline = config.get("baseline", {})
    metrics = summary["metrics"]
    lines = [
        "# Competitive Learning Mock Run",
        "",
        "- simulation_only: true",
        f"- top_agent: {metrics['population']['top_agent']}",
        f"- population.elo_top: {metrics['population']['elo_top']:.3f}",
        f"- simulation.sharpe_mean: {metrics['simulation']['sharpe']:.6f}",
        "",
        "## OOS Baseline Context",
        (
            f"Paper-level baseline remains {baseline.get('oos_reference', 'EXP-20260602-008')} "
            f"with walk-forward oos.sharpe {baseline.get('oos_sharpe', 0.586)}. "
            "Population Elo and simulation metrics are auxiliary and must not be treated as OOS evidence."
        ),
        "",
        "## Rankings",
    ]
    for item in summary["rankings"]:
        lines.append(f"- {item['agent_id']}: elo={item['elo']:.3f}, type={item['agent_type']}")
    return "\n".join(lines) + "\n"


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
