from __future__ import annotations

from quant_mas.rl import (
    CandidateRun,
    rank_candidates_by_group_relative_reward,
    summarize_grpo_ranking,
)


def test_single_group_ranking_order() -> None:
    candidates = [
        CandidateRun("b", "random", 1, 0.1),
        CandidateRun("a", "buy_hold", 1, 0.3),
    ]

    ranked = rank_candidates_by_group_relative_reward(candidates)

    assert [item.name for item in ranked] == ["a", "b"]
    assert ranked[0].rank == 1


def test_multi_group_relative_ranking_is_group_local() -> None:
    candidates = [
        CandidateRun("w1_low", "random", 1, 1.0),
        CandidateRun("w1_high", "buy_hold", 1, 2.0),
        CandidateRun("w2_low", "random", 2, 10.0),
        CandidateRun("w2_high", "buy_hold", 2, 11.0),
    ]

    ranked = rank_candidates_by_group_relative_reward(candidates)
    by_name = {item.name: item for item in ranked}

    assert by_name["w1_high"].relative_reward == by_name["w2_high"].relative_reward
    assert by_name["w1_high"].rank == 1
    assert by_name["w2_high"].rank == 1


def test_group_mean_subtraction_sets_relative_reward() -> None:
    ranked = rank_candidates_by_group_relative_reward(
        [
            CandidateRun("a", "p", 1, 1.0),
            CandidateRun("b", "p", 1, 3.0),
        ]
    )

    assert ranked[0].group_mean == 2.0
    assert ranked[0].relative_reward == 1.0


def test_empty_candidates_returns_empty_list() -> None:
    assert rank_candidates_by_group_relative_reward([]) == []


def test_summarize_grpo_ranking_reports_top_candidate() -> None:
    ranked = rank_candidates_by_group_relative_reward(
        [
            CandidateRun("a", "random", 1, 0.1),
            CandidateRun("b", "buy_hold", 1, 0.2),
        ]
    )

    summary = summarize_grpo_ranking(ranked)

    assert summary["top_candidate"] == "b"
    assert summary["candidate_count"] == 2
    assert summary["simulation_only"] is True


def test_tie_breaking_is_deterministic_by_name() -> None:
    ranked = rank_candidates_by_group_relative_reward(
        [
            CandidateRun("z", "random", 1, 1.0),
            CandidateRun("a", "buy_hold", 1, 1.0),
        ]
    )

    assert [item.name for item in ranked] == ["a", "z"]
