"""Rule-based supervisor agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quant_mas.core import AgentEvent, AgentFinishEvent, ToolCallEvent
from quant_mas.tools import ToolRegistry


@dataclass(frozen=True)
class RouteRule:
    """Keyword rule for routing a task to a tool."""

    tool_name: str
    keywords: tuple[str, ...]


DEFAULT_ROUTE_RULES = (
    RouteRule("ml_backtest", ("ml backtest", "ml_backtest", "机器学习回测", "ml回测", "ML回测")),
    RouteRule("risk_check", ("risk", "风控", "风险", "风险检查")),
    RouteRule("pipeline", ("pipeline", "全流程", "端到端", "end to end")),
    RouteRule("backtest", ("backtest", "回测", "策略测试")),
    RouteRule("train_model", ("train", "model", "训练", "模型")),
    RouteRule("report", ("report", "summary", "报告", "摘要")),
    RouteRule("data_summary", ("data", "dataset", "数据", "概览")),
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
            result = self.tool_registry.get(tool_name).run(
                **self._kwargs_for_tool(tool_name, tool_kwargs)
            )
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
        available = ", ".join(rule.tool_name for rule in self.route_rules)
        raise ValueError(
            f"No tool route matched task: {task}. Available task types: {available}"
        )

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
        if tool_name == "risk_check":
            if "config_path" not in common and "risk_config_path" in common:
                common["config_path"] = common["risk_config_path"]
        if tool_name == "ml_backtest":
            if "config_path" not in common and "tool_config" in common:
                common["config_path"] = common["tool_config"]
            if "features_path" not in common and "input_path" in common:
                common["features_path"] = common["input_path"]
        if tool_name == "pipeline":
            if "backtest_config" not in common and "tool_config" in common:
                common["backtest_config"] = common["tool_config"]
        return common
