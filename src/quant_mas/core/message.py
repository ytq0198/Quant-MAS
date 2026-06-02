"""Chat message primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal


MessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class Message:
    """Internal chat message with OpenAI-compatible conversion."""

    role: MessageRole
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            payload["name"] = self.name
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Message":
        return cls(
            role=payload["role"],
            content=payload.get("content", ""),
            name=payload.get("name"),
            metadata=payload.get("metadata", {}),
        )

