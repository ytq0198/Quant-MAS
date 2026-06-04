"""Internal agent communication primitives for orchestration dry-runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class AgentMessage:
    """Base internal message exchanged by orchestration components."""

    sender: str
    message_type: str
    created_at: str = field(default_factory=_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PlanMessage(AgentMessage):
    """Message describing a planned pipeline."""

    pipeline_id: str = ""
    nodes: list[str] = field(default_factory=list)
    message_type: str = "plan"


@dataclass(frozen=True)
class NodeResultMessage(AgentMessage):
    """Message emitted when a scheduler node finishes."""

    pipeline_id: str = ""
    node_id: str = ""
    status: str = "success"
    artifacts: dict[str, str] = field(default_factory=dict)
    message_type: str = "node_result"


@dataclass(frozen=True)
class AuditMessage(AgentMessage):
    """Message pointing to an audit event or audit log."""

    pipeline_id: str = ""
    node_id: str = ""
    audit_path: str = ""
    message_type: str = "audit"


class InMemoryMessageBus:
    """Small in-memory pub/sub bus used by tests and dry-run schedulers."""

    def __init__(self) -> None:
        self._messages: dict[str, list[AgentMessage]] = {}

    def publish(self, topic: str, message: AgentMessage) -> None:
        self._messages.setdefault(topic, []).append(message)

    def subscribe(self, topic: str) -> list[AgentMessage]:
        return list(self._messages.get(topic, []))

    def topics(self) -> list[str]:
        return sorted(self._messages)
