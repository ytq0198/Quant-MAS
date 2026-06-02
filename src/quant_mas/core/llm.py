"""LLM client boundary."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from quant_mas.core.message import Message


class LLMClient(ABC):
    """Abstract chat-completion client."""

    @abstractmethod
    def complete(self, messages: Sequence[Message], **kwargs) -> Message:
        """Return an assistant message."""


class MockLLMClient(LLMClient):
    """Deterministic LLM client for tests and offline development."""

    def __init__(self, responses: Sequence[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.calls: list[list[Message]] = []

    def complete(self, messages: Sequence[Message], **kwargs) -> Message:
        self.calls.append(list(messages))
        if self.responses:
            content = self.responses.pop(0)
        else:
            latest_user = next(
                (message.content for message in reversed(messages) if message.role == "user"),
                "",
            )
            content = f"Mock response: {latest_user}"
        return Message(role="assistant", content=content)

