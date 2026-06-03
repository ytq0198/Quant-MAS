"""Neo4j graph store skeleton for experiment relationships."""

from __future__ import annotations

import os
from typing import Any, Protocol


class Neo4jSession(Protocol):
    def run(self, query: str, **kwargs: Any) -> Any: ...
    def __enter__(self) -> "Neo4jSession": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...


class Neo4jDriver(Protocol):
    def session(self) -> Neo4jSession: ...
    def close(self) -> None: ...


class Neo4jGraphStore:
    """Small Neo4j CRUD wrapper for strategy-feature-experiment graphs."""

    def __init__(
        self,
        *,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        driver: Neo4jDriver | None = None,
    ) -> None:
        self.uri = uri or os.getenv("NEO4J_URI")
        self.user = user or os.getenv("NEO4J_USER")
        self.password = password or os.getenv("NEO4J_PASSWORD")
        self._driver = driver
        if self._driver is None:
            if not (self.uri and self.user and self.password):
                raise ValueError("Neo4j requires NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD")
            try:
                from neo4j import GraphDatabase
            except ImportError as exc:
                raise ImportError("Neo4j backend requires neo4j Python driver.") from exc
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
            )

    def upsert_experiment(
        self,
        *,
        experiment_id: str,
        name: str,
        family: str = "unknown",
        metrics: dict[str, Any] | None = None,
    ) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MERGE (e:Experiment {id: $experiment_id})
                SET e.name = $name,
                    e.family = $family,
                    e.metrics = $metrics
                """,
                experiment_id=experiment_id,
                name=name,
                family=family,
                metrics=metrics or {},
            )

    def upsert_strategy(self, *, name: str, strategy_type: str = "unknown") -> None:
        with self._driver.session() as session:
            session.run(
                """
                MERGE (s:Strategy {name: $name})
                SET s.strategy_type = $strategy_type
                """,
                name=name,
                strategy_type=strategy_type,
            )

    def link_experiment_strategy(self, *, experiment_id: str, strategy_name: str) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MATCH (e:Experiment {id: $experiment_id})
                MERGE (s:Strategy {name: $strategy_name})
                MERGE (e)-[:USES_STRATEGY]->(s)
                """,
                experiment_id=experiment_id,
                strategy_name=strategy_name,
            )

    def link_experiment_feature(self, *, experiment_id: str, feature_name: str) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MATCH (e:Experiment {id: $experiment_id})
                MERGE (f:Feature {name: $feature_name})
                MERGE (e)-[:USES_FEATURE]->(f)
                """,
                experiment_id=experiment_id,
                feature_name=feature_name,
            )

    def close(self) -> None:
        self._driver.close()
