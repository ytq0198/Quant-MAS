"""Simulation-only RL utilities for Quant MAS."""

from quant_mas.rl.baseline_policy import (
    BuyAndHoldPolicy,
    MLCopyPolicy,
    Policy,
    RandomPolicy,
    build_policy,
)
from quant_mas.rl.candidate_bridge import (
    extract_top_candidates,
    run_candidate_backtest_smoke,
    walk_forward_stub,
    write_candidates,
)
from quant_mas.rl.env_schema import RewardConfig, StepResult, TradingEnvConfig
from quant_mas.rl.competitive_runner import CompetitiveEpisodeRunner, CompetitiveRunConfig
from quant_mas.rl.elo_rating import expected_score, update_elo, update_pair
from quant_mas.rl.grpo_experiment import (
    CandidateRun,
    rank_candidates_by_group_relative_reward,
    summarize_grpo_ranking,
)
from quant_mas.rl.grpo_agent import GRPOPolicyAgent, PolicyState
from quant_mas.rl.marl_stub import MARLTrainingStub, MultiAgentTrainingProtocol
from quant_mas.rl.mock_data import build_synthetic_ml_signals, build_synthetic_ohlcv
from quant_mas.rl.population_training import (
    GenerationSummary,
    PopulationTrainingConfig,
    PopulationTrainingLoop,
)
from quant_mas.rl.ppo_trainer import PPOTrainer, TrainerProtocol
from quant_mas.rl.reward import compute_episode_metrics, compute_step_reward
from quant_mas.rl.training_loop import (
    RLTrainingLoop,
    TrajectoryRecord,
    TrainingRunResult,
    schedule_walk_forward_eval_stub,
)
from quant_mas.rl.trading_env import TradingEnv

__all__ = [
    "BuyAndHoldPolicy",
    "CandidateRun",
    "CompetitiveEpisodeRunner",
    "CompetitiveRunConfig",
    "GRPOPolicyAgent",
    "GenerationSummary",
    "MARLTrainingStub",
    "MLCopyPolicy",
    "MultiAgentTrainingProtocol",
    "PPOTrainer",
    "Policy",
    "PolicyState",
    "PopulationTrainingConfig",
    "PopulationTrainingLoop",
    "RLTrainingLoop",
    "RandomPolicy",
    "RewardConfig",
    "StepResult",
    "TrainerProtocol",
    "TradingEnv",
    "TradingEnvConfig",
    "TrajectoryRecord",
    "TrainingRunResult",
    "build_policy",
    "build_synthetic_ml_signals",
    "build_synthetic_ohlcv",
    "compute_episode_metrics",
    "compute_step_reward",
    "extract_top_candidates",
    "expected_score",
    "rank_candidates_by_group_relative_reward",
    "run_candidate_backtest_smoke",
    "schedule_walk_forward_eval_stub",
    "summarize_grpo_ranking",
    "update_elo",
    "update_pair",
    "walk_forward_stub",
    "write_candidates",
]
