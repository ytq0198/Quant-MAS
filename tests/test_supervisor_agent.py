from __future__ import annotations

import pytest

from quant_mas.agents import SupervisorAgent
from quant_mas.core import AgentFinishEvent, ToolCallEvent
from quant_mas.tools import BaseTool, ToolRegistry, ToolResult


class StaticTool(BaseTool):
    def __init__(self, name: str) -> None:
        super().__init__(name=name, description=f"{name} test tool")
        self.calls = []

    def run(self, **kwargs) -> ToolResult:
        self.calls.append(kwargs)
        return ToolResult(
            content=f"{self.name} completed",
            metadata={"called_with": kwargs},
        )


def make_registry() -> tuple[ToolRegistry, dict[str, StaticTool]]:
    tools = {
        "data_summary": StaticTool("data_summary"),
        "backtest": StaticTool("backtest"),
        "train_model": StaticTool("train_model"),
        "ml_backtest": StaticTool("ml_backtest"),
        "pipeline": StaticTool("pipeline"),
        "risk_check": StaticTool("risk_check"),
        "report": StaticTool("report"),
    }
    return ToolRegistry(tools.values()), tools


def test_supervisor_routes_keywords_to_tools() -> None:
    registry, tools = make_registry()
    supervisor = SupervisorAgent(registry)

    result = supervisor.run("please run a backtest", input_path="data.parquet")

    assert result == "backtest completed"
    assert len(tools["backtest"].calls) == 1
    assert tools["backtest"].calls[0]["input_path"] == "data.parquet"
    assert isinstance(supervisor.events[1], ToolCallEvent)
    assert supervisor.events[1].tool_name == "backtest"
    assert isinstance(supervisor.events[-1], AgentFinishEvent)


def test_supervisor_maps_data_path_for_data_summary_tool() -> None:
    registry, tools = make_registry()
    supervisor = SupervisorAgent(registry)

    result = supervisor.run("summarize data", data_path="market.parquet")

    assert result == "data_summary completed"
    assert tools["data_summary"].calls[0]["path"] == "market.parquet"


@pytest.mark.parametrize(
    ("task", "tool_name"),
    [
        ("train the model", "train_model"),
        ("show latest report", "report"),
        ("数据概览", "data_summary"),
        ("运行回测", "backtest"),
        ("run ml backtest", "ml_backtest"),
        ("ML回测", "ml_backtest"),
        ("check risk limits", "risk_check"),
        ("风控检查", "risk_check"),
        ("run end to end pipeline", "pipeline"),
        ("端到端流程", "pipeline"),
    ],
)
def test_supervisor_route_table(task: str, tool_name: str) -> None:
    registry, _ = make_registry()
    supervisor = SupervisorAgent(registry)

    assert supervisor.route(task) == tool_name


def test_supervisor_rejects_unknown_task() -> None:
    registry, _ = make_registry()
    supervisor = SupervisorAgent(registry)

    with pytest.raises(ValueError, match="Available task types"):
        supervisor.run("do something mysterious")


def test_supervisor_requires_positive_max_steps() -> None:
    registry, _ = make_registry()

    with pytest.raises(ValueError, match="max_steps"):
        SupervisorAgent(registry, max_steps=0)


def test_supervisor_maps_risk_kwargs() -> None:
    registry, tools = make_registry()
    supervisor = SupervisorAgent(registry)

    supervisor.run(
        "风控检查",
        targets_path="targets.parquet",
        risk_config_path="risk.yaml",
    )

    assert tools["risk_check"].calls[0]["targets_path"] == "targets.parquet"
    assert tools["risk_check"].calls[0]["config_path"] == "risk.yaml"
    assert supervisor.events[1].tool_name == "risk_check"


def test_supervisor_maps_ml_backtest_kwargs() -> None:
    registry, tools = make_registry()
    supervisor = SupervisorAgent(registry)

    supervisor.run(
        "run ml backtest",
        tool_config="backtest_ml.yaml",
        input_path="features.parquet",
    )

    assert tools["ml_backtest"].calls[0]["config_path"] == "backtest_ml.yaml"
    assert tools["ml_backtest"].calls[0]["features_path"] == "features.parquet"
    assert supervisor.events[1].tool_name == "ml_backtest"


def test_supervisor_maps_pipeline_kwargs() -> None:
    registry, tools = make_registry()
    supervisor = SupervisorAgent(registry)

    supervisor.run("run end to end pipeline", tool_config="backtest.yaml")

    assert tools["pipeline"].calls[0]["backtest_config"] == "backtest.yaml"
    assert supervisor.events[1].tool_name == "pipeline"
