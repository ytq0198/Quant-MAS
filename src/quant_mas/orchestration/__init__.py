"""Experimental orchestration layer for reproducible research workflows.

ResearchWorkflow is a fixed six-step DAG for reproducible research pipelines.
It coexists with SupervisorAgent: SupervisorAgent routes one user task to one
tool, while ResearchWorkflow carries a QuantWorkflowState across nodes.
"""

from quant_mas.orchestration.langgraph_state import QuantWorkflowState, initial_state
from quant_mas.orchestration.mcp_scheduler import MCPScheduler, SchedulerResult
from quant_mas.orchestration.sequential_workflow import NODE_ORDER, run_sequential_workflow

__all__ = [
    "MCPScheduler",
    "NODE_ORDER",
    "QuantWorkflowState",
    "SchedulerResult",
    "initial_state",
    "run_sequential_workflow",
]
