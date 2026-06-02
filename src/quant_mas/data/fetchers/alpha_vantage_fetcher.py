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
    """Fetch daily OHLCV from Alpha Vantage TIME_SERIES_DAILY.

    Free tier notes:
    - ``compact`` returns only the latest ~100 trading days.
    - ``full`` may require premium or hit rate limits on some keys.
    - Default ``outputsize=auto`` tries ``full`` then ``compact``.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        outputsize: str = "auto",
        request_timeout_seconds: float = 60.0,
        delay_between_symbols_seconds: float = 12.0,
    ) -> None:
        self.api_key = resolve_alpha_vantage_api_key(api_key)
        self.outputsize = outputsize
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
        sizes = _resolve_outputsize_attempts(self.outputsize)
        errors: list[str] = []
        last_available: tuple[pd.Timestamp, pd.Timestamp] | None = None

        for outputsize in sizes:
            try:
                payload = self._fetch_payload(symbol, outputsize)
                frame, available = _parse_alpha_vantage_daily(
                    payload, symbol, start, end, outputsize=outputsize
                )
                if not frame.empty:
                    return frame
                if available is not None:
                    last_available = available
                errors.append(
                    f"{outputsize}: no rows in requested range {start}..{end}"
                )
            except ValueError as exc:
                errors.append(f"{outputsize}: {exc}")

        hint = (
            "Alpha Vantage free tier compact covers ~100 recent trading days only. "
            "For older history use --source stooq, or request a recent date window."
        )
        if last_available is not None:
            min_d, max_d = last_available
            hint = (
                f"Latest response covered {min_d.date()}..{max_d.date()}. "
                + hint
            )
        detail = "; ".join(errors) if errors else "no successful response"
        raise ValueError(f"Alpha Vantage returned no rows for {symbol}. {detail}. {hint}")

    def _fetch_payload(self, symbol: str, outputsize: str) -> dict:
        params = urllib.parse.urlencode(
            {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": outputsize,
                "apikey": self.api_key,
            }
        )
        url = f"https://www.alphavantage.co/query?{params}"
        with urllib.request.urlopen(url, timeout=self.request_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


def _resolve_outputsize_attempts(outputsize: str) -> tuple[str, ...]:
    normalized = outputsize.lower().strip()
    if normalized == "auto":
        return ("full", "compact")
    if normalized in {"full", "compact"}:
        return (normalized,)
    raise ValueError(f"Unsupported Alpha Vantage outputsize: {outputsize}")


def _extract_daily_series(payload: dict, symbol: str) -> dict:
    series = payload.get("Time Series (Daily)") or payload.get("Time Series (Daily Adjusted)")
    if not isinstance(series, dict):
        message = (
            payload.get("Note")
            or payload.get("Error Message")
            or payload.get("Information")
            or "missing daily time series"
        )
        raise ValueError(message)
    return series


def _parse_alpha_vantage_daily(
    payload: dict,
    symbol: str,
    start: str,
    end: str,
    *,
    outputsize: str = "compact",
) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp] | None]:
    series = _extract_daily_series(payload, symbol)
    rows = []
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    all_dates = sorted(pd.Timestamp(date_text) for date_text in series)
    available = (all_dates[0], all_dates[-1]) if all_dates else None

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
        return pd.DataFrame(columns=OHLCV_COLUMNS), available
    return pd.DataFrame(rows).loc[:, OHLCV_COLUMNS], available
