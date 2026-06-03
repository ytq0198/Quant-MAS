"""Agent layer package."""

from quant_mas.agents.report_agent import ReportAgent, ReportResult
from quant_mas.agents.research_agent import ResearchAgent, ResearchAgentOutput
from quant_mas.agents.risk_agent import RiskAgent
from quant_mas.agents.population_manager import AgentSpec, GenerationResult, PopulationManager
from quant_mas.agents.strategy_agent import (
    AgentEvaluation,
    AgentProposal,
    MeanReversionAgent,
    MomentumAgent,
    StrategyAgent,
    build_strategy_agent,
)
from quant_mas.agents.supervisor_agent import (
    DEFAULT_ROUTE_RULES,
    RouteRule,
    SupervisorAgent,
)

__all__ = [
    "DEFAULT_ROUTE_RULES",
    "AgentEvaluation",
    "AgentProposal",
    "AgentSpec",
    "GenerationResult",
    "MeanReversionAgent",
    "MomentumAgent",
    "PopulationManager",
    "ReportAgent",
    "ReportResult",
    "ResearchAgent",
    "ResearchAgentOutput",
    "RiskAgent",
    "RouteRule",
    "StrategyAgent",
    "SupervisorAgent",
    "build_strategy_agent",
]
