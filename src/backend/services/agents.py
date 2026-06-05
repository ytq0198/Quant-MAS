from __future__ import annotations

from typing import Any

_AGENTS: list[dict[str, Any]] = [
    {
        "name": "SupervisorAgent",
        "role": "Routes research tasks and enforces tool policy.",
        "中文": "路由研究任务并执行工具策略。",
        "live_trading_enabled": False,
        "tools": ["DataSummaryTool", "PipelineTool", "ReportTool"],
    },
    {
        "name": "ResearchAgent",
        "role": "Summarizes experiments, retrieves memory, and drafts research notes.",
        "中文": "总结实验、检索记忆并生成研究说明。",
        "live_trading_enabled": False,
        "tools": ["BacktestTool", "MLBacktestTool", "RiskTool", "ReportTool"],
    },
    {
        "name": "ReportAgent",
        "role": "Turns audited experiment outputs into readable reports.",
        "中文": "将经过审计的实验输出整理成可读报告。",
        "live_trading_enabled": False,
        "tools": ["ReportTool"],
    },
]


def list_agents() -> list[dict[str, Any]]:
    """Return mock-safe v4 agent registry metadata.

    返回 mock-safe 的 v4 智能体注册信息。
    """
    return _AGENTS


def run_agent_task(agent_name: str, task: str) -> dict[str, Any]:
    """Run a mock-safe agent task for Phase 2 UI/API integration.

    运行 Phase 2 UI/API 联调使用的 mock-safe 智能体任务。
    """
    known_agents = {agent["name"] for agent in _AGENTS}
    if agent_name not in known_agents:
        return {
            "agent": agent_name,
            "task": task,
            "status": "rejected",
            "live_trading_enabled": False,
            "message": "Unknown agent.",
            "中文": "未知智能体。",
            "events": [
                {
                    "type": "audit.agent.rejected",
                    "message": "Agent task rejected because the agent is not registered.",
                }
            ],
            "safety_notes": ["LLM agents do not place live orders."],
        }

    return {
        "agent": agent_name,
        "task": task,
        "status": "completed",
        "live_trading_enabled": False,
        "summary": (
            "Mock-safe Phase 2 response: the agent can summarize research context, "
            "route approved tools, and write audit-friendly notes."
        ),
        "中文": "Phase 2 mock-safe 响应：智能体可总结研究上下文、路由授权工具并生成便于审计的说明。",
        "events": [
            {
                "type": "audit.agent.task.accepted",
                "message": "Task accepted through the controlled backend API.",
            },
            {
                "type": "audit.agent.task.completed",
                "message": "Task completed without broker, order, shell, or secrets access.",
            },
        ],
        "safety_notes": [
            "LLM agents do not place live orders.",
            "All trading candidates require backtesting, risk checks, audit logs, and human confirmation.",
        ],
    }
