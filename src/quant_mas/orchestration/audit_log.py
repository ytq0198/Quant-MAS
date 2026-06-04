"""Append-only JSONL audit log helpers for M13 orchestration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class AuditEvent:
    """One scheduler audit event."""

    pipeline_id: str
    run_id: str
    node_id: str
    status: str
    metric_family: str
    timestamp: str = field(default_factory=_now_iso)
    duration_ms: int = 0
    artifacts: dict[str, str] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def append_audit_event(path: str | Path, event: AuditEvent) -> None:
    """Append one event to a JSONL audit log."""
    audit_path = Path(path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def read_audit_tail(path: str | Path, *, limit: int = 20) -> list[dict[str, Any]]:
    """Read the last ``limit`` audit events."""
    audit_path = Path(path)
    if not audit_path.exists():
        return []
    rows = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if limit <= 0:
        return []
    return rows[-limit:]


def summarize_audit_log(path: str | Path) -> dict[str, Any]:
    """Return compact audit counts for a JSONL log."""
    audit_path = Path(path)
    rows = read_audit_tail(audit_path, limit=10**9)
    status_counts: dict[str, int] = {}
    families: set[str] = set()
    nodes: list[str] = []
    for row in rows:
        status = str(row.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
        families.add(str(row.get("metric_family", "")))
        nodes.append(str(row.get("node_id", "")))
    return {
        "path": str(audit_path),
        "total_events": len(rows),
        "status_counts": status_counts,
        "metric_families": sorted(item for item in families if item),
        "nodes": nodes,
    }
