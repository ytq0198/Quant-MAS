"""Exposure and position-limit checks."""

from __future__ import annotations

import pandas as pd

from quant_mas.risk.decision import (
    RiskDecision,
    approved_decision,
    clipped_decision,
    rejected_decision,
)
from quant_mas.risk.limits import RiskLimits


def calculate_total_exposure(targets: pd.DataFrame) -> float:
    """Calculate gross exposure as sum(abs(target_weight))."""
    frame = _normalize_targets(targets)
    return round(float(frame["target_weight"].abs().sum()), 12)


def check_position_limits(
    targets: pd.DataFrame,
    limits: RiskLimits,
    *,
    clip: bool = True,
) -> RiskDecision:
    """Check and optionally clip target weights against risk limits."""
    original = _normalize_targets(targets)
    adjusted = original.copy()
    violations: list[str] = []

    if not limits.allow_short and (adjusted["target_weight"] < 0).any():
        violations.append("short_position_not_allowed")
        if clip:
            adjusted["target_weight"] = adjusted["target_weight"].clip(lower=0.0)

    too_large = adjusted["target_weight"].abs() > limits.max_position_weight
    if too_large.any():
        violations.append("max_position_weight_exceeded")
        if clip:
            adjusted["target_weight"] = adjusted["target_weight"].clip(
                lower=-limits.max_position_weight if limits.allow_short else 0.0,
                upper=limits.max_position_weight,
            )

    exposure_after_position = calculate_total_exposure(adjusted)
    if exposure_after_position > limits.max_total_exposure:
        violations.append("max_total_exposure_exceeded")
        if clip:
            scale = limits.max_total_exposure / exposure_after_position
            adjusted["target_weight"] = adjusted["target_weight"] * scale

    audit = {
        "original_total_exposure": calculate_total_exposure(original),
        "adjusted_total_exposure": calculate_total_exposure(adjusted),
        "max_position_weight": limits.max_position_weight,
        "max_total_exposure": limits.max_total_exposure,
        "allow_short": limits.allow_short,
        "require_human_approval": limits.require_human_approval,
    }

    if not violations:
        return approved_decision(
            reason="position limits passed",
            adjusted_targets=adjusted,
            audit=audit,
        )
    if not clip:
        return rejected_decision(
            reason="position limits failed",
            violations=violations,
            adjusted_targets=original,
            audit=audit,
        )
    return clipped_decision(
        reason="position targets clipped by risk limits",
        violations=violations,
        adjusted_targets=adjusted,
        audit=audit,
    )


def _normalize_targets(targets: pd.DataFrame) -> pd.DataFrame:
    required = {"symbol", "target_weight"}
    missing = required.difference(targets.columns)
    if missing:
        raise ValueError(f"Risk targets missing columns: {sorted(missing)}")
    frame = targets.loc[:, ["symbol", "target_weight"]].copy()
    frame["symbol"] = frame["symbol"].astype(str).str.strip().str.upper()
    frame["target_weight"] = pd.to_numeric(frame["target_weight"], errors="raise")
    if frame["symbol"].eq("").any():
        raise ValueError("Risk targets contain empty symbols")
    if frame["target_weight"].isna().any():
        raise ValueError("Risk targets contain missing target_weight")
    if frame.duplicated("symbol").any():
        raise ValueError("Risk targets contain duplicate symbols")
    return frame.sort_values("symbol").reset_index(drop=True)
