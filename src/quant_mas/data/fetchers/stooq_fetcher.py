"""Stooq OHLCV fetcher."""

from __future__ import annotations

import io
import time
import urllib.error
import urllib.request
from collections.abc import Sequence

import pandas as pd

from quant_mas.data.fetchers.base import MarketDataFetcher, normalize_symbols, resolve_env_value, to_yyyymmdd
from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv

STOOQ_SYMBOL_SUFFIX = ".us"
STOOQ_USER_AGENT = "Mozilla/5.0 (compatible; QuantMAS/1.0)"
STOOQ_API_KEY_URL = "https://stooq.com/q/d/?s=aapl.us&get_apikey"


def resolve_stooq_api_key(explicit: str | None = None) -> str:
    """Return Stooq API key from CLI arg or ``STOOQ_API_KEY`` env var."""
    try:
        return resolve_env_value(
            explicit,
            "STOOQ_API_KEY",
            service_name="Stooq",
            cli_hint="--stooq-api-key",
        )
    except ValueError as exc:
        raise ValueError(
            "Stooq requires an API key. Set STOOQ_API_KEY in .env or pass "
            f"--stooq-api-key. Get one at {STOOQ_API_KEY_URL}"
        ) from exc


def _parse_stooq_csv_payload(payload: bytes, symbol: str) -> pd.DataFrame:
    if not payload.strip():
        raise ValueError(f"empty Stooq response for {symbol}")
    preview = payload[:400].decode("utf-8", errors="replace")
    lowered = preview.lower()
    if "get your apikey" in lowered or (
        "apikey" in lowered and not preview.lstrip().startswith("Date,")
    ):
        raise ValueError(
            "Stooq returned API-key instructions instead of CSV. "
            f"Set STOOQ_API_KEY (see {STOOQ_API_KEY_URL})."
        )
    if not preview.lstrip().startswith("Date,"):
        raise ValueError(f"unexpected Stooq response for {symbol}: {preview[:120]!r}")
    frame = pd.read_csv(io.BytesIO(payload))
    if frame.empty:
        raise ValueError(f"empty Stooq CSV for {symbol}")
    renamed = frame.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    renamed["symbol"] = symbol
    renamed["date"] = pd.to_datetime(renamed["date"])
    return renamed.loc[:, OHLCV_COLUMNS]


class StooqFetcher(MarketDataFetcher):
    """Fetch daily OHLCV from Stooq CSV export."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        delay_between_symbols_seconds: float = 3.0,
        request_timeout_seconds: float = 60.0,
    ) -> None:
        self.api_key = resolve_stooq_api_key(api_key)
        self.delay_between_symbols_seconds = delay_between_symbols_seconds
        self.request_timeout_seconds = request_timeout_seconds

    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        normalized_symbols = normalize_symbols(symbols)
        frames: list[pd.DataFrame] = []
        failures: list[str] = []
        d1 = to_yyyymmdd(start)
        d2 = to_yyyymmdd(end)
        for index, symbol in enumerate(normalized_symbols):
            if index > 0 and self.delay_between_symbols_seconds > 0:
                time.sleep(self.delay_between_symbols_seconds)
            try:
                frames.append(self._download_symbol(symbol, d1, d2))
                print(f"[download] OK {symbol} {start} -> {end} (stooq)")
            except Exception as exc:
                failures.append(f"{symbol}: {exc}")
                print(f"[download] FAIL {symbol}: {exc}")
        if not frames:
            detail = "; ".join(failures) if failures else "no symbols succeeded"
            raise ValueError(f"No market data returned by Stooq. {detail}")
        if failures:
            print(f"[download] warning: skipped failed symbols: {', '.join(failures)}")
        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    @staticmethod
    def _stooq_ticker(symbol: str) -> str:
        return f"{symbol.lower()}{STOOQ_SYMBOL_SUFFIX}"

    def _download_symbol(self, symbol: str, d1: str, d2: str) -> pd.DataFrame:
        url = (
            f"https://stooq.com/q/d/l/?s={self._stooq_ticker(symbol)}&d1={d1}&d2={d2}"
            f"&i=d&apikey={self.api_key}"
        )
        request = urllib.request.Request(url, headers={"User-Agent": STOOQ_USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=self.request_timeout_seconds) as response:
                payload = response.read()
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Stooq request failed for {symbol}: {exc}") from exc
        return _parse_stooq_csv_payload(payload, symbol)
