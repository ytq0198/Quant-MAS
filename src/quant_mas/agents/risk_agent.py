"""Risk wrapper for competitive strategy proposals."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd

from quant_mas.agents.strategy_agent import AgentProposal
from quant_mas.risk import RiskLimits, check_position_limits


class RiskAgent:
    """Apply deterministic risk limits before a proposal enters simulation."""

    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits(max_position_weight=1.0, require_human_approval=False)

    def apply(
        self,
        proposal: AgentProposal,
        *,
        current_weight: float,
        equity: float,
        symbol: str = "SYN",
    ) -> AgentProposal:
        """Clip target_weight via shared position-limit logic."""
        targets = pd.DataFrame(
            [{"symbol": symbol, "target_weight": proposal.target_weight}]
        )
        decision = check_position_limits(targets, self.limits, clip=True)
        adjusted_weight = float(decision.adjusted_targets["target_weight"].iloc[0])
        metadata = {
            **proposal.metadata,
            "risk_status": decision.status,
            "risk_approved": decision.approved,
            "risk_violations": list(decision.violations),
            "risk_audit": {
                **decision.audit,
                "current_weight": float(current_weight),
                "equity": float(equity),
            },
        }
        return replace(proposal, target_weight=adjusted_weight, metadata=metadata)
