"""Risk decision records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class RiskDecision:
    """Auditable result of a risk check."""

    status: str
    reason: str
    approved: bool
    violations: list[str] = field(default_factory=list)
    adjusted_targets: pd.DataFrame | None = None
    audit: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "status": self.status,
            "reason": self.reason,
            "approved": self.approved,
            "violations": list(self.violations),
            "audit": self.audit,
        }
        if self.adjusted_targets is not None:
            payload["adjusted_targets"] = self.adjusted_targets.to_dict(orient="records")
        return payload


def approved_decision(
    *,
    reason: str,
    adjusted_targets: pd.DataFrame | None = None,
    audit: dict[str, Any] | None = None,
) -> RiskDecision:
    return RiskDecision(
        status="approved",
        reason=reason,
        approved=True,
        adjusted_targets=adjusted_targets,
        audit=audit or {},
    )


def clipped_decision(
    *,
    reason: str,
    violations: list[str],
    adjusted_targets: pd.DataFrame,
    audit: dict[str, Any] | None = None,
) -> RiskDecision:
    return RiskDecision(
        status="clipped",
        reason=reason,
        approved=True,
        violations=violations,
        adjusted_targets=adjusted_targets,
        audit=audit or {},
    )


def rejected_decision(
    *,
    reason: str,
    violations: list[str],
    adjusted_targets: pd.DataFrame | None = None,
    audit: dict[str, Any] | None = None,
) -> RiskDecision:
    return RiskDecision(
        status="rejected",
        reason=reason,
        approved=False,
        violations=violations,
        adjusted_targets=adjusted_targets,
        audit=audit or {},
    )
