"""Research baseline and experiment comparison utilities."""

from quant_mas.research.baseline import BaselineRegistry, BaselineRun
from quant_mas.research.candidate_validation import (
    CandidateStrategyAdapter,
    CandidateValidationResult,
    run_candidate_walk_forward,
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
    "CandidateStrategyAdapter",
    "CandidateValidationResult",
    "StrategyCandidate",
    "assert_no_oos_metrics",
    "build_comparison_table",
    "collect_experiment_metrics",
    "run_candidate_walk_forward",
    "save_candidate_validation_report",
]
