from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def get_recent_logs(log_root: str | Path | None = None, limit: int = 50) -> dict[str, Any]:
    """Return recent JSONL log events from configured log root.

    从配置日志目录返回最近 JSONL 事件。
    """
    root = Path(log_root or os.getenv("QUANT_MAS_LOG_ROOT", "logs")).expanduser()
    if not root.exists():
        return {"source": "fallback_empty", "path": str(root), "events": []}
    events: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.jsonl")):
        events.extend(_read_jsonl(path, limit - len(events)))
        if len(events) >= limit:
            break
    return {"source": "server_logs" if events else "fallback_empty", "path": str(root), "events": events}


def _read_jsonl(path: Path, limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    events: list[dict[str, Any]] = []
    for line in lines:
        if len(events) >= limit:
            break
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("source_path", str(path))
            events.append(payload)
    return events
