"""Internal MCP-style protocol adapters."""

from quant_mas.protocols.mcp.adapter import (
    execute_mcp_tool_call,
    registry_to_mcp_specs,
    tool_to_mcp_spec,
)
from quant_mas.protocols.mcp.policy import (
    PolicyDecision,
    PolicyEvaluation,
    ToolPolicy,
    default_tool_policy,
    evaluate_tool_call,
)
from quant_mas.protocols.mcp.types import (
    MCPParameterSpec,
    MCPToolCall,
    MCPToolResult,
    MCPToolSpec,
)

__all__ = [
    "MCPParameterSpec",
    "MCPToolCall",
    "MCPToolResult",
    "MCPToolSpec",
    "PolicyDecision",
    "PolicyEvaluation",
    "ToolPolicy",
    "default_tool_policy",
    "evaluate_tool_call",
    "execute_mcp_tool_call",
    "registry_to_mcp_specs",
    "tool_to_mcp_spec",
]
