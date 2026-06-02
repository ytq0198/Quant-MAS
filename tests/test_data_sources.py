from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

from quant_mas.data.fetchers import (
    AlphaVantageFetcher,
    DataSourceRegistry,
    FinnhubFetcher,
    FREDFetcher,
    SECEDGARFetcher,
    create_market_data_fetcher,
    default_data_source_registry,
    resolve_alpha_vantage_api_key,
    resolve_finnhub_api_key,
    resolve_fred_api_key,
    resolve_sec_edgar_user_agent,
)
from scripts import download_data


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self.payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


@pytest.mark.parametrize(
    ("resolver", "env_name"),
    [
        (resolve_alpha_vantage_api_key, "ALPHAVANTAGE_API_KEY"),
        (resolve_finnhub_api_key, "FINNHUB_API_KEY"),
        (resolve_fred_api_key, "FRED_API_KEY"),
        (resolve_sec_edgar_user_agent, "SEC_EDGAR_USER_AGENT"),
    ],
)
def test_resolve_new_data_source_secrets_missing_raises(
    resolver,
    env_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(env_name, raising=False)

    with pytest.raises(ValueError, match=env_name):
        resolver()


def test_alpha_vantage_fetcher_parses_daily_ohlcv(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "Time Series (Daily)": {
            "2026-01-02": {
                "1. open": "10.0",
                "2. high": "11.0",
                "3. low": "9.0",
                "4. close": "10.5",
                "5. volume": "1000",
            }
        }
    }

    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout=60.0: FakeResponse(payload))

    result = AlphaVantageFetcher(api_key="key", delay_between_symbols_seconds=0).fetch(
        ["AAPL"], "2026-01-01", "2026-01-03"
    )

    assert list(result.columns) == ["date", "symbol", "open", "high", "low", "close", "volume"]
    assert result.loc[0, "symbol"] == "AAPL"
    assert float(result.loc[0, "close"]) == 10.5


def test_alpha_vantage_auto_reports_available_range_when_filter_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "Time Series (Daily)": {
            "2026-05-01": {
                "1. open": "10.0",
                "2. high": "11.0",
                "3. low": "9.0",
                "4. close": "10.5",
                "5. volume": "1000",
            }
        }
    }
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda url, timeout=60.0: FakeResponse(payload),
    )

    with pytest.raises(ValueError, match="2026-05-01"):
        AlphaVantageFetcher(
            api_key="key", outputsize="compact", delay_between_symbols_seconds=0
        ).fetch(["AAPL"], "2024-01-01", "2024-06-01")


def test_finnhub_fetcher_parses_candle_ohlcv(monkeypatch: pytest.MonkeyPatch) -> None:
    timestamp = int(pd.Timestamp("2026-01-02").timestamp())
    payload = {
        "s": "ok",
        "t": [timestamp],
        "o": [10.0],
        "h": [11.0],
        "l": [9.0],
        "c": [10.5],
        "v": [1000],
    }
    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout=60.0: FakeResponse(payload))

    result = FinnhubFetcher(api_key="key", delay_between_symbols_seconds=0).fetch(
        ["MSFT"], "2026-01-01", "2026-01-03"
    )

    assert result.loc[0, "symbol"] == "MSFT"
    assert float(result.loc[0, "high"]) == 11.0


def test_fred_fetcher_parses_series(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "observations": [
            {
                "realtime_start": "2026-01-01",
                "realtime_end": "2026-01-01",
                "date": "2026-01-02",
                "value": "4.25",
            }
        ]
    }
    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout=60.0: FakeResponse(payload))

    result = FREDFetcher(api_key="key").fetch_series("DGS10", "2026-01-01", "2026-01-03")

    assert list(result.columns) == ["date", "series_id", "value", "realtime_start", "realtime_end"]
    assert result.loc[0, "series_id"] == "DGS10"
    assert result.loc[0, "value"] == 4.25


def test_sec_edgar_fetcher_parses_json_and_sets_user_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = {}

    def fake_urlopen(request, timeout=60.0):
        seen["user_agent"] = request.get_header("User-agent")
        seen["url"] = request.full_url
        return FakeResponse({"cik": "0000320193", "name": "Apple"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = SECEDGARFetcher(user_agent="Quant MAS test@example.com").fetch_submissions(
        "0000320193"
    )

    assert result["name"] == "Apple"
    assert seen["user_agent"] == "Quant MAS test@example.com"
    assert "CIK0000320193.json" in seen["url"]


def test_data_source_registry_create_fetcher(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "fred-key")
    registry = default_data_source_registry()

    assert set(registry.names()) >= {"yfinance", "stooq", "auto", "alpha_vantage", "finnhub", "fred", "sec_edgar"}
    assert registry.get("fred").kind == "macro"
    assert isinstance(registry.create_fetcher("fred"), FREDFetcher)
    assert isinstance(create_market_data_fetcher("alpha_vantage", api_key="key"), AlphaVantageFetcher)
    with pytest.raises(ValueError, match="Available sources"):
        registry.create_fetcher("missing")


def test_data_source_registry_custom_registration() -> None:
    registry = DataSourceRegistry()
    registry.register("custom", "macro", lambda: "fetcher")

    assert registry.create_fetcher("custom") == "fetcher"
    assert registry.get("custom").kind == "macro"


def test_download_data_cli_fred_missing_series_exits_nonzero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["download_data.py", "--source", "fred", "--storage-config", "configs/storage.yaml"],
    )
    monkeypatch.setenv("FRED_API_KEY", "key")

    assert download_data.main() == 1


def test_download_data_cli_sec_missing_cik_exits_nonzero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["download_data.py", "--source", "sec_edgar", "--storage-config", "configs/storage.yaml"],
    )
    monkeypatch.setenv("SEC_EDGAR_USER_AGENT", "Quant MAS test@example.com")

    assert download_data.main() == 1
