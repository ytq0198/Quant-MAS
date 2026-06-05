from __future__ import annotations

import os
from typing import Any


_SECRET_KEYS = {
    "QUANT_MAS_API_KEYS",
    "LLM_API_KEY",
    "VLLM_API_KEY",
    "FINNHUB_API_KEY",
    "ALPHAVANTAGE_API_KEY",
    "FRED_API_KEY",
    "HF_TOKEN",
    "POSTGRES_DSN",
    "PGVECTOR_DSN",
    "NEO4J_PASSWORD",
}


def get_effective_config() -> dict[str, Any]:
    """Return redacted effective backend config.

    返回脱敏后的后端有效配置。
    """
    keys = [
        "QUANT_MAS_ENV",
        "QUANT_MAS_AUTH_MODE",
        "QUANT_MAS_API_KEYS",
        "QUANT_MAS_ARTIFACT_ROOT",
        "QUANT_MAS_STORAGE_MODE",
        "VECTOR_STORE",
        "POSTGRES_DSN",
        "PGVECTOR_DSN",
        "NEO4J_URI",
        "NEO4J_PASSWORD",
        "LLM_PROVIDER",
        "LLM_API_KEY",
    ]
    values = {key: _redact(key, os.getenv(key, "")) for key in keys}
    return {
        "source": "server_config",
        "auth_mode": os.getenv("QUANT_MAS_AUTH_MODE", "open"),
        "storage_mode": os.getenv("QUANT_MAS_STORAGE_MODE", "local_files"),
        "vector_store": os.getenv("VECTOR_STORE", "in_memory"),
        "live_trading_enabled": False,
        "env": values,
        "values": values,
    }


def _redact(key: str, value: str) -> str:
    if not value:
        return ""
    if key in _SECRET_KEYS or "KEY" in key or "TOKEN" in key or "PASSWORD" in key:
        return "***redacted***"
    return value
