"""Static A2A-style Agent Card metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


QUANT_TOOL_NAMES = (
    "data_summary",
    "backtest",
    "train_model",
    "report",
    "ml_backtest",
    "pipeline",
    "risk_check",
)


@dataclass(frozen=True)
class AgentCard:
    """Static capability card for an internal Quant MAS agent."""

    name: str
    description: str
    version: str
    capabilities: tuple[str, ...]
    tools: tuple[str, ...]
    safety_constraints: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentCard":
        return cls(
            name=str(payload["name"]),
            description=str(payload.get("description", "")),
            version=str(payload.get("version", "0.1.0")),
            capabilities=tuple(str(item) for item in payload.get("capabilities", [])),
            tools=tuple(str(item) for item in payload.get("tools", [])),
            safety_constraints=tuple(
                str(item) for item in payload.get("safety_constraints", [])
            ),
            metadata=dict(payload.get("metadata", {})),
        )


def build_supervisor_card(version: str = "0.1.0") -> AgentCard:
    """Build a static SupervisorAgent card."""
    return AgentCard(
        name="SupervisorAgent",
        description="Rule-routed supervisor for Quant MAS tools.",
        version=version,
        capabilities=(
            "keyword_route_task_to_tool",
            "emit_tool_call_events",
            "emit_agent_finish_events",
        ),
        tools=QUANT_TOOL_NAMES,
        safety_constraints=(
            "no_live_orders",
            "no_broker_access",
            "policy_guarded_tool_calls",
        ),
        metadata={"routing": "deterministic_rules"},
    )


def build_research_card(version: str = "0.1.0") -> AgentCard:
    """Build a static ResearchAgent card."""
    return AgentCard(
        name="ResearchAgent",
        description="Research interpretation agent using structured context and optional LLM.",
        version=version,
        capabilities=(
            "build_research_hypotheses",
            "summarize_evidence",
            "suggest_follow_up_experiments",
        ),
        tools=(),
        safety_constraints=(
            "no_live_orders",
            "metrics_not_overwritten_by_llm",
            "facts_separated_from_llm_inference",
        ),
        metadata={"default_llm": "mock"},
    )


def build_report_card(version: str = "0.1.0") -> AgentCard:
    """Build a static ReportAgent card."""
    return AgentCard(
        name="ReportAgent",
        description="Report narrative agent that preserves Quant Engine metrics.",
        version=version,
        capabilities=(
            "summarize_metrics",
            "generate_report_narrative",
            "preserve_factual_metrics",
        ),
        tools=(),
        safety_constraints=(
            "no_live_orders",
            "metrics_not_overwritten_by_llm",
            "no_investment_advice",
        ),
        metadata={"default_llm": "mock"},
    )


def agent_card_to_dict(card: AgentCard) -> dict[str, Any]:
    """Return a JSON-serializable Agent Card dictionary."""
    return card.to_dict()
