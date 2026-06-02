"""Node execution context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quant_mas.orchestration.langgraph_state import QuantWorkflowState


@dataclass(frozen=True)
class NodeContext:
    """Paths and flags shared across workflow nodes."""

    work_dir: Path
    storage_config: Path
    features_config: Path
    train_config: Path
    ml_backtest_config: Path
    risk_config: Path
    dry_run: bool

    @classmethod
    def from_state(cls, state: QuantWorkflowState) -> "NodeContext":
        report_output_dir = state.get("report_output_dir")
        work_dir = (
            Path(report_output_dir).expanduser().parent
            if report_output_dir
            else Path("outputs") / "workflow_dry_run"
        )
        work_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            work_dir=work_dir,
            storage_config=Path(state["storage_config"]).expanduser(),
            features_config=Path(state["features_config"]).expanduser(),
            train_config=Path(state["train_config"]).expanduser(),
            ml_backtest_config=Path(state["ml_backtest_config"]).expanduser(),
            risk_config=Path(state["risk_config"]).expanduser(),
            dry_run=bool(state["dry_run"]),
        )
