"""Memory store factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from quant_mas.memory.json_store import JsonMemoryStore
from quant_mas.memory.sqlite_store import SqliteMemoryStore
from quant_mas.memory.store_base import MemoryStore


def create_memory_store(
    backend: str = "json",
    **kwargs: Any,
) -> MemoryStore:
    """Create a memory store backend."""
    normalized = backend.lower().strip()
    if normalized == "json":
        path = kwargs.get("json_path") or kwargs.get("path")
        if path is None:
            raise ValueError("json backend requires json_path or path")
        return JsonMemoryStore(path)
    if normalized == "sqlite":
        path = kwargs.get("sqlite_path") or kwargs.get("path")
        if path is None:
            raise ValueError("sqlite backend requires sqlite_path or path")
        return SqliteMemoryStore(path)
    raise ValueError("Unknown memory backend: " f"{backend}. Use json or sqlite.")


def create_memory_store_from_yaml(path: str | Path) -> MemoryStore:
    """Create a memory store from configs/memory.yaml style config."""
    config_path = Path(path).expanduser()
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    backend = config.get("memory_backend", "json")
    return create_memory_store(
        backend,
        json_path=_resolve_optional(config.get("json_path"), config_path),
        sqlite_path=_resolve_optional(config.get("sqlite_path"), config_path),
    )


def _resolve_optional(value: str | None, config_path: Path) -> Path | None:
    if value is None:
        return None
    result = Path(value).expanduser()
    if not result.is_absolute():
        result = config_path.parent / result
    return result
