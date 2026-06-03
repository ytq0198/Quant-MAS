"""MCP-style internal tool protocol types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class MCPParameterSpec:
    """One MCP-style parameter description."""

    name: str
    type: str
    required: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MCPParameterSpec":
        return cls(
            name=str(payload["name"]),
            type=str(payload.get("type", "string")),
            required=bool(payload.get("required", False)),
            description=str(payload.get("description", "")),
        )


@dataclass(frozen=True)
class MCPToolSpec:
    """MCP-style tool metadata exported from BaseTool."""

    name: str
    description: str
    parameters: tuple[MCPParameterSpec, ...] = ()
    safety_tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [item.to_dict() for item in self.parameters],
            "safety_tags": list(self.safety_tags),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MCPToolSpec":
        return cls(
            name=str(payload["name"]),
            description=str(payload.get("description", "")),
            parameters=tuple(
                MCPParameterSpec.from_dict(item)
                for item in payload.get("parameters", [])
            ),
            safety_tags=tuple(str(item) for item in payload.get("safety_tags", [])),
        )


@dataclass(frozen=True)
class MCPToolCall:
    """MCP-style tool call payload."""

    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"tool_name": self.tool_name, "arguments": self.arguments}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MCPToolCall":
        return cls(
            tool_name=str(payload["tool_name"]),
            arguments=dict(payload.get("arguments", {})),
        )


@dataclass(frozen=True)
class MCPToolResult:
    """Standardized MCP-style tool result."""

    status: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MCPToolResult":
        return cls(
            status=str(payload["status"]),
            content=str(payload.get("content", "")),
            metadata=dict(payload.get("metadata", {})),
        )
