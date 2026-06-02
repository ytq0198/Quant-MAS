"""SQLite MemoryStore backend."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from quant_mas.memory.experiment_memory import ExperimentRecord, _json_safe
from quant_mas.memory.store_base import (
    MemoryStore,
    sort_records_by_metric,
    resolve_metric,
)


class SqliteMemoryStore(MemoryStore):
    """SQLite-backed experiment memory store."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
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
            metrics=metrics or {},
            artifacts={
                key: str(Path(value).expanduser())
                for key, value in (artifacts or {}).items()
            },
            params=_json_safe(params or {}),
            notes=notes,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO experiments (
                    id, name, status, created_at, metrics_json,
                    artifacts_json, params_json, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
        return record

    def get(self, experiment_id: str) -> ExperimentRecord:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM experiments WHERE id = ?",
                (experiment_id,),
            ).fetchone()
        if row is None:
            raise ValueError(f"Experiment not found: {experiment_id}")
        return self._row_to_record(row)

    def list(self) -> list[ExperimentRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM experiments ORDER BY rowid ASC"
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

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
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    artifacts_json TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    notes TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ExperimentRecord:
        return ExperimentRecord(
            experiment_id=row["id"],
            name=row["name"],
            status=row["status"],
            created_at=row["created_at"],
            metrics=json.loads(row["metrics_json"]),
            artifacts=json.loads(row["artifacts_json"]),
            params=json.loads(row["params_json"]),
            notes=row["notes"],
        )
