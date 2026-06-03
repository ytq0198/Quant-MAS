"""Population training loop for simulation-only competitive learning."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.agents import AgentSpec, PopulationManager, RiskAgent, build_strategy_agent
from quant_mas.memory import ExperimentMemory
from quant_mas.rl.competitive_runner import CompetitiveEpisodeRunner, CompetitiveRunConfig
from quant_mas.rl.mock_data import build_synthetic_ohlcv


@dataclass(frozen=True)
class PopulationTrainingConfig:
    """Configuration for a short, deterministic population training loop."""

    generations: int = 3
    n_windows: int = 3
    bars_per_window: int = 32
    top_k: int = 2
    mutate_sigma: float = 0.05
    seed: int = 42
    output_dir: Path = Path("outputs/population_training")
    simulation_only: bool = True

    def __post_init__(self) -> None:
        if self.generations <= 0:
            raise ValueError("generations must be positive")
        if self.n_windows <= 0:
            raise ValueError("n_windows must be positive")
        if self.bars_per_window < 2:
            raise ValueError("bars_per_window must be at least 2")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.mutate_sigma < 0:
            raise ValueError("mutate_sigma must be non-negative")
        if not self.simulation_only:
            raise ValueError("Population training is simulation-only in M11.5")


@dataclass(frozen=True)
class GenerationSummary:
    """One generation result with auditable metrics and artifact paths."""

    generation: int
    top_agent: str
    elo_top: float
    rankings: list[dict[str, Any]]
    metrics: dict[str, Any]
    artifacts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PopulationTrainingLoop:
    """Evaluate, rank, mutate, and re-evaluate a strategy-agent population."""

    def __init__(
        self,
        *,
        initial_specs: list[AgentSpec],
        config: PopulationTrainingConfig,
        risk_agent: RiskAgent | None = None,
        market_data: pd.DataFrame | None = None,
    ) -> None:
        if len(initial_specs) < 2:
            raise ValueError("PopulationTrainingLoop requires at least two initial specs")
        self.initial_specs = initial_specs
        self.config = config
        self.risk_agent = risk_agent or RiskAgent()
        self.market_data = (
            market_data.copy()
            if market_data is not None
            else build_synthetic_ohlcv(config.n_windows * config.bars_per_window + 1)
        )

    def run(
        self,
        *,
        dry_run: bool = True,
        memory_path: str | Path | None = None,
        experiment_name: str = "population_training_mock_001",
    ) -> dict[str, Any]:
        """Run the training loop and optionally persist artifacts and memory."""
        generation_summaries: list[GenerationSummary] = []
        current_specs = [AgentSpec(spec.agent_id, spec.agent_type, dict(spec.params), spec.elo) for spec in self.initial_specs]
        output_dir = Path(self.config.output_dir).expanduser()
        artifacts: dict[str, str] = {}

        for generation in range(1, self.config.generations + 1):
            population = PopulationManager(top_k_size=self.config.top_k)
            agents = []
            for spec in current_specs:
                population.register(AgentSpec(spec.agent_id, spec.agent_type, dict(spec.params), spec.elo))
                agents.append(build_strategy_agent(spec.agent_id, spec.agent_type, spec.params))
            run_summary = CompetitiveEpisodeRunner(
                agents=agents,
                risk_agent=self.risk_agent,
                population=population,
                config=CompetitiveRunConfig(
                    n_windows=self.config.n_windows,
                    bars_per_window=self.config.bars_per_window,
                    seed=self.config.seed + generation - 1,
                ),
                market_data=self.market_data,
            ).run_mock()
            top = run_summary["rankings"][0]
            metrics = _generation_metrics(
                generation=generation,
                agent_count=len(current_specs),
                run_metrics=run_summary["metrics"],
                top=top,
            )
            generation_artifacts: dict[str, str] = {}
            if not dry_run:
                output_dir.mkdir(parents=True, exist_ok=True)
                metrics_path = output_dir / f"generation_{generation:03d}_metrics.json"
                metrics_path.write_text(
                    json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                generation_artifacts["metrics"] = str(metrics_path)
                artifacts[f"generation_{generation:03d}_metrics"] = str(metrics_path)
            generation_summaries.append(
                GenerationSummary(
                    generation=generation,
                    top_agent=str(top["agent_id"]),
                    elo_top=float(top["elo"]),
                    rankings=list(run_summary["rankings"]),
                    metrics=metrics,
                    artifacts=generation_artifacts,
                )
            )
            if generation < self.config.generations:
                current_specs = [
                    AgentSpec(item["agent_id"], item["agent_type"], dict(item.get("params", {})), float(item.get("elo", 1500.0)))
                    for item in run_summary["rankings"][: self.config.top_k]
                ]
                population = PopulationManager(top_k_size=self.config.top_k)
                for spec in current_specs:
                    population.register(spec)
                population.generation = generation - 1
                current_specs.extend(population.next_generation(mutate_sigma=self.config.mutate_sigma))

        final = generation_summaries[-1]
        aggregate_metrics = _aggregate_training_metrics(generation_summaries)
        if not dry_run:
            rankings_path = output_dir / "rankings.csv"
            summary_path = output_dir / "summary.md"
            _write_rankings(rankings_path, generation_summaries)
            summary_path.write_text(_summary_markdown(generation_summaries), encoding="utf-8")
            artifacts["rankings"] = str(rankings_path)
            artifacts["summary"] = str(summary_path)

        record = None
        if not dry_run:
            record = ExperimentMemory(memory_path or "outputs/reports/experiments.json").add(
                name=experiment_name,
                metrics=aggregate_metrics,
                artifacts=artifacts,
                params={
                    "family": "competitive_learning",
                    "simulation_only": True,
                    "config": _config_to_dict(self.config),
                },
                notes="M11.5 population training loop; auxiliary simulation metrics only.",
            )
        result = {
            "simulation_only": True,
            "generations": [item.to_dict() for item in generation_summaries],
            "final_rankings": final.rankings,
            "best_agent": final.top_agent,
            "metrics": aggregate_metrics,
            "artifacts": artifacts,
            "experiment_id": record.experiment_id if record else None,
            "dry_run": dry_run,
        }
        _assert_no_oos(result["metrics"])
        return result


def _generation_metrics(
    *,
    generation: int,
    agent_count: int,
    run_metrics: dict[str, Any],
    top: dict[str, Any],
) -> dict[str, Any]:
    simulation = run_metrics.get("simulation", {})
    return {
        "population": {
            "generation": float(generation),
            "elo_top": float(top["elo"]),
            "top_agent": str(top["agent_id"]),
            "agent_count": float(agent_count),
        },
        "simulation": {
            "sharpe_mean": float(simulation.get("sharpe", 0.0)),
            "reward_mean": float(simulation.get("reward_mean", 0.0)),
            "max_drawdown_mean": float(simulation.get("max_drawdown", 0.0)),
            "total_return_mean": float(simulation.get("total_return", 0.0)),
        },
    }


def _aggregate_training_metrics(generations: list[GenerationSummary]) -> dict[str, Any]:
    final = generations[-1]
    reward_mean = sum(item.metrics["simulation"]["reward_mean"] for item in generations) / len(generations)
    sharpe_mean = sum(item.metrics["simulation"]["sharpe_mean"] for item in generations) / len(generations)
    return {
        "population": {
            "generations": float(len(generations)),
            "final_top_agent": final.top_agent,
            "final_elo_top": float(final.elo_top),
        },
        "simulation": {
            "reward_mean": float(reward_mean),
            "sharpe_mean": float(sharpe_mean),
            "max_drawdown_mean": float(final.metrics["simulation"]["max_drawdown_mean"]),
        },
    }


def _write_rankings(path: Path, generations: list[GenerationSummary]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["generation", "rank", "agent_id", "agent_type", "elo"],
        )
        writer.writeheader()
        for generation in generations:
            for rank, item in enumerate(generation.rankings, start=1):
                writer.writerow(
                    {
                        "generation": generation.generation,
                        "rank": rank,
                        "agent_id": item["agent_id"],
                        "agent_type": item["agent_type"],
                        "elo": item["elo"],
                    }
                )


def _summary_markdown(generations: list[GenerationSummary]) -> str:
    final = generations[-1]
    lines = [
        "# Population Training Mock Run",
        "",
        "- simulation_only: true",
        f"- generations: {len(generations)}",
        f"- final_top_agent: {final.top_agent}",
        f"- final_elo_top: {final.elo_top:.3f}",
        "",
        "Population metrics are not walk-forward OOS metrics.",
        "Paper baseline remains EXP-20260602-008 oos.sharpe 0.586.",
        "",
        "## Generations",
    ]
    for item in generations:
        lines.append(
            f"- generation {item.generation}: top={item.top_agent}, "
            f"elo={item.elo_top:.3f}, reward_mean={item.metrics['simulation']['reward_mean']:.6f}"
        )
    return "\n".join(lines) + "\n"


def _config_to_dict(config: PopulationTrainingConfig) -> dict[str, Any]:
    payload = asdict(config)
    payload["output_dir"] = str(config.output_dir)
    return payload


def _assert_no_oos(value: Any) -> None:
    if isinstance(value, dict):
        if "oos" in value:
            raise ValueError("Population training metrics must not contain oos metrics")
        for item in value.values():
            _assert_no_oos(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_oos(item)
