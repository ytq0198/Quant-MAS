"""Parquet-based storage utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class ParquetStorage:
    """Small wrapper around pandas parquet IO."""

    def save(self, frame: pd.DataFrame, path: str | Path, **kwargs: Any) -> Path:
        """Save a DataFrame to parquet and create parent directories."""
        target = Path(path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(target, index=False, **kwargs)
        return target

    def load(self, path: str | Path, **kwargs: Any) -> pd.DataFrame:
        """Load a parquet file into a DataFrame."""
        target = Path(path).expanduser()
        if not target.exists():
            raise FileNotFoundError(f"Parquet file does not exist: {target}")
        return pd.read_parquet(target, **kwargs)

    def exists(self, path: str | Path) -> bool:
        """Return whether the parquet path exists."""
        return Path(path).expanduser().exists()

