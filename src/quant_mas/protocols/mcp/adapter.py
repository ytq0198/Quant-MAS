"""Adapters between Quant MAS tools and internal MCP-style calls."""

from __future__ import annotations

from collections.abc import Sequence

from quant_mas.protocols.mcp.policy import (
    PolicyDecision,
    ToolPolicy,
    default_tool_policy,
)
from quant_mas.protocols.mcp.types import (
    MCPParameterSpec,
    MCPToolCall,
    MCPToolResult,
    MCPToolSpec,
)
from quant_mas.tools import BaseTool, ToolRegistry


TOOL_PARAMETER_SPECS: dict[str, tuple[MCPParameterSpec, ...]] = {
    "data_summary": (
        MCPParameterSpec("path", "string", True, "Parquet data path."),
    ),
    "backtest": (
        MCPParameterSpec("input_path", "string", False, "OHLCV parquet path."),
        MCPParameterSpec("config_path", "string", False, "Backtest config path."),
        MCPParameterSpec("output_dir", "string", False, "Report output directory."),
    ),
    "train_model": (
        MCPParameterSpec("input_path", "string", False, "Feature parquet path."),
        MCPParameterSpec("config_path", "string", False, "Training config path."),
        MCPParameterSpec("output_dir", "string", False, "Model output directory."),
    ),
    "report": (
        MCPParameterSpec("memory_path", "string", False, "Experiment memory path."),
        MCPParameterSpec("output_path", "string", False, "Optional copied report path."),
    ),
    "ml_backtest": (
        MCPParameterSpec("features_path", "string", False, "Feature parquet path."),
        MCPParameterSpec("model_path", "string", False, "Model artifact path."),
        MCPParameterSpec("output_dir", "string", False, "Report output directory."),
    ),
    "pipeline": (
        MCPParameterSpec("symbols", "object", False, "Symbol list."),
        MCPParameterSpec("skip_download", "boolean", False, "Avoid real downloads."),
        MCPParameterSpec("skip_features", "boolean", False, "Use existing features."),
    ),
    "risk_check": (
        MCPParameterSpec("targets_path", "string", True, "Target weights parquet path."),
        MCPParameterSpec("config_path", "string", False, "Risk config path."),
    ),
}


def tool_to_mcp_spec(
    tool: BaseTool,
    *,
    parameter_specs: Sequence[MCPParameterSpec] | None = None,
) -> MCPToolSpec:
    """Convert a BaseTool into an MCP-style metadata spec."""
    parameters = tuple(parameter_specs or TOOL_PARAMETER_SPECS.get(tool.name, ()))
    return MCPToolSpec(
        name=tool.name,
        description=tool.description,
        parameters=parameters,
        safety_tags=("quant", "no_live_order"),
    )


def registry_to_mcp_specs(registry: ToolRegistry) -> list[MCPToolSpec]:
    """Export all tools in a registry as MCP-style specs."""
    return [tool_to_mcp_spec(tool) for tool in registry.list()]


def execute_mcp_tool_call(
    registry: ToolRegistry,
    call: MCPToolCall,
    *,
    policy: ToolPolicy | None = None,
    confirmed: bool = False,
) -> MCPToolResult:
    """Execute a policy-guarded MCP-style call through ToolRegistry."""
    active_policy = policy or default_tool_policy()
    evaluation = active_policy.evaluate(call)
    if evaluation.decision == PolicyDecision.DENY:
        return MCPToolResult(
            status="denied",
            content=evaluation.reason,
            metadata={"policy_decision": evaluation.decision.value},
        )
    if evaluation.decision == PolicyDecision.REQUIRE_CONFIRMATION and not confirmed:
        return MCPToolResult(
            status="denied",
            content=f"Confirmation required: {evaluation.reason}",
            metadata={"policy_decision": evaluation.decision.value},
        )
    try:
        result = registry.get(call.tool_name).run(**call.arguments)
    except Exception as exc:
        return MCPToolResult(
            status="error",
            content=str(exc),
            metadata={"tool_name": call.tool_name},
        )
    return MCPToolResult(
        status="ok",
        content=result.content,
        metadata=result.metadata,
    )
