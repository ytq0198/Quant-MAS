"""Protocol adapters for Quant MAS."""

from quant_mas.protocols.a2a import (
    AgentCard,
    agent_card_to_dict,
    build_report_card,
    build_research_card,
    build_supervisor_card,
)
from quant_mas.protocols.mcp import (
    MCPParameterSpec,
    MCPToolCall,
    MCPToolResult,
    MCPToolSpec,
    PolicyDecision,
    PolicyEvaluation,
    ToolPolicy,
    default_tool_policy,
    evaluate_tool_call,
    execute_mcp_tool_call,
    registry_to_mcp_specs,
    tool_to_mcp_spec,
)

__all__ = [
    "AgentCard",
    "MCPParameterSpec",
    "MCPToolCall",
    "MCPToolResult",
    "MCPToolSpec",
    "PolicyDecision",
    "PolicyEvaluation",
    "ToolPolicy",
    "agent_card_to_dict",
    "build_report_card",
    "build_research_card",
    "build_supervisor_card",
    "default_tool_policy",
    "evaluate_tool_call",
    "execute_mcp_tool_call",
    "registry_to_mcp_specs",
    "tool_to_mcp_spec",
]
