"""Optional LangGraph runner for ResearchWorkflow."""

from __future__ import annotations

from functools import partial

from quant_mas.orchestration.langgraph_state import QuantWorkflowState
from quant_mas.orchestration.node_context import NodeContext
from quant_mas.orchestration.nodes import NODE_FUNCTIONS
from quant_mas.orchestration.sequential_workflow import NODE_ORDER
from quant_mas.tools import ToolRegistry

try:
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    END = START = StateGraph = None
    LANGGRAPH_AVAILABLE = False


def _node_edges() -> list[tuple[str, str]]:
    """Return pairwise workflow edges between ordered nodes."""
    return list(zip(NODE_ORDER[:-1], NODE_ORDER[1:], strict=True))


def build_langgraph_workflow(tools: ToolRegistry):
    """Build a compiled LangGraph workflow when langgraph is installed."""
    if not LANGGRAPH_AVAILABLE:
        return None
    graph = StateGraph(dict)
    context_holder: dict[str, NodeContext | None] = {"context": None}

    def wrapped(node_name: str, state: QuantWorkflowState) -> QuantWorkflowState:
        context = context_holder["context"] or NodeContext.from_state(state)
        context_holder["context"] = context
        return NODE_FUNCTIONS[node_name](state, tools=tools, context=context)

    for node_name in NODE_ORDER:
        graph.add_node(node_name, partial(wrapped, node_name))
    graph.add_edge(START, NODE_ORDER[0])
    for left, right in _node_edges():
        graph.add_edge(left, right)
    graph.add_edge(NODE_ORDER[-1], END)
    return graph.compile()


def run_langgraph_workflow(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
) -> QuantWorkflowState:
    """Run ResearchWorkflow with LangGraph."""
    graph = build_langgraph_workflow(tools)
    if graph is None:
        raise ImportError(
            "langgraph is not installed. Use backend=sequential or install "
            '`python -m pip install -e ".[orchestration]"`.'
        )
    return graph.invoke(state)
