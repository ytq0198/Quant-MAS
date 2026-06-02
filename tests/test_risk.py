from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant_mas.risk import (
    RiskLimits,
    calculate_total_exposure,
    check_drawdown,
    check_position_limits,
)
from quant_mas.tools import RiskTool, ToolRegistry


def make_targets() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": ["AAA", "BBB", "CCC"],
            "target_weight": [0.4, 0.3, 0.2],
        }
    )


def test_calculate_total_exposure() -> None:
    targets = pd.DataFrame(
        {
            "symbol": ["AAA", "BBB"],
            "target_weight": [0.25, -0.1],
        }
    )

    assert calculate_total_exposure(targets) == 0.35


def test_check_position_limits_clips_and_audits() -> None:
    limits = RiskLimits(max_position_weight=0.25, max_total_exposure=0.6)

    decision = check_position_limits(make_targets(), limits)

    assert decision.status == "clipped"
    assert decision.approved is True
    assert "max_position_weight_exceeded" in decision.violations
    assert decision.adjusted_targets is not None
    assert decision.adjusted_targets["target_weight"].max() <= 0.25
    assert decision.audit["adjusted_total_exposure"] <= 0.6


def test_check_position_limits_can_reject_without_clip() -> None:
    limits = RiskLimits(max_position_weight=0.25, max_total_exposure=0.6)

    decision = check_position_limits(make_targets(), limits, clip=False)

    assert decision.status == "rejected"
    assert decision.approved is False
    assert "max_position_weight_exceeded" in decision.violations


def test_check_drawdown_rejects_breach() -> None:
    equity = pd.DataFrame({"equity": [100.0, 120.0, 90.0, 95.0]})
    limits = RiskLimits(max_drawdown=0.2)

    decision = check_drawdown(equity, limits)

    assert decision.status == "rejected"
    assert "max_drawdown_exceeded" in decision.violations
    assert decision.audit["max_drawdown"] < -0.2


def test_risk_tool_registers_and_returns_auditable_result(tmp_path: Path) -> None:
    targets_path = tmp_path / "targets.parquet"
    config_path = tmp_path / "risk.yaml"
    make_targets().to_parquet(targets_path, index=False)
    config_path.write_text(
        "\n".join(
            [
                "risk:",
                "  max_position_weight: 0.25",
                "  max_total_exposure: 0.6",
                "  max_drawdown: 0.2",
                "  allow_short: false",
                "  require_human_approval: true",
            ]
        ),
        encoding="utf-8",
    )
    registry = ToolRegistry([RiskTool()])

    result = registry.get("risk_check").run(
        targets_path=targets_path,
        config_path=config_path,
    )

    assert result.metadata["status"] == "clipped"
    assert result.metadata["approved"] is True
    assert result.metadata["limits"]["require_human_approval"] is True
    assert "decisions" in result.metadata
    assert "adjusted_targets" in result.metadata
