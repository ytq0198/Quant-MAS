"""Strategy-candidate schema for population-to-Quant-Engine validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class StrategyCandidate:
    """Serializable candidate selected from a strategy population."""

    candidate_id: str
    source: str
    agent_id: str
    agent_type: str
    params: dict[str, Any] = field(default_factory=dict)
    selection_metrics: dict[str, Any] = field(default_factory=dict)
    validation_metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        assert_no_oos_metrics(self.selection_metrics)
        assert_no_oos_metrics(self.validation_metrics)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StrategyCandidate":
        return cls(
            candidate_id=str(payload["candidate_id"]),
            source=str(payload["source"]),
            agent_id=str(payload["agent_id"]),
            agent_type=str(payload["agent_type"]),
            params=dict(payload.get("params", {})),
            selection_metrics=dict(payload.get("selection_metrics", {})),
            validation_metrics=dict(payload.get("validation_metrics", {})),
            artifacts={str(key): str(value) for key, value in dict(payload.get("artifacts", {})).items()},
            notes=str(payload.get("notes", "")),
        )


def assert_no_oos_metrics(metrics: dict[str, Any]) -> None:
    """Reject OOS metrics in candidate selection/validation payloads."""
    for key, value in metrics.items():
        if str(key).lower() == "oos" or str(key).lower().startswith("oos."):
            raise ValueError("StrategyCandidate must not contain oos metrics in M11.6")
        if isinstance(value, dict):
            assert_no_oos_metrics(value)
