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
            params=_json_safe(params or {}),
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

    def get(self, experiment_id: str) -> ExperimentRecord:
        """Return one experiment by id."""
        for record in self.list():
            if record.experiment_id == experiment_id:
                return record
        raise ValueError(f"Experiment not found: {experiment_id}")

    def search_by_name(
        self,
        keyword: str,
        *,
        case_sensitive: bool = False,
    ) -> list[ExperimentRecord]:
        """Search experiments by substring match on name."""
        if not keyword:
            return []
        needle = keyword if case_sensitive else keyword.lower()
        results = []
        for record in self.list():
            haystack = record.name if case_sensitive else record.name.lower()
            if needle in haystack:
                results.append(record)
        return results

    def sort_by_metric(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> list[ExperimentRecord]:
        """Sort records by a metric value, keeping missing metrics last."""
        records = self.list()
        present = [
            record
            for record in records
            if _resolve_metric(record.metrics, metric) is not None
        ]
        missing = [
            record
            for record in records
            if _resolve_metric(record.metrics, metric) is None
        ]
        present.sort(
            key=lambda record: _resolve_metric(record.metrics, metric),
            reverse=descending,
        )
        return present + missing

    def list_artifact_paths(self, experiment_id: str) -> dict[str, str]:
        """Return artifact paths for one experiment."""
        return dict(self.get(experiment_id).artifacts)

    def find_best(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> ExperimentRecord:
        """Return the best experiment by metric."""
        sorted_records = self.sort_by_metric(metric, descending=descending)
        if not sorted_records or _resolve_metric(sorted_records[0].metrics, metric) is None:
            raise ValueError(f"No experiments contain metric: {metric}")
        return sorted_records[0]

    def _write(self, records: list[ExperimentRecord]) -> None:
        payload = [record.__dict__ for record in records]
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value.expanduser())
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _resolve_metric(metrics: dict[str, Any], metric: str) -> Any:
    current: Any = metrics
    for part in metric.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current
