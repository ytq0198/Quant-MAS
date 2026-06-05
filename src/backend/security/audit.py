from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def append_audit_event(path: str | Path, event: dict[str, Any]) -> dict[str, Any]:
    """Append one audit event as JSONL.

    以 JSONL 追加一条审计事件。
    """
    audit_path = Path(path).expanduser()
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "safety": {"live_trading_enabled": False},
        **event,
    }
    audit_path.write_text(
        audit_path.read_text(encoding="utf-8") if audit_path.exists() else "",
        encoding="utf-8",
    )
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload
