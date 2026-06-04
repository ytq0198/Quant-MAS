"""Fetch company news from Finnhub for real-news text experiments."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path

from quant_mas.data.fetchers.finnhub_fetcher import resolve_finnhub_api_key
from quant_mas.text.real_news import RealNewsRecord


def fetch_finnhub_company_news_records(
    symbols: Sequence[str],
    *,
    start: str,
    end: str,
    api_key: str | None = None,
    chunk_months: int = 1,
    delay_seconds: float = 1.0,
    request_timeout_seconds: float = 60.0,
    progress: bool = False,
) -> list[RealNewsRecord]:
    """Download Finnhub company news for each symbol between start and end."""
    if chunk_months < 1:
        raise ValueError("chunk_months must be >= 1")
    token = resolve_finnhub_api_key(api_key)
    normalized = [symbol.upper() for symbol in symbols]
    if not normalized:
        raise ValueError("At least one symbol is required")

    chunks = iter_date_chunks(start, end, chunk_months=chunk_months)
    total_requests = len(normalized) * len(chunks)
    if progress:
        _log_progress(
            f"starting Finnhub download: symbols={normalized} "
            f"requests={total_requests} delay={delay_seconds}s"
        )

    records: list[RealNewsRecord] = []
    seen: set[tuple[str, int | str, ...]] = set()
    request_index = 0
    consecutive_empty = 0
    for index, symbol in enumerate(normalized):
        if index > 0 and delay_seconds > 0:
            time.sleep(delay_seconds)
        for chunk_start, chunk_end in chunks:
            request_index += 1
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            if progress:
                _log_progress(
                    f"request {request_index}/{total_requests}: "
                    f"{symbol} {chunk_start}..{chunk_end} ..."
                )
            payload = _request_company_news(
                symbol=symbol,
                start=chunk_start,
                end=chunk_end,
                api_key=token,
                request_timeout_seconds=request_timeout_seconds,
            )
            chunk_added = 0
            for item in payload:
                record = parse_finnhub_news_item(item, symbol=symbol)
                news_id = item.get("id")
                key = (
                    (record.symbol, int(news_id))
                    if news_id is not None
                    else (record.symbol, record.published_at, record.title)
                )
                if key in seen:
                    continue
                seen.add(key)
                records.append(record)
                chunk_added += 1
            if progress:
                _log_progress(
                    f"request {request_index}/{total_requests}: "
                    f"{symbol} {chunk_start}..{chunk_end} -> "
                    f"raw={len(payload)} +{chunk_added} (total {len(records)})"
                )
            if len(payload) == 0:
                consecutive_empty += 1
                if progress and consecutive_empty == 12:
                    _log_progress(
                        "warning: 12 consecutive empty API responses. "
                        "Finnhub free tier company-news is typically limited to "
                        "the most recent 1 year. Stop (Ctrl+C) and rerun with a "
                        "recent --start date, e.g. last 365 days."
                    )
            else:
                consecutive_empty = 0

    records.sort(key=lambda record: (record.symbol, record.published_at))
    if progress:
        _log_progress(f"download complete: {len(records)} unique records")
    return records


def parse_finnhub_news_item(item: dict, *, symbol: str) -> RealNewsRecord:
    """Convert one Finnhub company-news payload item to RealNewsRecord."""
    headline = str(item.get("headline", "")).strip()
    summary = str(item.get("summary", "")).strip()
    if not headline and not summary:
        raise ValueError("Finnhub news item missing headline and summary")
    published_at = _format_finnhub_datetime(item.get("datetime"))
    source_name = str(item.get("source", "finnhub")).strip() or "finnhub"
    return RealNewsRecord(
        published_at=published_at,
        symbol=symbol.upper(),
        source=f"finnhub:{source_name}",
        title=headline,
        text=summary,
        url=str(item["url"]) if item.get("url") else None,
        metadata={
            "provider": "finnhub",
            "category": item.get("category"),
            "finnhub_id": item.get("id"),
            "related": item.get("related"),
        },
    )


def write_real_news_jsonl(records: list[RealNewsRecord], path: str | Path) -> Path:
    """Write RealNewsRecord rows as JSONL."""
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    return output


def iter_date_chunks(start: str, end: str, *, chunk_months: int) -> list[tuple[str, str]]:
    """Split [start, end] into inclusive YYYY-MM-DD windows."""
    start_ts = datetime.strptime(start, "%Y-%m-%d")
    end_ts = datetime.strptime(end, "%Y-%m-%d")
    if start_ts > end_ts:
        raise ValueError("start must be on or before end")

    chunks: list[tuple[str, str]] = []
    cursor = start_ts
    while cursor <= end_ts:
        month_index = cursor.month - 1 + chunk_months
        year = cursor.year + month_index // 12
        month = month_index % 12 + 1
        next_start = datetime(year, month, 1)
        chunk_end = min(end_ts, next_start - timedelta(days=1))
        chunks.append((cursor.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        cursor = chunk_end + timedelta(days=1)
    return chunks


def _request_company_news(
    *,
    symbol: str,
    start: str,
    end: str,
    api_key: str,
    request_timeout_seconds: float,
) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "symbol": symbol,
            "from": start,
            "to": end,
            "token": api_key,
        }
    )
    url = f"https://finnhub.io/api/v1/company-news?{params}"
    try:
        with urllib.request.urlopen(url, timeout=request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"Finnhub company-news HTTP {exc.code} for {symbol} {start}..{end}: {body}"
        ) from exc
    if not isinstance(payload, list):
        raise ValueError(f"Unexpected Finnhub company-news payload for {symbol}: {payload!r}")
    return payload


def _log_progress(message: str) -> None:
    print(f"[fetch-real-news] {message}", file=sys.stderr, flush=True)


def _format_finnhub_datetime(value: object) -> str:
    if value is None:
        raise ValueError("Finnhub news item missing datetime")
    timestamp = int(value)
    return datetime.fromtimestamp(timestamp, timezone.utc).replace(tzinfo=None).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
