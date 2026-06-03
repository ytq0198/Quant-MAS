"""Deterministic Elo utilities for population simulation."""

from __future__ import annotations


def expected_score(rating_a: float, rating_b: float) -> float:
    """Return player A's expected score against player B."""
    return float(1.0 / (1.0 + 10 ** ((float(rating_b) - float(rating_a)) / 400.0)))


def update_elo(
    rating: float,
    expected: float,
    score: float,
    *,
    k: float = 32.0,
) -> float:
    """Update one Elo rating from expected and actual score."""
    if k <= 0:
        raise ValueError("k must be positive")
    if not 0.0 <= expected <= 1.0:
        raise ValueError("expected must be in [0, 1]")
    if score not in {0.0, 0.5, 1.0}:
        raise ValueError("score must be 0.0, 0.5, or 1.0")
    return float(rating + k * (score - expected))


def update_pair(
    rating_a: float,
    rating_b: float,
    *,
    score_a: float,
    k: float = 32.0,
) -> tuple[float, float]:
    """Update both sides of a two-agent match."""
    expected_a = expected_score(rating_a, rating_b)
    expected_b = expected_score(rating_b, rating_a)
    return (
        update_elo(rating_a, expected_a, score_a, k=k),
        update_elo(rating_b, expected_b, 1.0 - score_a, k=k),
    )
