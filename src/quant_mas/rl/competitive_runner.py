"""Competitive mock runner for strategy-agent populations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from quant_mas.agents.population_manager import PopulationManager
from quant_mas.agents.risk_agent import RiskAgent
from quant_mas.agents.strategy_agent import AgentEvaluation, StrategyAgent
from quant_mas.rl.env_schema import TradingEnvConfig
from quant_mas.rl.mock_data import build_synthetic_ohlcv
from quant_mas.rl.trading_env import TradingEnv


@dataclass(frozen=True)
class CompetitiveRunConfig:
    """Configuration for the first mock competitive runner."""

    n_windows: int = 3
    bars_per_window: int = 32
    seed: int = 42
    aggregation: str = "mean"

    def __post_init__(self) -> None:
        if self.n_windows <= 0:
            raise ValueError("n_windows must be positive")
        if self.bars_per_window < 2:
            raise ValueError("bars_per_window must be at least 2")
        if self.aggregation not in {"mean", "best_elo"}:
            raise ValueError("aggregation must be mean or best_elo")


class CompetitiveEpisodeRunner:
    """Run multiple strategy agents on shared market windows using shadow envs."""

    def __init__(
        self,
        *,
        agents: list[StrategyAgent],
        risk_agent: RiskAgent,
        population: PopulationManager,
        config: CompetitiveRunConfig,
        market_data: pd.DataFrame | None = None,
    ) -> None:
        if len(agents) < 2:
            raise ValueError("CompetitiveEpisodeRunner requires at least two agents")
        self.agents = agents
        self.risk_agent = risk_agent
        self.population = population
        self.config = config
        self.market_data = (
            market_data.copy()
            if market_data is not None
            else build_synthetic_ohlcv(config.n_windows * config.bars_per_window + 1)
        )

    def run_mock(self) -> dict[str, Any]:
        """Run deterministic simulation-only windows and update population Elo."""
        evaluations: list[AgentEvaluation] = []
        window_results: list[dict[str, Any]] = []
        for window_id, window in enumerate(self._windows()):
            per_window: list[AgentEvaluation] = []
            for agent in self.agents:
                evaluation = self._run_agent_window(agent, window, window_id=window_id)
                self.population.record_evaluation(evaluation)
                evaluations.append(evaluation)
                per_window.append(evaluation)
            self._update_window_elo(per_window, window_id=window_id)
            window_results.append(
                {
                    "window_id": window_id,
                    "evaluations": [
                        {
                            "agent_id": item.agent_id,
                            "reward": item.reward,
                            "metrics": item.metrics,
                        }
                        for item in sorted(per_window, key=lambda item: (-item.reward, item.agent_id))
                    ],
                }
            )

        rankings = self.population.rankings()
        top = rankings[0]
        metrics = _aggregate_metrics(evaluations)
        summary = {
            "simulation_only": True,
            "config": asdict(self.config),
            "metrics": {
                "population": {
                    "elo_top": float(top.elo),
                    "top_agent": top.agent_id,
                    "agent_count": float(len(self.agents)),
                    "windows": float(self.config.n_windows),
                },
                "simulation": metrics,
            },
            "rankings": [asdict(spec) for spec in rankings],
            "windows": window_results,
            "population_state": self.population.export_state(),
        }
        _assert_no_oos_metrics(summary["metrics"])
        return summary

    def _run_agent_window(
        self,
        agent: StrategyAgent,
        window: pd.DataFrame,
        *,
        window_id: int,
    ) -> AgentEvaluation:
        env = TradingEnv(
            window,
            config=TradingEnvConfig(max_steps=len(window) - 1),
            risk_limits=self.risk_agent.limits,
        )
        observation, info = env.reset(seed=self.config.seed + window_id)
        equity_curve = [float(info.get("equity", 100_000.0))]
        total_reward = 0.0
        terminated = truncated = False
        while not (terminated or truncated):
            proposal = agent.propose(observation, info)
            adjusted = self.risk_agent.apply(
                proposal,
                current_weight=float(info.get("position_weight", 0.0)),
                equity=float(info.get("equity", 100_000.0)),
            )
            result = env.step(_nearest_action_index(adjusted.target_weight, env.config.action_levels))
            observation = result.observation
            info = result.info
            total_reward += float(result.reward)
            equity_curve.append(float(info["equity"]))
            terminated = result.terminated
            truncated = result.truncated
        evaluation = agent.evaluate_episode(equity_curve, window_id=window_id)
        return AgentEvaluation(
            agent_id=evaluation.agent_id,
            metrics=evaluation.metrics,
            reward=float(evaluation.reward + total_reward),
            window_id=window_id,
        )

    def _update_window_elo(self, evaluations: list[AgentEvaluation], *, window_id: int) -> None:
        ordered = sorted(evaluations, key=lambda item: (-item.reward, item.agent_id))
        for left_index, left in enumerate(ordered):
            for right in ordered[left_index + 1 :]:
                if left.reward == right.reward:
                    self.population.record_draw(left.agent_id, right.agent_id, window_id=window_id)
                else:
                    self.population.record_match(left.agent_id, right.agent_id, window_id=window_id)

    def _windows(self) -> list[pd.DataFrame]:
        data = self.market_data.sort_values("date").reset_index(drop=True)
        windows = []
        for window_id in range(self.config.n_windows):
            start = window_id * self.config.bars_per_window
            stop = start + self.config.bars_per_window
            window = data.iloc[start:stop].copy()
            if len(window) < 2:
                raise ValueError("Not enough market data for configured windows")
            windows.append(window.reset_index(drop=True))
        return windows


def _nearest_action_index(target_weight: float, action_levels: tuple[float, ...]) -> int:
    distances = [abs(float(level) - float(target_weight)) for level in action_levels]
    return int(min(range(len(action_levels)), key=lambda index: (distances[index], index)))


def _aggregate_metrics(evaluations: list[AgentEvaluation]) -> dict[str, float]:
    if not evaluations:
        return {"sharpe": 0.0, "total_return": 0.0, "max_drawdown": 0.0, "reward_mean": 0.0}
    keys = ["simulation.sharpe", "simulation.total_return", "simulation.max_drawdown"]
    result = {}
    for key in keys:
        short_key = key.removeprefix("simulation.")
        result[short_key] = float(
            sum(item.metrics.get(key, 0.0) for item in evaluations) / len(evaluations)
        )
    result["reward_mean"] = float(sum(item.reward for item in evaluations) / len(evaluations))
    return result


def _assert_no_oos_metrics(metrics: dict[str, Any]) -> None:
    if "oos" in metrics:
        raise ValueError("Competitive simulation metrics must not contain oos metrics")
    for value in metrics.values():
        if isinstance(value, dict):
            _assert_no_oos_metrics(value)
