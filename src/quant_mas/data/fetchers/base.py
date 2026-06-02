"""Fetcher base classes and shared helpers."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Any

import pandas as pd


class MarketDataFetcher(ABC):
    """Abstract interface for OHLCV market data fetchers."""

    @abstractmethod
    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        """Fetch OHLCV data for symbols between start and end dates."""


def normalize_symbols(symbols: Sequence[str]) -> list[str]:
    normalized = [symbol.upper() for symbol in symbols]
    if not normalized:
        raise ValueError("At least one symbol is required")
    return normalized


def to_yyyymmdd(date_text: str) -> str:
    return datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y%m%d")


def to_unix_seconds(date_text: str) -> int:
    return int(datetime.strptime(date_text, "%Y-%m-%d").timestamp())


def resolve_env_value(
    explicit: str | None,
    env_name: str,
    *,
    service_name: str,
    cli_hint: str | None = None,
) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    env_value = os.environ.get(env_name, "").strip()
    if env_value:
        return env_value
    hint = f" or pass {cli_hint}" if cli_hint else ""
    raise ValueError(
        f"{service_name} requires an API key or user-agent. "
        f"Set {env_name} in .env{hint}."
    )


def json_records_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame.from_records(records)
