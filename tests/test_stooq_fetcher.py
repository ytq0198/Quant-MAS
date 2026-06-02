from __future__ import annotations

import io

import pytest

from quant_mas.data.fetchers import (
    AutoMarketDataFetcher,
    StooqFetcher,
    YFinanceFetcher,
    _parse_stooq_csv_payload,
    resolve_stooq_api_key,
)


def _stooq_csv() -> bytes:
    content = "Date,Open,High,Low,Close,Volume\n2026-01-02,10.0,11.0,9.0,10.5,1000\n"
    return content.encode()


def test_resolve_stooq_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STOOQ_API_KEY", "abc123")
    assert resolve_stooq_api_key() == "abc123"
    assert resolve_stooq_api_key("override") == "override"


def test_resolve_stooq_api_key_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STOOQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="STOOQ_API_KEY"):
        resolve_stooq_api_key()


def test_parse_stooq_csv_payload_rejects_apikey_page() -> None:
    payload = b"Get your apikey:\n1. Open https://stooq.com/q/d/?s=aapl.us&get_apikey\n"
    with pytest.raises(ValueError, match="API-key instructions"):
        _parse_stooq_csv_payload(payload, "AAPL")


def test_stooq_fetcher_parses_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def __init__(self, payload: bytes) -> None:
            self._payload = payload

        def read(self) -> bytes:
            return self._payload

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    def fake_urlopen(request, timeout: float = 60.0) -> FakeResponse:
        assert "apikey=test-key" in request.full_url
        return FakeResponse(_stooq_csv())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = StooqFetcher(api_key="test-key", delay_between_symbols_seconds=0).fetch(
        ["AAPL"], "2026-01-01", "2026-01-03"
    )

    assert len(result) == 1
    assert result.loc[0, "symbol"] == "AAPL"
    assert float(result.loc[0, "close"]) == 10.5


def test_auto_fetcher_falls_back_to_stooq(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_yfinance(self, symbols, start, end):  # noqa: ANN001
        raise ValueError("No market data returned by yfinance. rate limit")

    class FakeResponse:
        def read(self) -> bytes:
            return _stooq_csv()

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    monkeypatch.setattr(YFinanceFetcher, "fetch", fail_yfinance)
    monkeypatch.setattr("urllib.request.urlopen", lambda request, timeout=60.0: FakeResponse())

    result = AutoMarketDataFetcher(stooq_api_key="test-key").fetch(
        ["MSFT"], "2026-01-01", "2026-01-03"
    )

    assert len(result) == 1
    assert result.loc[0, "symbol"] == "MSFT"


def test_yfinance_rate_limit_backoff_caps_wait() -> None:
    fetcher = YFinanceFetcher(
        rate_limit_backoff_seconds=120.0,
        max_rate_limit_wait_seconds=900.0,
    )
    assert fetcher._retry_wait_seconds(1, RuntimeError("YFRateLimitError")) == 120.0
    assert fetcher._retry_wait_seconds(4, RuntimeError("Too Many Requests")) == 900.0
