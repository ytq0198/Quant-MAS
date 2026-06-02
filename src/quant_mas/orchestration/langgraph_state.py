"""Workflow state for experimental orchestration."""

from __future__ import annotations

from typing import Any, TypedDict


class QuantWorkflowState(TypedDict):
    task: str
    dry_run: bool
    storage_config: str
    features_config: str
    train_config: str
    ml_backtest_config: str
    risk_config: str
    raw_path: str | None
    features_path: str | None
    model_path: str | None
    report_output_dir: str | None
    targets_path: str | None
    equity_path: str | None
    current_node: str | None
    completed_nodes: list[str]
    errors: list[str]
    events: list[dict[str, Any]]
    artifacts: dict[str, str]
    metrics: dict[str, Any]


def initial_state(**kwargs: Any) -> QuantWorkflowState:
    """Create a serializable workflow state snapshot."""
    state: QuantWorkflowState = {
        "task": "",
        "dry_run": True,
        "storage_config": "configs/storage.yaml",
        "features_config": "configs/features.yaml",
        "train_config": "configs/train.yaml",
        "ml_backtest_config": "configs/backtest_ml.yaml",
        "risk_config": "configs/risk.yaml",
        "raw_path": None,
        "features_path": None,
        "model_path": None,
        "report_output_dir": None,
        "targets_path": None,
        "equity_path": None,
        "current_node": None,
        "completed_nodes": [],
        "errors": [],
        "events": [],
        "artifacts": {},
        "metrics": {},
    }
    state.update(kwargs)
    state["completed_nodes"] = list(state.get("completed_nodes", []))
    state["errors"] = list(state.get("errors", []))
    state["events"] = list(state.get("events", []))
    state["artifacts"] = dict(state.get("artifacts", {}))
    state["metrics"] = dict(state.get("metrics", {}))
    return state
