from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from quant_mas.agents import ReportAgent, ResearchAgent
from quant_mas.context import (
    AgentContextBundle,
    ContextBuilder,
    ExperimentContextSnapshot,
    RagContextChunk,
    RiskContextSnapshot,
    compress_metrics,
    compress_rag_chunks,
    truncate_text,
)
from quant_mas.core import (
    LocalVLLMClient,
    Message,
    MockLLMClient,
    OpenAICompatibleLLMClient,
    resolve_llm_client,
)
from quant_mas.memory import JsonMemoryStore
from quant_mas.rag import Document, SimpleRetriever


def make_storage_config(tmp_path: Path) -> Path:
    path = tmp_path / "storage.yaml"
    path.write_text(
        "\n".join(
            [
                "project_root: .",
                f"raw_data_dir: {tmp_path / 'raw'}",
                f"processed_data_dir: {tmp_path / 'processed'}",
                f"features_dir: {tmp_path / 'features'}",
                f"models_dir: {tmp_path / 'models'}",
                f"reports_dir: {tmp_path / 'reports'}",
                f"logs_dir: {tmp_path / 'logs'}",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_context_schema_round_trip() -> None:
    bundle = AgentContextBundle(
        task="compare experiments",
        experiments=[
            ExperimentContextSnapshot(
                experiment_id="exp1",
                name="walk_forward",
                metrics={"oos": {"sharpe": 0.586}},
            )
        ],
        risk=RiskContextSnapshot(approved=True, status="approved", violations=[]),
        rag_chunks=[
            RagContextChunk(
                doc_id="doc",
                path="docs/research_notes.md",
                title="notes",
                snippet="walk-forward OOS",
                score=2.0,
            )
        ],
    )

    restored = AgentContextBundle.from_dict(bundle.to_dict())

    assert restored.task == bundle.task
    assert restored.experiments[0].metrics["oos"]["sharpe"] == 0.586
    assert restored.rag_chunks[0].title == "notes"


def test_compress_metrics_keeps_selected_nested_paths() -> None:
    metrics = {
        "oos": {"sharpe": 0.586, "max_drawdown": -0.2, "unused": 99},
        "total_return": 0.1,
        "large_blob": {"x": list(range(100))},
    }

    compressed = compress_metrics(metrics, keep_keys=["oos.sharpe", "total_return"])

    assert compressed == {"oos": {"sharpe": 0.586}, "total_return": 0.1}


def test_truncate_text_and_compress_rag_chunks() -> None:
    chunks = [
        RagContextChunk("a", "a.md", "A", "x" * 100, 1.0),
        RagContextChunk("b", "b.md", "B", "short", 0.5),
    ]

    compressed = compress_rag_chunks(chunks, max_chunks=1, max_chars=20)

    assert len(compressed) == 1
    assert len(compressed[0].snippet) <= 20
    assert truncate_text("abc", 10) == "abc"
    assert truncate_text("abcdef", 0) == ""


def test_context_builder_uses_synthetic_memory(tmp_path: Path) -> None:
    store = JsonMemoryStore(tmp_path / "experiments.json")
    store.add(
        name="latest_ml_backtest",
        metrics={"sharpe": 1.2, "oos": {"sharpe": 0.4}},
        artifacts={"summary": tmp_path / "summary.md"},
    )
    store.add(
        name="walk_forward_baseline",
        metrics={"oos": {"sharpe": 0.586}},
        artifacts={"summary": tmp_path / "baseline.md"},
    )

    bundle = ContextBuilder(
        memory_store=store,
        retriever=SimpleRetriever([]),
        storage_config=make_storage_config(tmp_path),
    ).build(task="summarize")

    assert bundle.experiments
    assert bundle.baseline is not None
    assert bundle.baseline.metrics["oos"]["sharpe"] == 0.586


def test_context_builder_adds_rag_chunks(tmp_path: Path) -> None:
    document = Document(
        doc_id="research_notes.md",
        path=tmp_path / "research_notes.md",
        title="Research Notes",
        content="walk-forward OOS sharpe baseline evidence",
        metadata={},
    )
    store = JsonMemoryStore(tmp_path / "experiments.json")

    bundle = ContextBuilder(
        memory_store=store,
        retriever=SimpleRetriever([document]),
        storage_config=make_storage_config(tmp_path),
    ).build(task="Explain walk-forward", rag_query="walk-forward")

    assert bundle.rag_chunks
    assert bundle.rag_chunks[0].score > 0


def test_context_builder_summarizes_workflow_state(tmp_path: Path) -> None:
    store = JsonMemoryStore(tmp_path / "experiments.json")
    workflow_state = {
        "completed_nodes": ["data_check", "risk_check"],
        "errors": [],
        "metrics": {
            "sharpe": 1.0,
            "risk": {"approved": True, "status": "approved", "violations": []},
        },
        "artifacts": {"summary": tmp_path / "summary.md"},
    }

    bundle = ContextBuilder(
        memory_store=store,
        retriever=SimpleRetriever([]),
        storage_config=make_storage_config(tmp_path),
    ).build(task="workflow", workflow_state=workflow_state)

    assert bundle.workflow["completed_nodes"] == ["data_check", "risk_check"]
    assert bundle.risk is not None
    assert bundle.risk.approved is True


def test_resolve_llm_client_defaults_to_mock(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
    # Server .env would repopulate LLM_API_KEY after delenv; keep this test offline-safe.
    monkeypatch.setattr("quant_mas.core.llm.load_repo_dotenv", lambda *args, **kwargs: False)

    assert isinstance(resolve_llm_client(use_llm=False), MockLLMClient)
    with pytest.warns(RuntimeWarning, match="LLM_API_KEY is not set"):
        client = resolve_llm_client(use_llm=True, provider="openai_compatible")
    assert isinstance(client, MockLLMClient)


def test_openai_compatible_llm_client_mock_http(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {"choices": [{"message": {"content": '{"hypothesis":"ok"}'}}]}
            ).encode("utf-8")

    captured = {}

    def fake_urlopen(req, timeout):
        captured["authorization"] = req.headers["Authorization"]
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("quant_mas.core.llm.request.urlopen", fake_urlopen)
    client = OpenAICompatibleLLMClient(
        base_url="https://example.test",
        api_key="secret-key",
        model="test-model",
        timeout_seconds=3,
    )

    response = client.complete([Message(role="user", content="hello")])

    assert response.content == '{"hypothesis":"ok"}'
    assert captured["authorization"] == "Bearer secret-key"
    assert captured["timeout"] == 3


def test_resolve_local_vllm_without_url_falls_back_to_mock(monkeypatch) -> None:
    monkeypatch.delenv("VLLM_BASE_URL", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "local_vllm")
    monkeypatch.setattr("quant_mas.core.llm.load_repo_dotenv", lambda *args, **kwargs: False)

    with pytest.warns(RuntimeWarning, match="VLLM_BASE_URL is not set"):
        client = resolve_llm_client(use_llm=True)

    assert isinstance(client, MockLLMClient)


def test_resolve_local_vllm_with_mock_http(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "hypothesis": "local ok",
                                        "evidence_summary": "facts only",
                                        "suggested_experiments": [],
                                        "risks_and_caveats": "mocked",
                                    }
                                )
                            }
                        }
                    ]
                }
            ).encode("utf-8")

    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("quant_mas.core.llm.load_repo_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("VLLM_MODEL", "local-test-model")
    monkeypatch.delenv("VLLM_API_KEY", raising=False)
    monkeypatch.setattr("quant_mas.core.llm.request.urlopen", fake_urlopen)

    client = resolve_llm_client(use_llm=True, provider="local_vllm")
    response = client.complete([Message(role="user", content="hello")])

    assert isinstance(client, LocalVLLMClient)
    assert response.metadata["provider"] == "local_vllm"
    assert captured["url"] == "http://127.0.0.1:8000/v1/chat/completions"
    assert captured["payload"]["model"] == "local-test-model"
    assert captured["payload"]["messages"][0]["content"] == "hello"
    assert "Authorization" not in captured["headers"]
    assert captured["timeout"] == 120


def test_use_llm_false_ignores_local_vllm_env(monkeypatch) -> None:
    monkeypatch.setattr("quant_mas.core.llm.load_repo_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("LLM_PROVIDER", "local_vllm")
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:8000")

    client = resolve_llm_client(use_llm=False)

    assert isinstance(client, MockLLMClient)


def test_research_agent_returns_structured_output_without_orders() -> None:
    client = MockLLMClient(
        [
            json.dumps(
                {
                    "hypothesis": "OOS evidence is modest.",
                    "evidence_summary": "Baseline OOS sharpe is 0.586.",
                    "suggested_experiments": ["Run walk-forward ablation."],
                    "risks_and_caveats": "No live trading inference.",
                }
            )
        ]
    )
    bundle = AgentContextBundle(task="Compare latest ML run")

    output = ResearchAgent(client).run_research(bundle)

    text = json.dumps(output.to_dict()).lower()
    assert output.hypothesis
    assert output.suggested_experiments
    assert "buy" not in text
    assert "sell order" not in text


def test_research_agent_local_vllm_preserves_metrics(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "hypothesis": "OOS baseline remains primary.",
                                        "evidence_summary": "LLM narration only.",
                                        "suggested_experiments": ["Run text ablation."],
                                        "risks_and_caveats": "Do not overwrite metrics.",
                                    }
                                )
                            }
                        }
                    ]
                }
            ).encode("utf-8")

    monkeypatch.setattr("quant_mas.core.llm.load_repo_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("VLLM_MODEL", "local-test-model")
    monkeypatch.setattr("quant_mas.core.llm.request.urlopen", lambda req, timeout: FakeResponse())
    bundle = AgentContextBundle(
        task="Explain baseline",
        experiments=[
            ExperimentContextSnapshot(
                experiment_id="exp",
                name="walk_forward",
                metrics={"oos": {"sharpe": 0.586}},
            )
        ],
    )

    output = ResearchAgent(llm_provider="local_vllm", use_llm=True).run_research(bundle)

    assert output.llm_provider == "local_vllm"
    assert output.context_snapshot["experiments"][0]["metrics"]["oos"]["sharpe"] == 0.586


def test_research_agent_llm_failure_warns_and_falls_back() -> None:
    class BrokenLLMClient(MockLLMClient):
        def complete(self, messages, **kwargs):
            raise RuntimeError("service unavailable")

    bundle = AgentContextBundle(task="Explain safely")

    with pytest.warns(RuntimeWarning, match="falling back to MockLLMClient"):
        output = ResearchAgent(BrokenLLMClient()).run_research(bundle)

    assert output.llm_provider == "mock"
    assert "Mock response" in output.evidence_summary


def test_report_agent_result_preserves_metrics_without_llm() -> None:
    metrics = {"total_return": 0.1, "nested": {"sharpe": 1.0}}
    original = copy.deepcopy(metrics)
    client = MockLLMClient(["changed"])

    result = ReportAgent(client).generate_report(
        title="Report",
        metrics=metrics,
        notes="facts only",
        use_llm=False,
        return_result=True,
    )

    assert metrics == original
    assert result.metrics == original
    assert result.narrative is None
    assert len(client.calls) == 0


def test_run_research_agent_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_research_agent.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--task" in result.stdout


def test_generate_report_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--use-llm" in result.stdout
