"""Append-only JSONL trade memory."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TradeRecord:
    """Serializable trade record for future paper-trading audit."""

    trade_id: str
    timestamp: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)


class TradeMemory:
    """Append-only JSONL trade log (stub for future paper trading)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def append(self, record: TradeRecord) -> TradeRecord:
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record.__dict__, ensure_ascii=False) + "\n")
        return record

    def list(self, limit: int | None = None) -> list[TradeRecord]:
        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative")
        records = [
            TradeRecord(**json.loads(line))
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if limit is None:
            return records
        return records[-limit:]

    def latest(self) -> TradeRecord:
        records = self.list()
        if not records:
            raise ValueError("No trades recorded")
        return records[-1]
