from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.services.config import get_audit_dir


def list_audit_logs(artifact_root: str | Path | None = None, limit: int = 50) -> dict[str, Any]:
    """List audit JSONL events from configured audit directory.

    从配置的审计目录列出 JSONL 审计事件。
    """
    audit_dir = get_audit_dir(artifact_root)
    if not audit_dir.exists():
        return {"source": "fallback_empty", "path": str(audit_dir), "events": []}

    events: list[dict[str, Any]] = []
    for jsonl_path in sorted(audit_dir.rglob("*.jsonl")):
        events.extend(_read_jsonl_events(jsonl_path, limit - len(events)))
        if len(events) >= limit:
            break

    return {
        "source": "server_artifact" if events else "fallback_empty",
        "path": str(audit_dir),
        "events": events,
    }


def _read_jsonl_events(jsonl_path: Path, limit: int) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if limit <= 0:
        return events
    try:
        lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return events
    for line in lines:
        if len(events) >= limit:
            break
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("source_path", str(jsonl_path))
            events.append(payload)
    return events
