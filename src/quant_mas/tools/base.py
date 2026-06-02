"""Tool abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    """Result returned by a tool."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Base interface for agent-callable tools."""

    name: str
    description: str

    def __init__(self, name: str, description: str) -> None:
        if not name:
            raise ValueError("tool name is required")
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        """Run tool and return a string-oriented result."""

