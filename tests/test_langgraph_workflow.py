from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from quant_mas.agents import SupervisorAgent
from quant_mas.orchestration import NODE_ORDER, initial_state, run_sequential_workflow
from quant_mas.orchestration.langgraph_workflow import build_langgraph_workflow
from quant_mas.orchestration.node_context import NodeContext
from quant_mas.orchestration.registry import WorkflowMockModel, create_default_tool_registry
from quant_mas.tools import (
    BaseTool,
    DataSummaryTool,
    ReportTool,
    RiskTool,
    ToolRegistry,
    ToolResult,
    TrainModelTool,
)


class FailingTool(BaseTool):
    def __init__(self, name: str) -> None:
        super().__init__(name=name, description=f"{name} fails")

    def run(self, **kwargs) -> ToolResult:
        raise RuntimeError(f"{self.name} boom")


def make_storage_config(tmp_path: Path) -> Path:
    path = tmp_path / "storage.yaml"
    path.write_text(
        "\n".join(
            [
                "project_root: .",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    return path


def make_state(tmp_path: Path):
    return initial_state(
        task="test workflow",
        dry_run=True,
        storage_config=str(make_storage_config(tmp_path)),
        report_output_dir=str(tmp_path / "workflow" / "reports"),
    )


def make_context(tmp_path: Path, state=None) -> NodeContext:
    state = state or make_state(tmp_path)
    return NodeContext.from_state(state)


def test_initial_state_defaults() -> None:
    state = initial_state()

    assert state["dry_run"] is True
    assert state["task"] == ""
    assert state["completed_nodes"] == []
    assert state["events"] == []
    assert state["raw_path"] is None


def test_sequential_workflow_dry_run_completes_six_nodes(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    result = run_sequential_workflow(
        state,
        tools=create_default_tool_registry(dry_run=True),
        context=make_context(tmp_path, state),
    )

    assert result["errors"] == []
    assert result["completed_nodes"] == NODE_ORDER
    assert len(result["completed_nodes"]) == 6
    assert "summary" in result["artifacts"]


def test_node_order_matches_completion_events(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    result = run_sequential_workflow(
        state,
        tools=create_default_tool_registry(dry_run=True),
        context=make_context(tmp_path, state),
    )

    completed = [
        event["node"]
        for event in result["events"]
        if event["event_type"] == "node_complete"
    ]
    assert completed == NODE_ORDER


def test_stop_on_error_short_circuits_later_nodes(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    tools = ToolRegistry(
        [
            DataSummaryTool(),
            TrainModelTool(model_factory=WorkflowMockModel),
            FailingTool("ml_backtest"),
            RiskTool(),
            ReportTool(),
        ]
    )

    result = run_sequential_workflow(
        state,
        tools=tools,
        stop_on_error=True,
        context=make_context(tmp_path, state),
    )

    assert result["errors"]
    assert "ml_backtest" not in result["completed_nodes"]
    assert "risk_check" not in result["completed_nodes"]
    assert result["completed_nodes"] == ["data_check", "feature_build", "train_model"]


def test_no_stop_on_error_continues_later_nodes(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    tools = ToolRegistry(
        [
            DataSummaryTool(),
            TrainModelTool(model_factory=WorkflowMockModel),
            FailingTool("ml_backtest"),
            RiskTool(),
            ReportTool(),
        ]
    )

    result = run_sequential_workflow(
        state,
        tools=tools,
        stop_on_error=False,
        context=make_context(tmp_path, state),
    )

    assert result["errors"]
    assert "risk_check" in result["completed_nodes"]
    assert "report" in result["completed_nodes"]


def test_dry_run_does_not_call_yfinance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_fetch(*args, **kwargs):
        raise AssertionError("YFinanceFetcher should not be called in dry-run")

    monkeypatch.setattr("quant_mas.data.fetchers.YFinanceFetcher.fetch", fail_fetch)
    state = make_state(tmp_path)

    result = run_sequential_workflow(
        state,
        tools=create_default_tool_registry(dry_run=True),
        context=make_context(tmp_path, state),
    )

    assert result["errors"] == []


def test_events_include_tool_calls(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    result = run_sequential_workflow(
        state,
        tools=create_default_tool_registry(dry_run=True),
        context=make_context(tmp_path, state),
    )

    tool_events = [event for event in result["events"] if event["event_type"] == "tool_call"]
    assert {event["metadata"]["tool_name"] for event in tool_events} >= {
        "data_summary",
        "train_model",
        "ml_backtest",
        "risk_check",
        "report",
    }


def test_run_langgraph_workflow_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_langgraph_workflow.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--backend" in result.stdout


def test_run_langgraph_workflow_cli_sequential_dry_run(tmp_path: Path) -> None:
    output_json = tmp_path / "state.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_langgraph_workflow.py",
            "--dry-run",
            "--backend",
            "sequential",
            "--storage-config",
            str(make_storage_config(tmp_path)),
            "--report-output-dir",
            str(tmp_path / "workflow" / "reports"),
            "--output-json",
            str(output_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_json.exists()


def test_supervisor_agent_still_routes() -> None:
    supervisor = SupervisorAgent(ToolRegistry([DataSummaryTool()]))

    assert supervisor.route("数据概览") == "data_summary"


def test_langgraph_build_and_dry_run_when_available(tmp_path: Path) -> None:
    pytest.importorskip("langgraph")
    state = make_state(tmp_path)
    tools = create_default_tool_registry(dry_run=True)

    graph = build_langgraph_workflow(tools)

    assert graph is not None
