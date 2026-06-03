"""Safety policy for internal MCP-style tool calls."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from quant_mas.protocols.mcp.types import MCPToolCall


SAFE_QUANT_TOOLS = {
    "data_summary",
    "backtest",
    "train_model",
    "report",
    "ml_backtest",
    "pipeline",
    "risk_check",
}


class PolicyDecision(str, Enum):
    """Policy decision values."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"


@dataclass(frozen=True)
class PolicyEvaluation:
    """Policy evaluation result."""

    decision: PolicyDecision
    reason: str = ""


class ToolPolicy:
    """Deny-by-default safety gateway for tool calls."""

    def __init__(
        self,
        *,
        allowed_tools: set[str] | None = None,
        deny_tool_patterns: tuple[str, ...] = (
            "shell",
            "exec",
            "broker",
            "order",
            "place_order",
            "live_trade",
        ),
        deny_argument_patterns: tuple[str, ...] = (
            "api_key",
            "secret",
            "password",
            "token",
        ),
        require_confirmation_tools: set[str] | None = None,
    ) -> None:
        self.allowed_tools = allowed_tools or set(SAFE_QUANT_TOOLS)
        self.deny_tool_patterns = tuple(item.lower() for item in deny_tool_patterns)
        self.deny_argument_patterns = tuple(item.lower() for item in deny_argument_patterns)
        self.require_confirmation_tools = require_confirmation_tools or set()

    def evaluate(self, call: MCPToolCall) -> PolicyEvaluation:
        tool_name = call.tool_name.lower()
        if any(pattern in tool_name for pattern in self.deny_tool_patterns):
            return PolicyEvaluation(
                PolicyDecision.DENY,
                f"tool name is denied by pattern: {call.tool_name}",
            )
        denied_argument = _find_denied_argument(call.arguments, self.deny_argument_patterns)
        if denied_argument:
            return PolicyEvaluation(
                PolicyDecision.DENY,
                f"argument is denied by pattern: {denied_argument}",
            )
        denied_path = _find_denied_path(call.arguments)
        if denied_path:
            return PolicyEvaluation(
                PolicyDecision.DENY,
                f"path points to a denied secret-like target: {denied_path}",
            )
        if tool_name not in self.allowed_tools:
            return PolicyEvaluation(
                PolicyDecision.DENY,
                f"tool is not in allowlist: {call.tool_name}",
            )
        if tool_name in self.require_confirmation_tools:
            return PolicyEvaluation(
                PolicyDecision.REQUIRE_CONFIRMATION,
                f"tool requires confirmation: {call.tool_name}",
            )
        return PolicyEvaluation(PolicyDecision.ALLOW, "tool call allowed")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ToolPolicy":
        payload = yaml.safe_load(Path(path).expanduser().read_text(encoding="utf-8")) or {}
        config = payload.get("protocols", {}).get("mcp", payload.get("mcp", payload))
        return cls(
            deny_tool_patterns=tuple(config.get("deny_tool_patterns", cls().deny_tool_patterns)),
            deny_argument_patterns=tuple(
                config.get("deny_argument_patterns", cls().deny_argument_patterns)
            ),
            require_confirmation_tools=set(config.get("require_confirmation_tools", [])),
        )


def evaluate_tool_call(call: MCPToolCall, policy: ToolPolicy | None = None) -> PolicyEvaluation:
    """Evaluate a tool call with the provided or default policy."""
    return (policy or default_tool_policy()).evaluate(call)


def default_tool_policy() -> ToolPolicy:
    """Return the default deny-by-default policy."""
    return ToolPolicy()


def _find_denied_argument(arguments: dict[str, Any], patterns: tuple[str, ...]) -> str | None:
    for key, value in arguments.items():
        lowered = str(key).lower()
        if any(pattern in lowered for pattern in patterns):
            return str(key)
        if isinstance(value, dict):
            nested = _find_denied_argument(value, patterns)
            if nested:
                return f"{key}.{nested}"
    return None


def _find_denied_path(arguments: dict[str, Any]) -> str | None:
    for key, value in arguments.items():
        lowered_key = str(key).lower()
        if isinstance(value, dict):
            nested = _find_denied_path(value)
            if nested:
                return nested
        if not isinstance(value, str):
            continue
        lowered_value = value.lower()
        if lowered_key.endswith("_path") or lowered_key.endswith("path"):
            if ".env" in lowered_value or "secret" in lowered_value or "secrets" in lowered_value:
                return value
    return None
