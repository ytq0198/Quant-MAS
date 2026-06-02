"""Finnhub OHLCV fetcher."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Sequence

import pandas as pd

from quant_mas.data.fetchers.base import (
    MarketDataFetcher,
    normalize_symbols,
    resolve_env_value,
    to_unix_seconds,
)
from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv


def resolve_finnhub_api_key(explicit: str | None = None) -> str:
    return resolve_env_value(
        explicit,
        "FINNHUB_API_KEY",
        service_name="Finnhub",
        cli_hint="--api-key",
    )


class FinnhubFetcher(MarketDataFetcher):
    """Fetch daily OHLCV from Finnhub `/stock/candle`."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        request_timeout_seconds: float = 60.0,
        delay_between_symbols_seconds: float = 1.0,
    ) -> None:
        self.api_key = resolve_finnhub_api_key(api_key)
        self.request_timeout_seconds = request_timeout_seconds
        self.delay_between_symbols_seconds = delay_between_symbols_seconds

    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        frames = []
        for index, symbol in enumerate(normalize_symbols(symbols)):
            if index > 0 and self.delay_between_symbols_seconds > 0:
                time.sleep(self.delay_between_symbols_seconds)
            frames.append(self._download_symbol(symbol, start, end))
        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    def _download_symbol(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        params = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "resolution": "D",
                "from": to_unix_seconds(start),
                "to": to_unix_seconds(end),
                "token": self.api_key,
            }
        )
        url = f"https://finnhub.io/api/v1/stock/candle?{params}"
        with urllib.request.urlopen(url, timeout=self.request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return _parse_finnhub_candle(payload, symbol)


def _parse_finnhub_candle(payload: dict, symbol: str) -> pd.DataFrame:
    if payload.get("s") != "ok":
        raise ValueError(f"Finnhub response error for {symbol}: {payload.get('s')}")
    rows = []
    for timestamp, open_, high, low, close, volume in zip(
        payload.get("t", []),
        payload.get("o", []),
        payload.get("h", []),
        payload.get("l", []),
        payload.get("c", []),
        payload.get("v", []),
        strict=True,
    ):
        rows.append(
            {
                "date": pd.to_datetime(timestamp, unit="s"),
                "symbol": symbol,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
    if not rows:
        raise ValueError(f"Finnhub returned no rows for {symbol}")
    return pd.DataFrame(rows).loc[:, OHLCV_COLUMNS]
