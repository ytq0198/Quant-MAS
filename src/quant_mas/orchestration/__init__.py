"""Experimental orchestration layer for reproducible research workflows.

ResearchWorkflow is a fixed six-step DAG for reproducible research pipelines.
It coexists with SupervisorAgent: SupervisorAgent routes one user task to one
tool, while ResearchWorkflow carries a QuantWorkflowState across nodes.
"""

from quant_mas.orchestration.langgraph_state import QuantWorkflowState, initial_state
from quant_mas.orchestration.langgraph_recipe_workflow import (
    build_langgraph_from_recipe,
    run_langgraph_recipe_workflow,
)
from quant_mas.orchestration.mcp_scheduler import MCPScheduler, SchedulerResult
from quant_mas.orchestration.pipeline_recipe import PipelineNode, PipelineRecipe, load_recipe_yaml
from quant_mas.orchestration.sequential_workflow import NODE_ORDER, run_sequential_workflow

__all__ = [
    "MCPScheduler",
    "NODE_ORDER",
    "PipelineNode",
    "PipelineRecipe",
    "QuantWorkflowState",
    "SchedulerResult",
    "build_langgraph_from_recipe",
    "initial_state",
    "load_recipe_yaml",
    "run_langgraph_recipe_workflow",
    "run_sequential_workflow",
]
