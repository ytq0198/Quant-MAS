from __future__ import annotations

from pathlib import Path

import pytest

from quant_mas.memory import ExperimentMemory, TradeMemory, TradeRecord
from quant_mas.rag import SimpleRetriever, load_document, load_documents


def seed_experiments(path: Path) -> tuple[ExperimentMemory, list]:
    memory = ExperimentMemory(path)
    records = [
        memory.add(
            experiment_id="exp-001",
            name="server_lgbm_gpu",
            metrics={"sharpe": 1.1, "total_return": 0.2, "oos": {"sharpe": 0.7}},
            artifacts={"summary": path.parent / "gpu.md"},
        ),
        memory.add(
            experiment_id="exp-002",
            name="walk-forward 样本外",
            metrics={"sharpe": 2.0, "total_return": 0.1, "oos": {"sharpe": 1.4}},
            artifacts={"summary": path.parent / "wf.md"},
        ),
        memory.add(
            experiment_id="exp-003",
            name="baseline report",
            metrics={"total_return": -0.1},
            artifacts={"metrics": path.parent / "metrics.json"},
        ),
    ]
    return memory, records


def test_experiment_memory_get_and_artifacts(tmp_path: Path) -> None:
    memory, records = seed_experiments(tmp_path / "experiments.json")

    found = memory.get("exp-002")
    artifacts = memory.list_artifact_paths("exp-001")

    assert found == records[1]
    assert artifacts["summary"].endswith("gpu.md")
    with pytest.raises(ValueError, match="Experiment not found"):
        memory.get("missing")


def test_experiment_memory_search_by_name(tmp_path: Path) -> None:
    memory, _ = seed_experiments(tmp_path / "experiments.json")

    assert [record.experiment_id for record in memory.search_by_name("LGBM")] == ["exp-001"]
    assert [record.experiment_id for record in memory.search_by_name("样本外")] == ["exp-002"]
    assert memory.search_by_name("LGBM", case_sensitive=True) == []


def test_experiment_memory_sort_and_find_best_metric(tmp_path: Path) -> None:
    memory, _ = seed_experiments(tmp_path / "experiments.json")

    by_sharpe = memory.sort_by_metric("sharpe")
    by_oos = memory.sort_by_metric("oos.sharpe")
    best = memory.find_best("total_return")

    assert [record.experiment_id for record in by_sharpe] == ["exp-002", "exp-001", "exp-003"]
    assert [record.experiment_id for record in by_oos] == ["exp-002", "exp-001", "exp-003"]
    assert best.experiment_id == "exp-001"


def test_experiment_memory_find_best_missing_metric_raises(tmp_path: Path) -> None:
    memory, _ = seed_experiments(tmp_path / "experiments.json")

    with pytest.raises(ValueError, match="No experiments contain metric"):
        memory.find_best("missing_metric")


def test_trade_memory_append_list_latest(tmp_path: Path) -> None:
    memory = TradeMemory(tmp_path / "trades.jsonl")
    first = TradeRecord(
        trade_id="t1",
        timestamp="2026-06-02T10:00:00Z",
        symbol="AAA",
        side="buy",
        quantity=10,
        price=100,
        status="simulated",
        metadata={"source": "test"},
    )
    second = TradeRecord(
        trade_id="t2",
        timestamp="2026-06-02T10:01:00Z",
        symbol="AAA",
        side="sell",
        quantity=5,
        price=101,
        status="rejected",
        metadata={"reason": "risk"},
    )

    assert memory.append(first) == first
    memory.append(second)

    assert memory.list() == [first, second]
    assert memory.list(limit=1) == [second]
    assert memory.latest() == second


def test_trade_memory_latest_empty_raises(tmp_path: Path) -> None:
    memory = TradeMemory(tmp_path / "trades.jsonl")

    with pytest.raises(ValueError, match="No trades recorded"):
        memory.latest()


def test_load_document_md_txt_and_truncation(tmp_path: Path) -> None:
    md_path = tmp_path / "note.md"
    txt_path = tmp_path / "plain.txt"
    md_path.write_text("# Walk-forward Note\nOOS validation matters.", encoding="utf-8")
    txt_path.write_text("alpha beta gamma", encoding="utf-8")

    md_doc = load_document(md_path)
    txt_doc = load_document(txt_path, max_chars=5)

    assert md_doc.title == "Walk-forward Note"
    assert md_doc.metadata["extension"] == ".md"
    assert txt_doc.content == "alpha"
    assert txt_doc.metadata["truncated"] is True


def test_load_documents_skips_hidden_and_loads_json(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "research_notes.md").write_text("walk-forward OOS", encoding="utf-8")
    (docs / "payload.json").write_text('{"text": "risk memory"}', encoding="utf-8")
    (docs / ".hidden.md").write_text("hidden", encoding="utf-8")

    loaded = load_documents(docs)

    assert [document.doc_id for document in loaded] == ["payload.json", "research_notes.md"]
    assert any(document.content == "risk memory" for document in loaded)


def test_simple_retriever_searches_synthetic_documents(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("risk risk drawdown", encoding="utf-8")
    (docs / "b.md").write_text("risk report", encoding="utf-8")
    retriever = SimpleRetriever.from_directories([docs])

    results = retriever.search("risk", top_k=2)

    assert [result.document.doc_id for result in results] == ["a.md", "b.md"]
    assert results[0].score == 2.0
    assert results[0].matched_terms == ["risk"]


def test_simple_retriever_finds_research_notes_fixture(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "research_notes.md").write_text(
        "Prompt 17 adds walk-forward OOS evaluation.",
        encoding="utf-8",
    )
    retriever = SimpleRetriever.from_directories([docs])

    results = retriever.search("walk-forward OOS")

    assert results
    assert results[0].document.title == "research_notes"
    assert set(results[0].matched_terms) == {"walk-forward", "oos"}


def test_simple_retriever_top_k_and_tie_sort(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "b.txt").write_text("model", encoding="utf-8")
    (docs / "a.txt").write_text("model", encoding="utf-8")
    (docs / "c.txt").write_text("model model", encoding="utf-8")
    retriever = SimpleRetriever.from_directories([docs])

    results = retriever.search("model", top_k=2)

    assert [result.document.doc_id for result in results] == ["c.txt", "a.txt"]
