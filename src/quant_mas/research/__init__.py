"""Research baseline and experiment comparison utilities."""

from quant_mas.research.baseline import BaselineRegistry, BaselineRun
from quant_mas.research.candidate_validation import (
    CandidateBatchValidationResult,
    CandidateStrategyAdapter,
    CandidateValidationResult,
    build_candidate_oos_comparison,
    run_candidate_batch_walk_forward,
    run_candidate_walk_forward,
    save_candidate_batch_validation_report,
    save_candidate_validation_report,
)
from quant_mas.research.metrics_table import (
    build_comparison_table,
    collect_experiment_metrics,
)
from quant_mas.research.strategy_candidate import StrategyCandidate, assert_no_oos_metrics

__all__ = [
    "BaselineRegistry",
    "BaselineRun",
    "CandidateBatchValidationResult",
    "CandidateStrategyAdapter",
    "CandidateValidationResult",
    "StrategyCandidate",
    "assert_no_oos_metrics",
    "build_candidate_oos_comparison",
    "build_comparison_table",
    "collect_experiment_metrics",
    "run_candidate_batch_walk_forward",
    "run_candidate_walk_forward",
    "save_candidate_batch_validation_report",
    "save_candidate_validation_report",
]
