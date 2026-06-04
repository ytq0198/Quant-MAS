"""Real financial-news ingestion and trading-day alignment helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.text.data_schema import FinancialTextRecord


@dataclass(frozen=True)
class RealNewsRecord:
    """One raw news item with a publication timestamp."""

    published_at: str
    symbol: str
    source: str
    title: str
    text: str = ""
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RealNewsRecord":
        title = str(payload.get("title", "")).strip()
        text = str(payload.get("text", "")).strip()
        if not title and not text:
            raise ValueError("real news record requires title or text")
        return cls(
            published_at=str(payload["published_at"]),
            symbol=str(payload["symbol"]).upper(),
            source=str(payload.get("source", "unknown")),
            title=title,
            text=text,
            url=str(payload["url"]) if payload.get("url") else None,
            metadata=dict(payload.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "published_at": self.published_at,
            "symbol": self.symbol,
            "source": self.source,
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "metadata": dict(self.metadata),
        }


def load_real_news_records(path: str | Path) -> list[RealNewsRecord]:
    """Load real news records from JSONL or parquet without network access."""
    source = Path(path).expanduser()
    if source.suffix.lower() == ".jsonl":
        records = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(RealNewsRecord.from_dict(json.loads(line)))
        return records
    if source.suffix.lower() == ".parquet":
        frame = pd.read_parquet(source)
        return [RealNewsRecord.from_dict(row) for row in frame.to_dict(orient="records")]
    raise ValueError("Real news path must be .jsonl or .parquet")


def align_real_news_to_features(
    records: list[RealNewsRecord],
    features: pd.DataFrame,
    *,
    market_close: str = "16:00",
    date_col: str = "date",
    symbol_col: str = "symbol",
) -> tuple[list[FinancialTextRecord], dict[str, Any]]:
    """Align timestamped news to available feature bars.

    News published after market close is assigned to the next available feature
    date for the same symbol. News without a future tradable bar is dropped and
    counted in the returned audit summary.
    """
    _require_feature_calendar(features, date_col=date_col, symbol_col=symbol_col)
    close_time = _parse_market_close(market_close)
    calendar = _calendar_by_symbol(features, date_col=date_col, symbol_col=symbol_col)

    aligned: list[FinancialTextRecord] = []
    dropped = 0
    dropped_reasons: dict[str, int] = {}
    for record in records:
        symbol = record.symbol.upper()
        if symbol not in calendar:
            dropped += 1
            dropped_reasons["unknown_symbol"] = dropped_reasons.get("unknown_symbol", 0) + 1
            continue
        published = _parse_timestamp(record.published_at)
        target_day = published.date()
        if published.time() > close_time:
            target_day = target_day + pd.Timedelta(days=1)
        aligned_day = _next_available_day(calendar[symbol], pd.Timestamp(target_day))
        if aligned_day is None:
            dropped += 1
            dropped_reasons["no_future_bar"] = dropped_reasons.get("no_future_bar", 0) + 1
            continue
        aligned.append(
            FinancialTextRecord(
                date=aligned_day.date().isoformat(),
                symbol=symbol,
                source=record.source,
                text=_combined_text(record),
                metadata={
                    **record.metadata,
                    "published_at": record.published_at,
                    "title": record.title,
                    "url": record.url,
                    "aligned_from": "real_news",
                    "market_close": market_close,
                },
            )
        )

    audit = {
        "input_records": len(records),
        "aligned_records": len(aligned),
        "dropped_records": dropped,
        "dropped_reasons": dropped_reasons,
        "market_close": market_close,
        "feature_symbols": sorted(calendar),
    }
    return aligned, audit


def write_real_news_alignment_report(
    records: list[FinancialTextRecord],
    audit: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, str]:
    """Write aligned news JSONL plus audit files."""
    destination = Path(output_dir).expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    jsonl_path = destination / "aligned_news.jsonl"
    metrics_path = destination / "alignment_metrics.json"
    summary_path = destination / "summary.md"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    metrics_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(_summary_markdown(audit), encoding="utf-8")
    return {
        "aligned_news": str(jsonl_path),
        "metrics": str(metrics_path),
        "summary": str(summary_path),
    }


def _calendar_by_symbol(
    features: pd.DataFrame,
    *,
    date_col: str,
    symbol_col: str,
) -> dict[str, pd.DatetimeIndex]:
    frame = features[[date_col, symbol_col]].copy()
    frame[date_col] = pd.to_datetime(frame[date_col]).dt.normalize()
    frame[symbol_col] = frame[symbol_col].astype(str).str.upper()
    return {
        str(symbol): pd.DatetimeIndex(sorted(group[date_col].dropna().unique()))
        for symbol, group in frame.groupby(symbol_col)
    }


def _next_available_day(days: pd.DatetimeIndex, target: pd.Timestamp) -> pd.Timestamp | None:
    normalized = target.normalize()
    candidates = days[days >= normalized]
    if candidates.empty:
        return None
    return pd.Timestamp(candidates[0])


def _combined_text(record: RealNewsRecord) -> str:
    if record.title and record.text:
        return f"{record.title}\n\n{record.text}"
    return record.title or record.text


def _parse_market_close(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("market_close must use HH:MM or HH:MM:SS format") from exc


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid published_at timestamp: {value}") from exc
    return parsed.replace(tzinfo=None)


def _require_feature_calendar(
    features: pd.DataFrame,
    *,
    date_col: str,
    symbol_col: str,
) -> None:
    missing = [column for column in (date_col, symbol_col) if column not in features.columns]
    if missing:
        raise ValueError(f"features missing required columns: {missing}")
    if features.empty:
        raise ValueError("features frame is empty")


def _summary_markdown(audit: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Real News Alignment Audit",
            "",
            f"- input_records: {audit['input_records']}",
            f"- aligned_records: {audit['aligned_records']}",
            f"- dropped_records: {audit['dropped_records']}",
            f"- market_close: {audit['market_close']}",
            f"- dropped_reasons: {audit['dropped_reasons']}",
            "",
            "This alignment report is not an OOS result. It only documents news-to-bar availability.",
            "",
        ]
    )
