"""Sequential fallback runner for ResearchWorkflow."""

from __future__ import annotations

from quant_mas.orchestration.langgraph_state import QuantWorkflowState
from quant_mas.orchestration.node_context import NodeContext
from quant_mas.orchestration.nodes import NODE_FUNCTIONS
from quant_mas.orchestration.workflow_events import WorkflowFinishEvent
from quant_mas.tools import ToolRegistry


NODE_ORDER = ["data_check", "feature_build", "train_model", "ml_backtest", "risk_check", "report"]


def run_sequential_workflow(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    stop_on_error: bool = True,
    context: NodeContext | None = None,
) -> QuantWorkflowState:
    """Run ResearchWorkflow nodes in fixed order."""
    context = context or NodeContext.from_state(state)
    for node_name in NODE_ORDER:
        if state["errors"] and stop_on_error:
            break
        node = NODE_FUNCTIONS[node_name]
        node(state, tools=tools, context=context)
    state["current_node"] = None
    state["events"].append(
        WorkflowFinishEvent(
            event_type="workflow_finish",
            message="Research workflow finished",
            metadata={
                "completed_nodes": list(state["completed_nodes"]),
                "errors": list(state["errors"]),
            },
        ).to_dict()
    )
    return state
