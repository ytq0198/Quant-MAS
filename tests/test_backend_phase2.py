from backend.services.agents import list_agents, run_agent_task
from backend.services.memory import search_memory
from backend.services.tools import list_tools


def test_list_agents_exposes_mock_safe_research_agents():
    agents = list_agents()

    agent_names = {agent["name"] for agent in agents}
    assert {"SupervisorAgent", "ResearchAgent", "ReportAgent"}.issubset(agent_names)
    assert all(agent["live_trading_enabled"] is False for agent in agents)


def test_list_tools_exposes_controlled_quant_tools():
    tools = list_tools()

    tool_names = {tool["name"] for tool in tools}
    assert {"BacktestTool", "RiskTool", "PipelineTool"}.issubset(tool_names)
    assert all("broker" not in tool["allowed_operations"] for tool in tools)
    assert all("order" not in tool["allowed_operations"] for tool in tools)


def test_memory_search_returns_local_research_context():
    results = search_memory("OOS baseline")

    assert results["query"] == "OOS baseline"
    assert results["mode"] == "local-fixture"
    assert results["results"]
    assert any("EXP-20260602-008" in item["title"] for item in results["results"])


def test_run_agent_task_is_mock_safe_and_auditable():
    result = run_agent_task("ResearchAgent", "Summarize OOS baseline")

    assert result["agent"] == "ResearchAgent"
    assert result["status"] == "completed"
    assert result["live_trading_enabled"] is False
    assert "audit" in result["events"][0]["type"]
    assert "LLM agents do not place live orders." in result["safety_notes"]
