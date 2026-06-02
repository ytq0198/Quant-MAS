"""JSON-backed experiment memory."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ExperimentRecord:
    """Serializable experiment record."""

    experiment_id: str
    name: str
    status: str
    created_at: str
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


class ExperimentMemory:
    """Append-only JSON storage for lightweight experiment records."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

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
            params=params or {},
            notes=notes,
        )
        records = self.list()
        records.append(record)
        self._write(records)
        return record

    def list(self) -> list[ExperimentRecord]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [ExperimentRecord(**item) for item in raw]

    def latest(self) -> ExperimentRecord:
        records = self.list()
        if not records:
            raise ValueError("No experiments recorded")
        return records[-1]

    def _write(self, records: list[ExperimentRecord]) -> None:
        payload = [record.__dict__ for record in records]
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

