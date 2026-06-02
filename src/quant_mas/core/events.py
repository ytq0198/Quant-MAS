"""Agent workflow events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal


AgentEventType = Literal["agent", "tool_call", "agent_finish"]


@dataclass(frozen=True)
class AgentEvent:
    """Base event emitted during an agent workflow."""

    event_type: AgentEventType
    message: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolCallEvent(AgentEvent):
    """Event emitted when a tool is selected and called."""

    tool_name: str = ""

    def __init__(
        self,
        *,
        tool_name: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        object.__setattr__(self, "event_type", "tool_call")
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "created_at", datetime.now(UTC).isoformat())
        object.__setattr__(self, "metadata", metadata or {})
        object.__setattr__(self, "tool_name", tool_name)


@dataclass(frozen=True)
class AgentFinishEvent(AgentEvent):
    """Event emitted when an agent workflow finishes."""

    result: str = ""

    def __init__(
        self,
        *,
        result: str,
        message: str = "Agent workflow finished",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        object.__setattr__(self, "event_type", "agent_finish")
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "created_at", datetime.now(UTC).isoformat())
        object.__setattr__(self, "metadata", metadata or {})
        object.__setattr__(self, "result", result)

