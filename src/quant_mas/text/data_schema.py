"""Schemas for financial text records and derived text signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class FinancialTextRecord:
    """One text item available as of its publication/as-of date."""

    date: date | str
    symbol: str
    source: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["date"] = _date_to_str(self.date)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FinancialTextRecord":
        return cls(
            date=str(payload["date"]),
            symbol=str(payload["symbol"]),
            source=str(payload.get("source", "unknown")),
            text=str(payload.get("text", "")),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class TextSignalRecord:
    """One numeric text-derived feature value."""

    date: date | str
    symbol: str
    signal_name: str
    value: float
    model_id: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["date"] = _date_to_str(self.date)
        payload["value"] = float(self.value)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TextSignalRecord":
        return cls(
            date=str(payload["date"]),
            symbol=str(payload["symbol"]),
            signal_name=str(payload["signal_name"]),
            value=float(payload["value"]),
            model_id=str(payload.get("model_id", "")),
        )


def _date_to_str(value: date | str) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def parse_record_date(value: date | str) -> date:
    """Parse text record dates consistently."""
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(str(value)).date()
