from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.services.agents import list_agents, run_agent_task
from backend.security.api_keys import Principal
from backend.security.audit import append_audit_event
from backend.security.dependencies import require_role
from backend.security.roles import Role

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
def run_agent(
    request: AgentRunRequest,
    principal: Principal = Depends(require_role(Role.RESEARCHER)),
) -> dict[str, Any]:
    """Run a controlled mock-safe agent task.

    运行受控的 mock-safe 智能体任务。
    """
    result = run_agent_task(request.agent, request.task)
    audit_path = os.getenv("QUANT_MAS_AUDIT_WRITE_PATH")
    if audit_path:
        append_audit_event(
            audit_path,
            {
                "event_type": "agent.run",
                "agent": request.agent,
                "status": result.get("status"),
                "role": principal.role.value,
                "key_fingerprint": principal.key_fingerprint,
            },
        )
    return result
