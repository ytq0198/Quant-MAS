from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

import pytest

from quant_mas.memory import Neo4jGraphStore, PostgresMemoryStore, create_memory_store
from quant_mas.rag import PgVectorStore


class FakePostgresConnection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.last_result: list[dict[str, Any]] = []
        self.queries: list[str] = []
        self.commits = 0
        self.closed = False

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> None:
        self.queries.append(query)
        normalized = " ".join(query.lower().split())
        if normalized.startswith("insert into experiments"):
            assert params is not None
            row = {
                "id": params[0],
                "name": params[1],
                "status": params[2],
                "created_at": params[3],
                "metrics_json": params[4],
                "artifacts_json": params[5],
                "params_json": params[6],
                "notes": params[7],
            }
            self.rows = [item for item in self.rows if item["id"] != row["id"]]
            self.rows.append(row)
        elif "where id = %s" in normalized:
            assert params is not None
            self.last_result = [row for row in self.rows if row["id"] == params[0]]
        elif normalized.startswith("select id, name"):
            self.last_result = list(self.rows)

    def fetchone(self):
        return self.last_result[0] if self.last_result else None

    def fetchall(self):
        return list(self.last_result)

    def commit(self) -> None:
        self.commits += 1

    def close(self) -> None:
        self.closed = True


class FakePgVectorConnection:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, Any]] = {}
        self.last_result: list[tuple[str, str, float]] = []
        self.queries: list[str] = []
        self.commits = 0

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> None:
        self.queries.append(query)
        normalized = " ".join(query.lower().split())
        if normalized.startswith("insert into"):
            assert params is not None
            self.rows[str(params[0])] = {
                "embedding": params[1],
                "metadata": params[2],
            }
        elif normalized.startswith("select id"):
            self.last_result = [
                (id_, row["metadata"], 1.0 - index * 0.1)
                for index, (id_, row) in enumerate(sorted(self.rows.items()))
            ]
            if params:
                self.last_result = self.last_result[: int(params[-1])]
        elif normalized.startswith("delete from"):
            assert params is not None
            self.rows.pop(str(params[0]), None)

    def fetchall(self):
        return list(self.last_result)

    def commit(self) -> None:
        self.commits += 1

    def close(self) -> None:
        pass


class FakeSession:
    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query: str, **kwargs: Any) -> None:
        self.calls.append((query, kwargs))


class FakeNeo4jDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.closed = False

    def session(self) -> FakeSession:
        return FakeSession(self.calls)

    def close(self) -> None:
        self.closed = True


def test_postgres_memory_store_add_get_and_nested_metric_sort() -> None:
    connection = FakePostgresConnection()
    store = PostgresMemoryStore(connection=connection)

    store.add(
        experiment_id="a",
        name="low",
        metrics={"oos": {"sharpe": 0.1}},
        artifacts={"summary": "a.md"},
    )
    store.add(
        experiment_id="b",
        name="high",
        metrics={"oos": {"sharpe": 0.5}},
        artifacts={"summary": "b.md"},
    )

    assert store.get("a").name == "low"
    assert store.find_best("oos.sharpe").experiment_id == "b"
    assert [record.experiment_id for record in store.sort_by_metric("oos.sharpe")] == ["b", "a"]
    assert connection.commits >= 3


def test_postgres_memory_search_by_name_case_insensitive() -> None:
    connection = FakePostgresConnection()
    store = PostgresMemoryStore(connection=connection)
    store.add(experiment_id="exp", name="Walk Forward Baseline")

    results = store.search_by_name("walk")

    assert len(results) == 1
    assert results[0].experiment_id == "exp"


def test_postgres_store_requires_dsn_or_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POSTGRES_DSN", raising=False)

    with pytest.raises(ValueError, match="POSTGRES_DSN"):
        PostgresMemoryStore(initialize=False)


def test_memory_factory_accepts_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://example")

    store = create_memory_store("postgres", connection=FakePostgresConnection())

    assert isinstance(store, PostgresMemoryStore)


def test_pgvector_store_upsert_search_delete() -> None:
    connection = FakePgVectorConnection()
    store = PgVectorStore(connection=connection, dimensions=3)

    store.upsert(
        ["doc1", "doc2"],
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        [{"title": "one"}, {"title": "two"}],
    )
    results = store.search([1.0, 0.0, 0.0], top_k=1)
    store.delete(["doc1"])

    assert results[0].id == "doc1"
    assert results[0].metadata["title"] == "one"
    assert "doc1" not in connection.rows


def test_pgvector_rejects_dimension_mismatch() -> None:
    store = PgVectorStore(connection=FakePgVectorConnection(), dimensions=3)

    with pytest.raises(ValueError, match="dimension"):
        store.upsert(["bad"], [[1.0, 2.0]], [{}])


def test_pgvector_requires_dsn_or_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POSTGRES_DSN", raising=False)

    with pytest.raises(ValueError, match="POSTGRES_DSN"):
        PgVectorStore(initialize=False)


def test_neo4j_graph_store_records_queries_with_mock_driver() -> None:
    driver = FakeNeo4jDriver()
    store = Neo4jGraphStore(driver=driver)

    store.upsert_experiment(
        experiment_id="exp1",
        name="experiment",
        family="walk_forward",
        metrics={"oos": {"sharpe": 0.586}},
    )
    store.upsert_strategy(name="ma_cross", strategy_type="baseline")
    store.link_experiment_strategy(experiment_id="exp1", strategy_name="ma_cross")
    store.link_experiment_feature(experiment_id="exp1", feature_name="rsi_14")
    store.close()

    assert len(driver.calls) == 4
    assert driver.closed is True
    assert any("USES_STRATEGY" in query for query, _ in driver.calls)


def test_neo4j_requires_env_or_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NEO4J_URI", raising=False)
    monkeypatch.delenv("NEO4J_USER", raising=False)
    monkeypatch.delenv("NEO4J_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="Neo4j"):
        Neo4jGraphStore()


def test_query_memory_help_lists_postgres_backend() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/query_memory.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "postgres" in result.stdout


def test_index_documents_help_lists_pgvector_backend() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/index_documents.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "pgvector" in result.stdout


def test_enterprise_config_example_is_valid_yaml() -> None:
    import yaml

    config = yaml.safe_load(
        open("configs/memory.enterprise.yaml.example", encoding="utf-8")
    )

    assert config["memory_backend"] == "postgres"
    assert config["vector_store"] == "pgvector"
    assert "neo4j" in config
