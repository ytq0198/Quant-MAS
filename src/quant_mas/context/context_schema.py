"""Structured context schemas for research agents."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MarketContextSnapshot:
    """Small market data summary without embedding full data frames."""

    symbols: list[str] = field(default_factory=list)
    date_range: dict[str, str | None] = field(default_factory=dict)
    row_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarketContextSnapshot":
        return cls(
            symbols=list(payload.get("symbols", [])),
            date_range=dict(payload.get("date_range", {})),
            row_counts=dict(payload.get("row_counts", {})),
        )


@dataclass(frozen=True)
class ExperimentContextSnapshot:
    """Experiment facts produced by Quant Engine and Memory."""

    experiment_id: str
    name: str
    family: str = "unknown"
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    status: str = "unknown"
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExperimentContextSnapshot":
        return cls(
            experiment_id=str(payload.get("experiment_id", "")),
            name=str(payload.get("name", "")),
            family=str(payload.get("family", "unknown")),
            metrics=dict(payload.get("metrics", {})),
            artifacts={key: str(value) for key, value in payload.get("artifacts", {}).items()},
            status=str(payload.get("status", "unknown")),
            created_at=payload.get("created_at"),
        )


@dataclass(frozen=True)
class RiskContextSnapshot:
    """Auditable risk status from workflow or risk tools."""

    approved: bool | None = None
    status: str = "unknown"
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RiskContextSnapshot":
        return cls(
            approved=payload.get("approved"),
            status=str(payload.get("status", "unknown")),
            violations=[str(item) for item in payload.get("violations", [])],
        )


@dataclass(frozen=True)
class RagContextChunk:
    """One compressed retrieval snippet."""

    doc_id: str
    path: str
    title: str
    snippet: str
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RagContextChunk":
        return cls(
            doc_id=str(payload.get("doc_id", "")),
            path=str(payload.get("path", "")),
            title=str(payload.get("title", "")),
            snippet=str(payload.get("snippet", "")),
            score=float(payload.get("score", 0.0)),
        )


@dataclass(frozen=True)
class AgentContextBundle:
    """Complete research context bundle for optional LLM interpretation."""

    task: str
    market: MarketContextSnapshot = field(default_factory=MarketContextSnapshot)
    experiments: list[ExperimentContextSnapshot] = field(default_factory=list)
    baseline: ExperimentContextSnapshot | None = None
    risk: RiskContextSnapshot | None = None
    rag_chunks: list[RagContextChunk] = field(default_factory=list)
    workflow: dict[str, Any] = field(default_factory=dict)
    baseline_ref: str = "EXP-20260602-008"
    built_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "market": self.market.to_dict(),
            "experiments": [item.to_dict() for item in self.experiments],
            "baseline": self.baseline.to_dict() if self.baseline else None,
            "risk": self.risk.to_dict() if self.risk else None,
            "rag_chunks": [item.to_dict() for item in self.rag_chunks],
            "workflow": _json_safe(self.workflow),
            "baseline_ref": self.baseline_ref,
            "built_at": self.built_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentContextBundle":
        baseline_payload = payload.get("baseline")
        risk_payload = payload.get("risk")
        return cls(
            task=str(payload.get("task", "")),
            market=MarketContextSnapshot.from_dict(payload.get("market", {})),
            experiments=[
                ExperimentContextSnapshot.from_dict(item)
                for item in payload.get("experiments", [])
            ],
            baseline=(
                ExperimentContextSnapshot.from_dict(baseline_payload)
                if baseline_payload
                else None
            ),
            risk=RiskContextSnapshot.from_dict(risk_payload) if risk_payload else None,
            rag_chunks=[
                RagContextChunk.from_dict(item)
                for item in payload.get("rag_chunks", [])
            ],
            workflow=dict(payload.get("workflow", {})),
            baseline_ref=str(payload.get("baseline_ref", "EXP-20260602-008")),
            built_at=str(payload.get("built_at", datetime.now(UTC).isoformat())),
        )


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
