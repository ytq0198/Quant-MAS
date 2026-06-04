"""Optional LangGraph backend for M13 YAML pipeline recipes."""

from __future__ import annotations

from pathlib import Path

from quant_mas.orchestration.mcp_scheduler import MCPScheduler, SchedulerResult
from quant_mas.orchestration.pipeline_recipe import PipelineRecipe

try:
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    END = START = StateGraph = None
    LANGGRAPH_AVAILABLE = False


def build_langgraph_from_recipe(recipe: str | Path | PipelineRecipe):
    """Build a LangGraph DAG from a scheduler recipe when LangGraph is installed."""
    if not LANGGRAPH_AVAILABLE:
        return None

    scheduler = MCPScheduler()
    planned = scheduler.plan(recipe)

    graph = StateGraph(dict)

    def make_node(node_id: str, metric_family: str):
        def run_node(state: dict) -> dict:
            completed = list(state.get("completed_nodes", []))
            families = dict(state.get("metric_families", {}))
            completed.append(node_id)
            families[node_id] = metric_family
            return {
                **state,
                "completed_nodes": completed,
                "metric_families": families,
            }

        return run_node

    for node in planned:
        graph.add_node(node.node_id, make_node(node.node_id, node.metric_family))

    if planned:
        graph.add_edge(START, planned[0].node_id)
        for left, right in zip(planned[:-1], planned[1:], strict=True):
            graph.add_edge(left.node_id, right.node_id)
        graph.add_edge(planned[-1].node_id, END)

    return graph.compile()


def run_langgraph_recipe_workflow(
    recipe: str | Path | PipelineRecipe,
    *,
    output_dir: str | Path = "outputs/pipelines",
    dry_run: bool = True,
    run_id: str | None = None,
) -> SchedulerResult:
    """Run a recipe through the optional LangGraph backend.

    M13.2 remains dry-run only. When LangGraph is unavailable, this function
    falls back to the deterministic M13 scheduler backend so CLI smoke tests
    remain portable.
    """
    if not dry_run:
        raise ValueError("M13.2 LangGraph recipe workflow only supports dry_run=True")

    if LANGGRAPH_AVAILABLE:
        graph = build_langgraph_from_recipe(recipe)
        if graph is not None:
            graph.invoke({"completed_nodes": [], "metric_families": {}})

    return MCPScheduler().run(recipe, output_dir=output_dir, dry_run=True, run_id=run_id)
