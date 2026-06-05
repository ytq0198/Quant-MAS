from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.agents import list_agents, run_agent_task

router = APIRouter(prefix="/api/agents", tags=["agents"])


class AgentRunRequest(BaseModel):
    agent: str
    task: str


@router.get("")
def read_agents() -> list[dict[str, Any]]:
    """Return registered mock-safe agents.

    返回已注册的 mock-safe 智能体。
    """
    return list_agents()


@router.post("/run")
def run_agent(request: AgentRunRequest) -> dict[str, Any]:
    """Run a controlled mock-safe agent task.

    运行受控的 mock-safe 智能体任务。
    """
    return run_agent_task(request.agent, request.task)
