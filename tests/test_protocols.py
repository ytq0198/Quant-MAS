from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from quant_mas.protocols import (
    MCPParameterSpec,
    MCPToolCall,
    MCPToolResult,
    MCPToolSpec,
    PolicyDecision,
    ToolPolicy,
    agent_card_to_dict,
    build_supervisor_card,
    execute_mcp_tool_call,
    registry_to_mcp_specs,
    tool_to_mcp_spec,
)
from quant_mas.tools import BaseTool, ToolRegistry, ToolResult


class EchoTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="echo", description="echo for tests")
        self.calls: list[dict[str, Any]] = []

    def run(self, **kwargs: Any) -> ToolResult:
        self.calls.append(kwargs)
        return ToolResult(content="ok", metadata=kwargs)


class DataSummaryStub(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="data_summary", description="summarize data")
        self.called = False

    def run(self, **kwargs: Any) -> ToolResult:
        self.called = True
        return ToolResult(content="summary ok", metadata=kwargs)


class PipelineStub(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="pipeline", description="run pipeline")

    def run(self, **kwargs: Any) -> ToolResult:
        return ToolResult(content="pipeline ok", metadata=kwargs)


def test_mcp_types_round_trip() -> None:
    spec = MCPToolSpec(
        name="data_summary",
        description="summary",
        parameters=(MCPParameterSpec("path", "string", True, "data path"),),
        safety_tags=("quant", "no_live_order"),
    )
    call = MCPToolCall("data_summary", {"path": "x.parquet"})
    result = MCPToolResult("ok", "done", {"rows": 1})

    assert MCPToolSpec.from_dict(spec.to_dict()) == spec
    assert MCPToolCall.from_dict(call.to_dict()) == call
    assert MCPToolResult.from_dict(result.to_dict()) == result


def test_tool_to_mcp_spec_keeps_name_and_description() -> None:
    tool = EchoTool()

    spec = tool_to_mcp_spec(tool)

    assert spec.name == "echo"
    assert spec.description == "echo for tests"


def test_registry_to_mcp_specs_matches_tool_count() -> None:
    registry = ToolRegistry([EchoTool(), DataSummaryStub()])

    specs = registry_to_mcp_specs(registry)

    assert len(specs) == len(registry.list())


def test_policy_denies_shell_and_broker_tool_names() -> None:
    policy = ToolPolicy(allowed_tools={"data_summary"})

    assert policy.evaluate(MCPToolCall("shell_exec", {})).decision == PolicyDecision.DENY
    assert policy.evaluate(MCPToolCall("broker_order", {})).decision == PolicyDecision.DENY


def test_policy_denies_secret_arguments() -> None:
    policy = ToolPolicy(allowed_tools={"data_summary"})

    evaluation = policy.evaluate(MCPToolCall("data_summary", {"api_key": "secret"}))

    assert evaluation.decision == PolicyDecision.DENY


def test_policy_denies_env_paths() -> None:
    policy = ToolPolicy(allowed_tools={"risk_check"})

    evaluation = policy.evaluate(MCPToolCall("risk_check", {"targets_path": ".env"}))

    assert evaluation.decision == PolicyDecision.DENY


def test_policy_allows_data_summary_with_benign_kwargs() -> None:
    policy = ToolPolicy(allowed_tools={"data_summary"})

    evaluation = policy.evaluate(MCPToolCall("data_summary", {"path": "sample.parquet"}))

    assert evaluation.decision == PolicyDecision.ALLOW


def test_require_confirmation_without_confirmed_is_denied() -> None:
    registry = ToolRegistry([PipelineStub()])
    policy = ToolPolicy(
        allowed_tools={"pipeline"},
        require_confirmation_tools={"pipeline"},
    )

    result = execute_mcp_tool_call(
        registry,
        MCPToolCall("pipeline", {"skip_download": True}),
        policy=policy,
        confirmed=False,
    )

    assert result.status == "denied"
    assert "Confirmation required" in result.content


def test_require_confirmation_confirmed_executes() -> None:
    registry = ToolRegistry([PipelineStub()])
    policy = ToolPolicy(
        allowed_tools={"pipeline"},
        require_confirmation_tools={"pipeline"},
    )

    result = execute_mcp_tool_call(
        registry,
        MCPToolCall("pipeline", {"skip_download": True}),
        policy=policy,
        confirmed=True,
    )

    assert result.status == "ok"
    assert result.content == "pipeline ok"


def test_execute_mcp_tool_call_allow_invokes_tool() -> None:
    tool = DataSummaryStub()
    registry = ToolRegistry([tool])
    policy = ToolPolicy(allowed_tools={"data_summary"})

    result = execute_mcp_tool_call(
        registry,
        MCPToolCall("data_summary", {"path": "sample.parquet"}),
        policy=policy,
    )

    assert result.status == "ok"
    assert tool.called is True


def test_execute_mcp_tool_call_deny_does_not_invoke_tool() -> None:
    tool = DataSummaryStub()
    registry = ToolRegistry([tool])
    policy = ToolPolicy(allowed_tools={"data_summary"})

    result = execute_mcp_tool_call(
        registry,
        MCPToolCall("shell_data_summary", {"path": "sample.parquet"}),
        policy=policy,
    )

    assert result.status == "denied"
    assert tool.called is False


def test_build_supervisor_card_contains_quant_tools() -> None:
    card = build_supervisor_card()

    assert set(card.tools) >= {
        "data_summary",
        "backtest",
        "train_model",
        "report",
        "ml_backtest",
        "pipeline",
        "risk_check",
    }
    assert "no_live_orders" in card.safety_constraints


def test_agent_card_to_dict_is_json_serializable() -> None:
    payload = agent_card_to_dict(build_supervisor_card())

    assert json.loads(json.dumps(payload))["name"] == "SupervisorAgent"


def test_export_agent_cards_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/export_agent_cards.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--include-mcp-specs" in result.stdout


def test_export_agent_cards_writes_files(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_agent_cards.py",
            "--config",
            "configs/protocols.yaml",
            "--output-dir",
            str(tmp_path),
            "--include-mcp-specs",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (tmp_path / "supervisor_agent_card.json").exists()
    assert (tmp_path / "research_agent_card.json").exists()
    assert (tmp_path / "report_agent_card.json").exists()
    assert (tmp_path / "mcp_tools.json").exists()
