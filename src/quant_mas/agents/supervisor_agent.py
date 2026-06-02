"""Rule-based supervisor agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quant_mas.core import AgentEvent, AgentFinishEvent, ToolCallEvent
from quant_mas.tools import ToolRegistry, ToolResult


@dataclass(frozen=True)
class RouteRule:
    """Keyword rule for routing a task to a tool."""

    tool_name: str
    keywords: tuple[str, ...]


DEFAULT_ROUTE_RULES = (
    RouteRule("backtest", ("backtest", "回测", "策略测试")),
    RouteRule("train_model", ("train", "model", "训练", "模型")),
    RouteRule("report", ("report", "summary", "报告", "摘要")),
    RouteRule("data_summary", ("data", "dataset", "summary", "数据", "概览")),
)


class SupervisorAgent:
    """Small rule-based supervisor for internal quant workflows."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        max_steps: int = 4,
        route_rules: tuple[RouteRule, ...] = DEFAULT_ROUTE_RULES,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.route_rules = route_rules
        self.events: list[AgentEvent] = []

    def run(self, task: str, **tool_kwargs: Any) -> str:
        """Route one task to one deterministic tool."""
        self.events = [
            AgentEvent(
                event_type="agent",
                message=f"Received task: {task}",
            )
        ]
        for step in range(self.max_steps):
            if step > 0:
                break
            tool_name = self.route(task)
            self.events.append(
                ToolCallEvent(
                    tool_name=tool_name,
                    message=f"Calling tool: {tool_name}",
                    metadata={"step": step},
                )
            )
            result = self.tool_registry.get(tool_name).run(**self._kwargs_for_tool(tool_name, tool_kwargs))
            finish = AgentFinishEvent(
                result=result.content,
                metadata={
                    "tool_name": tool_name,
                    "tool_result_metadata": result.metadata,
                },
            )
            self.events.append(finish)
            return result.content
        raise RuntimeError(f"SupervisorAgent exceeded max_steps={self.max_steps}")

    def route(self, task: str) -> str:
        normalized = task.lower()
        for rule in self.route_rules:
            if any(keyword.lower() in normalized for keyword in rule.keywords):
                return rule.tool_name
        raise ValueError(f"No tool route matched task: {task}")

    @staticmethod
    def _kwargs_for_tool(tool_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        common = {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }
        if tool_name == "data_summary" and "path" not in common:
            for alias in ("data_path", "input_path"):
                if alias in common:
                    common["path"] = common[alias]
                    break
        return common

