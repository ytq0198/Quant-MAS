"""GRPO-style group-relative ranking for simulation candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any


@dataclass(frozen=True)
class CandidateRun:
    """One candidate policy run in one evaluation group/window."""

    name: str
    policy: str
    window_id: int
    reward: float
    metrics: dict[str, float] = field(default_factory=dict)
    rank: int | None = None
    group_mean: float | None = None
    relative_reward: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def rank_candidates_by_group_relative_reward(
    candidates: list[CandidateRun],
    *,
    group_key: str = "window_id",
) -> list[CandidateRun]:
    """Rank candidates by group-relative reward."""
    if not candidates:
        return []
    groups: dict[Any, list[CandidateRun]] = {}
    for candidate in candidates:
        key = getattr(candidate, group_key)
        groups.setdefault(key, []).append(candidate)

    ranked: list[CandidateRun] = []
    for group_candidates in groups.values():
        mean_reward = sum(item.reward for item in group_candidates) / len(group_candidates)
        ordered = sorted(group_candidates, key=lambda item: (-item.reward, item.name))
        for rank, candidate in enumerate(ordered, start=1):
            ranked.append(
                replace(
                    candidate,
                    rank=rank,
                    group_mean=float(mean_reward),
                    relative_reward=float(candidate.reward - mean_reward),
                )
            )
    return sorted(
        ranked,
        key=lambda item: (
            -float(item.relative_reward if item.relative_reward is not None else item.reward),
            item.window_id,
            item.name,
        ),
    )


def summarize_grpo_ranking(ranked: list[CandidateRun]) -> dict[str, Any]:
    """Summarize ranked candidates for CLI and experiment metadata."""
    if not ranked:
        return {"candidate_count": 0, "top_candidate": None, "simulation_only": True}
    top = ranked[0]
    return {
        "candidate_count": len(ranked),
        "top_candidate": top.name,
        "top_policy": top.policy,
        "top_reward": top.reward,
        "top_relative_reward": top.relative_reward,
        "groups": sorted({item.window_id for item in ranked}),
        "simulation_only": True,
    }
