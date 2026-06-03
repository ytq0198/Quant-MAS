"""Population management for simulation-only competitive learning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any

from quant_mas.agents.strategy_agent import AgentEvaluation


@dataclass
class AgentSpec:
    """Serializable strategy-agent specification."""

    agent_id: str
    agent_type: str
    params: dict[str, Any] = field(default_factory=dict)
    elo: float = 1500.0


@dataclass(frozen=True)
class GenerationResult:
    """Summary of deterministic autocurriculum candidates."""

    generation: int
    candidates: list[AgentSpec]


class PopulationManager:
    """Track agent specs, evaluations, Elo ratings, and Top-K rankings."""

    def __init__(
        self,
        *,
        initial_elo: float = 1500.0,
        k_factor: float = 32.0,
        top_k_size: int = 2,
    ) -> None:
        if k_factor <= 0:
            raise ValueError("k_factor must be positive")
        if top_k_size <= 0:
            raise ValueError("top_k_size must be positive")
        self.initial_elo = float(initial_elo)
        self.k_factor = float(k_factor)
        self.top_k_size = int(top_k_size)
        self.specs: dict[str, AgentSpec] = {}
        self.evaluations: list[AgentEvaluation] = []
        self.matches: list[dict[str, Any]] = []
        self.generation = 0

    def register(self, spec: AgentSpec) -> None:
        if spec.agent_id in self.specs:
            raise ValueError(f"Duplicate agent_id: {spec.agent_id}")
        if spec.elo == 1500.0 and self.initial_elo != 1500.0:
            spec = replace(spec, elo=self.initial_elo)
        self.specs[spec.agent_id] = spec

    def record_match(self, winner_id: str, loser_id: str, *, window_id: int) -> None:
        from quant_mas.rl.elo_rating import update_pair

        if winner_id == loser_id:
            raise ValueError("winner_id and loser_id must differ")
        winner = self._require_spec(winner_id)
        loser = self._require_spec(loser_id)
        winner_elo, loser_elo = update_pair(
            winner.elo,
            loser.elo,
            score_a=1.0,
            k=self.k_factor,
        )
        winner.elo = winner_elo
        loser.elo = loser_elo
        self.matches.append(
            {
                "winner_id": winner_id,
                "loser_id": loser_id,
                "window_id": int(window_id),
                "winner_elo": winner_elo,
                "loser_elo": loser_elo,
            }
        )

    def record_draw(self, agent_a_id: str, agent_b_id: str, *, window_id: int) -> None:
        from quant_mas.rl.elo_rating import update_pair

        first = self._require_spec(agent_a_id)
        second = self._require_spec(agent_b_id)
        first.elo, second.elo = update_pair(
            first.elo,
            second.elo,
            score_a=0.5,
            k=self.k_factor,
        )
        self.matches.append(
            {
                "winner_id": None,
                "loser_id": None,
                "draw": [agent_a_id, agent_b_id],
                "window_id": int(window_id),
            }
        )

    def record_evaluation(self, evaluation: AgentEvaluation) -> None:
        self._require_spec(evaluation.agent_id)
        self.evaluations.append(evaluation)

    def rankings(self) -> list[AgentSpec]:
        return sorted(self.specs.values(), key=lambda spec: (-spec.elo, spec.agent_id))

    def top_k(self, k: int) -> list[AgentSpec]:
        if k <= 0:
            raise ValueError("k must be positive")
        return self.rankings()[:k]

    def next_generation(self, *, mutate_sigma: float = 0.05) -> list[AgentSpec]:
        """Copy Top-K params with deterministic jitter for M12 training loops."""
        if mutate_sigma < 0:
            raise ValueError("mutate_sigma must be non-negative")
        self.generation += 1
        candidates: list[AgentSpec] = []
        for rank, spec in enumerate(self.top_k(self.top_k_size), start=1):
            params = _mutate_params(spec.params, sigma=mutate_sigma, rank=rank, generation=self.generation)
            candidates.append(
                AgentSpec(
                    agent_id=f"{spec.agent_id}_g{self.generation}_{rank}",
                    agent_type=spec.agent_type,
                    params=params,
                    elo=self.initial_elo,
                )
            )
        return candidates

    def export_state(self) -> dict[str, Any]:
        rankings = [asdict(spec) for spec in self.rankings()]
        return {
            "initial_elo": self.initial_elo,
            "k_factor": self.k_factor,
            "top_k_size": self.top_k_size,
            "generation": self.generation,
            "rankings": rankings,
            "matches": list(self.matches),
            "evaluations": [
                {
                    "agent_id": item.agent_id,
                    "metrics": item.metrics,
                    "reward": item.reward,
                    "window_id": item.window_id,
                }
                for item in self.evaluations
            ],
        }

    def _require_spec(self, agent_id: str) -> AgentSpec:
        if agent_id not in self.specs:
            raise ValueError(f"Unknown agent_id: {agent_id}")
        return self.specs[agent_id]


def _mutate_params(
    params: dict[str, Any],
    *,
    sigma: float,
    rank: int,
    generation: int,
) -> dict[str, Any]:
    mutated: dict[str, Any] = {}
    jitter = sigma * (generation + rank) / 10.0
    for key, value in params.items():
        if isinstance(value, bool):
            mutated[key] = value
        elif isinstance(value, int):
            mutated[key] = max(1, int(round(value + jitter)))
        elif isinstance(value, float):
            mutated[key] = float(value + jitter)
        else:
            mutated[key] = value
    return mutated
