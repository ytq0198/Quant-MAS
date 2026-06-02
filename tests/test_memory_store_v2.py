from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from quant_mas.memory import (
    ExperimentMemory,
    JsonMemoryStore,
    SqliteMemoryStore,
    create_memory_store_from_yaml,
)
from quant_mas.rag import (
    Document,
    HashEmbeddingClient,
    HybridRetriever,
    InMemoryVectorStore,
    SimpleRetriever,
    chunk_text,
)


def add_records(store):
    first = store.add(
        experiment_id="exp-1",
        name="ma_cross",
        metrics={"sharpe": 0.7, "oos": {"sharpe": 0.3}},
        artifacts={"summary": "ma.md"},
    )
    second = store.add(
        experiment_id="exp-2",
        name="walk_forward",
        metrics={"sharpe": 1.1, "oos": {"sharpe": 1.4}},
        artifacts={"summary": "wf.md"},
    )
    third = store.add(
        experiment_id="exp-3",
        name="missing_metric",
        metrics={"total_return": 0.1},
    )
    return first, second, third


def test_json_memory_store_matches_experiment_memory(tmp_path: Path) -> None:
    path = tmp_path / "experiments.json"
    store = JsonMemoryStore(path)
    records = add_records(store)

    memory = ExperimentMemory(path)

    assert memory.list() == list(records)
    assert store.get("exp-2").name == "walk_forward"
    assert store.find_best("oos.sharpe").experiment_id == "exp-2"
    assert [record.experiment_id for record in store.search_by_name("walk")] == ["exp-2"]


def test_sqlite_memory_store_crud_and_nested_best(tmp_path: Path) -> None:
    store = SqliteMemoryStore(tmp_path / "experiments.db")
    add_records(store)

    assert store.get("exp-1").name == "ma_cross"
    assert len(store.list()) == 3
    assert store.find_best("oos.sharpe").experiment_id == "exp-2"
    assert [record.experiment_id for record in store.sort_by_metric("oos.sharpe")] == [
        "exp-2",
        "exp-1",
        "exp-3",
    ]


def test_json_and_sqlite_metric_order_consistent(tmp_path: Path) -> None:
    json_store = JsonMemoryStore(tmp_path / "experiments.json")
    sqlite_store = SqliteMemoryStore(tmp_path / "experiments.db")
    add_records(json_store)
    add_records(sqlite_store)

    assert [
        record.experiment_id for record in json_store.sort_by_metric("oos.sharpe")
    ] == [
        record.experiment_id for record in sqlite_store.sort_by_metric("oos.sharpe")
    ]


def test_hash_embedding_client_is_deterministic() -> None:
    client = HashEmbeddingClient(dimensions=8)

    first = client.embed(["walk forward"])[0]
    second = client.embed(["walk forward"])[0]
    other = client.embed(["risk"])[0]

    assert first == second
    assert first != other
    assert len(first) == 8


def test_in_memory_vector_store_upsert_search_and_delete() -> None:
    store = InMemoryVectorStore()
    store.upsert(
        ["a", "b"],
        [[1.0, 0.0], [0.0, 1.0]],
        [{"title": "A"}, {"title": "B"}],
    )

    results = store.search([1.0, 0.0], top_k=1)
    store.delete(["a"])

    assert results[0].id == "a"
    assert results[0].metadata["title"] == "A"
    assert [result.id for result in store.search([1.0, 0.0], top_k=2)] == ["b"]


def test_chunk_text_length_and_overlap() -> None:
    chunks = chunk_text("abcdefghij", chunk_size=4, overlap=1)

    assert chunks == ["abcd", "defg", "ghij"]


def test_hybrid_retriever_keyword_only() -> None:
    document = Document(
        doc_id="note.md",
        path=Path("note.md"),
        title="Note",
        content="walk-forward sharpe",
        metadata={},
    )
    retriever = HybridRetriever(keyword_retriever=SimpleRetriever([document]))

    results = retriever.search("walk-forward")

    assert results[0].document.doc_id == "note.md"
    assert results[0].sources == ["keyword"]


def test_hybrid_retriever_merges_vector_hits() -> None:
    document = Document(
        doc_id="note.md",
        path=Path("note.md"),
        title="Note",
        content="walk-forward sharpe",
        metadata={},
    )
    embedding_client = HashEmbeddingClient(dimensions=8)
    vector_store = InMemoryVectorStore()
    vector_store.upsert(
        ["chunk-1"],
        embedding_client.embed(["walk-forward sharpe"]),
        [
            {
                "doc_id": "note.md",
                "path": "note.md",
                "title": "Note",
                "content": "walk-forward sharpe",
            }
        ],
    )
    retriever = HybridRetriever(
        keyword_retriever=SimpleRetriever([document]),
        vector_store=vector_store,
        embedding_client=embedding_client,
    )

    results = retriever.search("walk-forward")

    assert results[0].document.doc_id == "note.md"
    assert set(results[0].sources) == {"keyword", "vector"}


def test_create_memory_store_from_yaml(tmp_path: Path) -> None:
    config = tmp_path / "memory.yaml"
    config.write_text(
        "\n".join(
            [
                "memory_backend: sqlite",
                "sqlite_path: experiments.db",
                "json_path: experiments.json",
            ]
        ),
        encoding="utf-8",
    )

    store = create_memory_store_from_yaml(config)
    record = store.add(experiment_id="exp-1", name="sqlite", metrics={"sharpe": 1.0})

    assert record.experiment_id == "exp-1"
    assert (tmp_path / "experiments.db").exists()


def test_index_documents_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/index_documents.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--vector-store" in result.stdout


def test_query_memory_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/query_memory.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--best-metric" in result.stdout
