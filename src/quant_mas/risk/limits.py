"""Risk limit configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RiskLimits:
    """Auditable first-pass risk limits for target weights."""

    max_position_weight: float = 0.2
    max_total_exposure: float = 1.0
    max_drawdown: float = 0.2
    allow_short: bool = False
    require_human_approval: bool = True

    def __post_init__(self) -> None:
        if self.max_position_weight <= 0:
            raise ValueError("max_position_weight must be positive")
        if self.max_total_exposure <= 0:
            raise ValueError("max_total_exposure must be positive")
        if not 0 <= self.max_drawdown <= 1:
            raise ValueError("max_drawdown must be between 0 and 1")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskLimits":
        """Create limits from either root-level or `risk` YAML data."""
        values = data.get("risk", data)
        return cls(
            max_position_weight=float(values.get("max_position_weight", 0.2)),
            max_total_exposure=float(values.get("max_total_exposure", 1.0)),
            max_drawdown=float(values.get("max_drawdown", 0.2)),
            allow_short=bool(values.get("allow_short", False)),
            require_human_approval=bool(values.get("require_human_approval", True)),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RiskLimits":
        with Path(path).expanduser().open("r", encoding="utf-8") as file:
            return cls.from_dict(yaml.safe_load(file) or {})

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_position_weight": self.max_position_weight,
            "max_total_exposure": self.max_total_exposure,
            "max_drawdown": self.max_drawdown,
            "allow_short": self.allow_short,
            "require_human_approval": self.require_human_approval,
        }
