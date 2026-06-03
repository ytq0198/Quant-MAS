"""PostgreSQL MemoryStore backend for enterprise deployments."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from quant_mas.memory._psycopg_compat import pg_execute, pg_fetchall, pg_fetchone
from quant_mas.memory.experiment_memory import ExperimentRecord, _json_safe
from quant_mas.memory.store_base import (
    MemoryStore,
    resolve_metric,
    sort_records_by_metric,
)


class PostgresConnection(Protocol):
    """Small DB-API compatible protocol used for tests and psycopg."""

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> Any: ...
    def fetchone(self) -> Any: ...
    def fetchall(self) -> list[Any]: ...
    def commit(self) -> None: ...
    def close(self) -> None: ...


class PostgresMemoryStore(MemoryStore):
    """PostgreSQL-backed experiment memory store.

    The store uses JSONB for nested metrics and keeps Python-side metric
    resolution aligned with JsonMemoryStore/SqliteMemoryStore.
    """

    def __init__(
        self,
        dsn: str | None = None,
        *,
        connection: PostgresConnection | None = None,
        initialize: bool = True,
    ) -> None:
        self.dsn = dsn or os.getenv("POSTGRES_DSN")
        self._provided_connection = connection
        if self._provided_connection is None and not self.dsn:
            raise ValueError("Postgres backend requires POSTGRES_DSN or dsn")
        if initialize:
            self._initialize()

    def add(
        self,
        *,
        name: str,
        status: str = "completed",
        metrics: dict[str, Any] | None = None,
        artifacts: dict[str, str | Path] | None = None,
        params: dict[str, Any] | None = None,
        notes: str = "",
        experiment_id: str | None = None,
    ) -> ExperimentRecord:
        record = ExperimentRecord(
            experiment_id=experiment_id or uuid4().hex,
            name=name,
            status=status,
            created_at=datetime.now(UTC).isoformat(),
            metrics=_json_safe(metrics or {}),
            artifacts={
                key: str(Path(value).expanduser())
                for key, value in (artifacts or {}).items()
            },
            params=_json_safe(params or {}),
            notes=notes,
        )
        connection = self._connect()
        try:
            pg_execute(
                connection,
                """
                INSERT INTO experiments (
                    id, name, status, created_at, metrics_json,
                    artifacts_json, params_json, notes
                )
                VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s)
                """,
                (
                    record.experiment_id,
                    record.name,
                    record.status,
                    record.created_at,
                    json.dumps(record.metrics, ensure_ascii=False),
                    json.dumps(record.artifacts, ensure_ascii=False),
                    json.dumps(record.params, ensure_ascii=False),
                    record.notes,
                ),
            )
            connection.commit()
        finally:
            self._close_if_owned(connection)
        return record

    def get(self, experiment_id: str) -> ExperimentRecord:
        connection = self._connect()
        try:
            row = pg_fetchone(
                connection,
                """
                SELECT id, name, status, created_at, metrics_json,
                       artifacts_json, params_json, notes
                FROM experiments
                WHERE id = %s
                """,
                (experiment_id,),
            )
        finally:
            self._close_if_owned(connection)
        if row is None:
            raise ValueError(f"Experiment not found: {experiment_id}")
        return _row_to_record(row)

    def list(self) -> list[ExperimentRecord]:
        connection = self._connect()
        try:
            rows = pg_fetchall(
                connection,
                """
                SELECT id, name, status, created_at, metrics_json,
                       artifacts_json, params_json, notes
                FROM experiments
                ORDER BY created_at ASC, id ASC
                """
            )
        finally:
            self._close_if_owned(connection)
        return [_row_to_record(row) for row in rows]

    def search_by_name(
        self,
        keyword: str,
        *,
        case_sensitive: bool = False,
    ) -> list[ExperimentRecord]:
        if not keyword:
            return []
        needle = keyword if case_sensitive else keyword.lower()
        records = []
        for record in self.list():
            haystack = record.name if case_sensitive else record.name.lower()
            if needle in haystack:
                records.append(record)
        return records

    def sort_by_metric(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> list[ExperimentRecord]:
        return sort_records_by_metric(self.list(), metric, descending=descending)

    def find_best(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> ExperimentRecord:
        sorted_records = self.sort_by_metric(metric, descending=descending)
        if not sorted_records or resolve_metric(sorted_records[0].metrics, metric) is None:
            raise ValueError(f"No experiments contain metric: {metric}")
        return sorted_records[0]

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            pg_execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metrics_json JSONB NOT NULL,
                    artifacts_json JSONB NOT NULL,
                    params_json JSONB NOT NULL,
                    notes TEXT NOT NULL
                )
                """
            )
            connection.commit()
        finally:
            self._close_if_owned(connection)

    def _connect(self) -> PostgresConnection:
        if self._provided_connection is not None:
            return self._provided_connection
        try:
            import psycopg
        except ImportError as exc:
            raise ImportError(
                "Postgres backend requires psycopg. Install an enterprise extra or psycopg."
            ) from exc
        return psycopg.connect(self.dsn)

    def _close_if_owned(self, connection: PostgresConnection) -> None:
        if self._provided_connection is None:
            connection.close()


def _row_to_record(row: Any) -> ExperimentRecord:
    if isinstance(row, dict):
        values = row
    elif hasattr(row, "keys"):
        values = {key: row[key] for key in row.keys()}
    else:
        keys = [
            "id",
            "name",
            "status",
            "created_at",
            "metrics_json",
            "artifacts_json",
            "params_json",
            "notes",
        ]
        values = dict(zip(keys, row, strict=True))
    return ExperimentRecord(
        experiment_id=str(values["id"]),
        name=str(values["name"]),
        status=str(values["status"]),
        created_at=str(values["created_at"]),
        metrics=_json_loads_if_needed(values["metrics_json"]),
        artifacts=_json_loads_if_needed(values["artifacts_json"]),
        params=_json_loads_if_needed(values["params_json"]),
        notes=str(values["notes"]),
    )


def _json_loads_if_needed(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return json.loads(value)
