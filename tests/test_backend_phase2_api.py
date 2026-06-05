import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_agents_endpoint_lists_registered_agents():
    client = TestClient(app)

    response = client.get("/api/agents")

    assert response.status_code == 200
    names = {agent["name"] for agent in response.json()}
    assert "ResearchAgent" in names


def test_tools_endpoint_lists_controlled_tools():
    client = TestClient(app)

    response = client.get("/api/tools")

    assert response.status_code == 200
    tool_names = {tool["name"] for tool in response.json()}
    assert "RiskTool" in tool_names


def test_memory_search_endpoint_returns_local_fixture_results():
    client = TestClient(app)

    response = client.get("/api/memory/search", params={"q": "OOS"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local-fixture"
    assert payload["results"]


def test_agent_run_endpoint_is_mock_safe():
    client = TestClient(app)

    response = client.post(
        "/api/agents/run",
        json={"agent": "ResearchAgent", "task": "Summarize safety boundary"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["live_trading_enabled"] is False
