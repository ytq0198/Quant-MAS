"""Bridge population winners into auditable strategy candidates."""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.backtest import BacktestEngine
from quant_mas.research import StrategyCandidate, assert_no_oos_metrics
from quant_mas.rl.mock_data import build_synthetic_ohlcv
from quant_mas.strategies import Strategy


def extract_top_candidates(
    population_result: dict[str, Any],
    *,
    top_k: int = 2,
) -> list[StrategyCandidate]:
    """Extract Top-K candidates from a population training result."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    rankings = population_result.get("final_rankings") or population_result.get("rankings") or []
    candidates: list[StrategyCandidate] = []
    for rank, item in enumerate(rankings[:top_k], start=1):
        metrics = _selection_metrics(population_result, item=item, rank=rank)
        candidates.append(
            StrategyCandidate(
                candidate_id=f"cand_{_slug(item['agent_id'])}",
                source="population_training",
                agent_id=str(item["agent_id"]),
                agent_type=str(item["agent_type"]),
                params=dict(item.get("params", {})),
                selection_metrics=metrics,
                notes="Selected from population ranking; requires Quant Engine validation.",
            )
        )
    return candidates


def write_candidates(
    candidates: list[StrategyCandidate],
    output_dir: str | Path,
) -> dict[str, str]:
    """Write candidates as JSON and CSV."""
    destination = Path(output_dir).expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "candidates.json"
    csv_path = destination / "candidates.csv"
    json_path.write_text(
        json.dumps([item.to_dict() for item in candidates], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "candidate_id",
                "agent_id",
                "agent_type",
                "population_rank",
                "population_elo",
                "simulation_reward_mean",
                "backtest_sharpe",
            ],
        )
        writer.writeheader()
        for item in candidates:
            writer.writerow(
                {
                    "candidate_id": item.candidate_id,
                    "agent_id": item.agent_id,
                    "agent_type": item.agent_type,
                    "population_rank": item.selection_metrics.get("population.rank"),
                    "population_elo": item.selection_metrics.get("population.elo"),
                    "simulation_reward_mean": item.selection_metrics.get("simulation.reward_mean"),
                    "backtest_sharpe": item.validation_metrics.get("backtest.sharpe"),
                }
            )
    return {"candidates_json": str(json_path), "candidates_csv": str(csv_path)}


def run_candidate_backtest_smoke(
    candidate: StrategyCandidate,
    market_data: pd.DataFrame | None = None,
) -> StrategyCandidate:
    """Run a small deterministic backtest smoke for one candidate."""
    data = market_data.copy() if market_data is not None else build_synthetic_ohlcv(64)
    result = BacktestEngine(_CandidateStrategy(candidate)).run(data)
    metrics = {f"backtest.{key}": value for key, value in result.metrics.items()}
    assert_no_oos_metrics(metrics)
    return replace(
        candidate,
        validation_metrics={**candidate.validation_metrics, **metrics},
    )


def walk_forward_stub(candidate: StrategyCandidate) -> dict[str, Any]:
    """Return explicit walk-forward stub metadata without producing OOS metrics."""
    return {
        "candidate_id": candidate.candidate_id,
        "status": "stub",
        "message": "Walk-forward OOS validation is not run in M11.6; no oos metrics were produced.",
    }


class _CandidateStrategy(Strategy):
    def __init__(self, candidate: StrategyCandidate) -> None:
        self.candidate = candidate

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        frame["date"] = pd.to_datetime(frame["date"])
        rows = []
        for symbol, group in frame.sort_values(["symbol", "date"]).groupby("symbol", sort=True):
            close = group["close"].astype(float)
            last_return = close.pct_change().fillna(0.0)
            scale = float(self.candidate.params.get("scale", 1.0))
            if self.candidate.agent_type == "momentum":
                target = (0.5 + scale * last_return * 10.0).clip(0.0, 1.0)
            elif self.candidate.agent_type == "mean_reversion":
                target = (0.5 - scale * last_return * 10.0).clip(0.0, 1.0)
            else:
                raise ValueError("Unsupported candidate agent_type for backtest smoke")
            rows.append(
                pd.DataFrame(
                    {
                        "date": group["date"].to_numpy(),
                        "symbol": symbol,
                        "target_weight": target.to_numpy(),
                    }
                )
            )
        return pd.concat(rows, ignore_index=True)


def _selection_metrics(
    population_result: dict[str, Any],
    *,
    item: dict[str, Any],
    rank: int,
) -> dict[str, Any]:
    metrics = population_result.get("metrics", {})
    generation_metrics = {}
    generations = population_result.get("generations") or []
    if generations:
        generation_metrics = generations[-1].get("metrics", {})
    simulation = metrics.get("simulation", generation_metrics.get("simulation", {}))
    selected = {
        "population.rank": float(rank),
        "population.elo": float(item.get("elo", 0.0)),
        "simulation.reward_mean": float(simulation.get("reward_mean", 0.0)),
        "simulation.sharpe_mean": float(simulation.get("sharpe_mean", simulation.get("sharpe", 0.0))),
    }
    assert_no_oos_metrics(selected)
    return selected


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in str(value)).strip("_")
