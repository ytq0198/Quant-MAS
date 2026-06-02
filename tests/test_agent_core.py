from __future__ import annotations

import pytest

from quant_mas.agents import ReportAgent
from quant_mas.core import BaseAgent, Message, MockLLMClient
from quant_mas.tools import BaseTool, ToolRegistry, ToolResult


class EchoAgent(BaseAgent):
    def step(self, *, step: int, **kwargs) -> Message:
        return self.llm_client.complete(self.history)


class NeverFinishAgent(EchoAgent):
    def is_finished(self, response: Message, *, step: int) -> bool:
        return False


class EchoTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="echo", description="Echo input text.")

    def run(self, **kwargs) -> ToolResult:
        return ToolResult(content=str(kwargs["text"]), metadata={"ok": True})


def test_message_converts_to_openai_style_dict() -> None:
    message = Message(role="user", content="hello", name="tester")

    assert message.to_dict() == {
        "role": "user",
        "content": "hello",
        "name": "tester",
    }
    restored = Message.from_dict({"role": "assistant", "content": "hi"})
    assert restored.role == "assistant"
    assert restored.content == "hi"


def test_mock_llm_client_returns_deterministic_response() -> None:
    client = MockLLMClient(["fixed"])
    response = client.complete([Message(role="user", content="hello")])

    assert response.role == "assistant"
    assert response.content == "fixed"
    assert len(client.calls) == 1


def test_base_agent_tracks_history_and_respects_max_steps() -> None:
    agent = EchoAgent(
        name="echo-agent",
        llm_client=MockLLMClient(["done"]),
        system_prompt="system",
        max_steps=1,
    )

    result = agent.run("task")

    assert result == "done"
    assert [message.role for message in agent.history] == [
        "system",
        "user",
        "assistant",
    ]


def test_base_agent_raises_when_max_steps_exceeded() -> None:
    agent = NeverFinishAgent(
        name="never-finish",
        llm_client=MockLLMClient(["step1", "step2"]),
        max_steps=2,
    )

    with pytest.raises(RuntimeError, match="max_steps"):
        agent.run("task")


def test_tool_registry_registers_and_runs_tools() -> None:
    registry = ToolRegistry()
    tool = EchoTool()

    registry.register(tool)
    result = registry.get("echo").run(text="hello")

    assert registry.names() == ["echo"]
    assert result.content == "hello"
    assert result.metadata["ok"] is True
    with pytest.raises(ValueError):
        registry.register(tool)


def test_report_agent_uses_mock_llm_without_real_api() -> None:
    client = MockLLMClient(["# Report\nNo live trading recommended."])
    agent = ReportAgent(client)

    report = agent.generate_report(
        title="Backtest",
        metrics={"total_return": 0.1, "max_drawdown": -0.05},
        notes="synthetic",
    )

    assert "No live trading" in report
    assert len(client.calls) == 1
    user_payload = client.calls[0][-1].content
    assert "total_return" in user_payload

