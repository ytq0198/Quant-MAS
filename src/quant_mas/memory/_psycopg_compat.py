"""Helpers for psycopg3 cursors and test fake connections."""

from __future__ import annotations

from typing import Any


def pg_execute(connection: Any, query: str, params: tuple[Any, ...] | None = None) -> Any:
    """Run SQL on a connection or test fake."""
    return connection.execute(query, params)


def pg_fetchall(connection: Any, query: str, params: tuple[Any, ...] | None = None) -> list[Any]:
    """Fetch all rows; works with psycopg3 cursors and test fakes."""
    result = pg_execute(connection, query, params)
    if result is not None and hasattr(result, "fetchall"):
        return result.fetchall()
    return connection.fetchall()


def pg_fetchone(connection: Any, query: str, params: tuple[Any, ...] | None = None) -> Any:
    """Fetch one row; works with psycopg3 cursors and test fakes."""
    result = pg_execute(connection, query, params)
    if result is not None and hasattr(result, "fetchone"):
        return result.fetchone()
    return connection.fetchone()
