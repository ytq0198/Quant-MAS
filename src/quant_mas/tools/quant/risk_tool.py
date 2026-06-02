"""Agent-callable risk tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.data import ParquetStorage
from quant_mas.risk import RiskDecision, RiskLimits, check_drawdown, check_position_limits
from quant_mas.tools.base import BaseTool, ToolResult


class RiskTool(BaseTool):
    """Run deterministic risk checks and return auditable metadata."""

    def __init__(self) -> None:
        super().__init__(
            name="risk_check",
            description="Check target weights and optional equity drawdown against risk limits.",
        )

    def run(self, **kwargs: Any) -> ToolResult:
        config_path = Path(kwargs.get("config_path", "configs/risk.yaml")).expanduser()
        targets_path = Path(kwargs["targets_path"]).expanduser()
        equity_path_value = kwargs.get("equity_path")
        clip = bool(kwargs.get("clip", True))

        limits = RiskLimits.from_yaml(config_path)
        targets = ParquetStorage().load(targets_path)
        position_decision = check_position_limits(targets, limits, clip=clip)
        decisions = {"position": position_decision}

        if equity_path_value:
            equity_path = Path(equity_path_value).expanduser()
            equity_curve = _load_frame(equity_path)
            decisions["drawdown"] = check_drawdown(equity_curve, limits)

        final_decision = _combine_decisions(decisions)
        metadata = {
            "status": final_decision.status,
            "approved": final_decision.approved,
            "violations": final_decision.violations,
            "limits": limits.as_dict(),
            "targets_path": str(targets_path),
            "decisions": {name: decision.as_dict() for name, decision in decisions.items()},
        }
        if final_decision.adjusted_targets is not None:
            metadata["adjusted_targets"] = final_decision.adjusted_targets.to_dict(
                orient="records"
            )
        content = (
            f"Risk check {final_decision.status}. "
            f"approved={final_decision.approved}. "
            f"violations={final_decision.violations or []}."
        )
        return ToolResult(content=content, metadata=metadata)


def _load_frame(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return ParquetStorage().load(path)


def _combine_decisions(decisions: dict[str, RiskDecision]) -> RiskDecision:
    rejected = [decision for decision in decisions.values() if not decision.approved]
    violations = [
        violation
        for decision in decisions.values()
        for violation in decision.violations
    ]
    position = decisions["position"]
    if rejected:
        return RiskDecision(
            status="rejected",
            reason="one or more risk checks rejected the request",
            approved=False,
            violations=violations,
            adjusted_targets=position.adjusted_targets,
            audit={"checks": list(decisions)},
        )
    if any(decision.status == "clipped" for decision in decisions.values()):
        return RiskDecision(
            status="clipped",
            reason="one or more risk checks adjusted the request",
            approved=True,
            violations=violations,
            adjusted_targets=position.adjusted_targets,
            audit={"checks": list(decisions)},
        )
    return RiskDecision(
        status="approved",
        reason="all risk checks passed",
        approved=True,
        adjusted_targets=position.adjusted_targets,
        audit={"checks": list(decisions)},
    )
