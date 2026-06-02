"""Alpha Vantage OHLCV fetcher."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Sequence

import pandas as pd

from quant_mas.data.fetchers.base import MarketDataFetcher, normalize_symbols, resolve_env_value
from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv


def resolve_alpha_vantage_api_key(explicit: str | None = None) -> str:
    return resolve_env_value(
        explicit,
        "ALPHAVANTAGE_API_KEY",
        service_name="Alpha Vantage",
        cli_hint="--api-key",
    )


class AlphaVantageFetcher(MarketDataFetcher):
    """Fetch daily OHLCV from Alpha Vantage TIME_SERIES_DAILY."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        request_timeout_seconds: float = 60.0,
        delay_between_symbols_seconds: float = 12.0,
    ) -> None:
        self.api_key = resolve_alpha_vantage_api_key(api_key)
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
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "full",
                "apikey": self.api_key,
            }
        )
        url = f"https://www.alphavantage.co/query?{params}"
        with urllib.request.urlopen(url, timeout=self.request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return _parse_alpha_vantage_daily(payload, symbol, start, end)


def _parse_alpha_vantage_daily(
    payload: dict,
    symbol: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    series = payload.get("Time Series (Daily)") or payload.get("Time Series (Daily Adjusted)")
    if not isinstance(series, dict):
        message = payload.get("Note") or payload.get("Error Message") or "missing daily time series"
        raise ValueError(f"Alpha Vantage response error for {symbol}: {message}")
    rows = []
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    for date_text, values in series.items():
        date = pd.Timestamp(date_text)
        if not start_ts <= date <= end_ts:
            continue
        rows.append(
            {
                "date": date,
                "symbol": symbol,
                "open": values["1. open"],
                "high": values["2. high"],
                "low": values["3. low"],
                "close": values["4. close"],
                "volume": values["5. volume"],
            }
        )
    if not rows:
        raise ValueError(f"Alpha Vantage returned no rows for {symbol}")
    return pd.DataFrame(rows).loc[:, OHLCV_COLUMNS]
