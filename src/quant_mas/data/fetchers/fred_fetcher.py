"""FRED macroeconomic series fetcher."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

import pandas as pd

from quant_mas.data.fetchers.base import resolve_env_value


def resolve_fred_api_key(explicit: str | None = None) -> str:
    return resolve_env_value(
        explicit,
        "FRED_API_KEY",
        service_name="FRED",
        cli_hint="--api-key",
    )


class FREDFetcher:
    """Fetch macro series from FRED as date, series_id, value rows."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        request_timeout_seconds: float = 60.0,
    ) -> None:
        self.api_key = resolve_fred_api_key(api_key)
        self.request_timeout_seconds = request_timeout_seconds

    def fetch_series(self, series_id: str, start: str, end: str) -> pd.DataFrame:
        if not series_id:
            raise ValueError("series_id is required for FRED")
        params = urllib.parse.urlencode(
            {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start,
                "observation_end": end,
            }
        )
        url = f"https://api.stlouisfed.org/fred/series/observations?{params}"
        with urllib.request.urlopen(url, timeout=self.request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        observations = payload.get("observations", [])
        rows = []
        for item in observations:
            value = item.get("value")
            rows.append(
                {
                    "date": pd.to_datetime(item["date"]),
                    "series_id": series_id,
                    "value": None if value == "." else float(value),
                    "realtime_start": item.get("realtime_start"),
                    "realtime_end": item.get("realtime_end"),
                }
            )
        return pd.DataFrame(rows, columns=["date", "series_id", "value", "realtime_start", "realtime_end"])
