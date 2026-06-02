"""Lightweight .env loader (no python-dotenv dependency)."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path, *, override: bool = False) -> bool:
    """Load ``KEY=VALUE`` lines from a file into ``os.environ``.

    Returns True if the file existed and was read.
    """

    if not path.is_file():
        return False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip().strip('"').strip("'")
        if not override and key in os.environ:
            continue
        os.environ[key] = value

    return True


def load_repo_dotenv(start: Path | None = None) -> bool:
    """Load ``.env`` from repo root (directory containing ``pyproject.toml``)."""

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return load_dotenv(candidate / ".env")
        if (candidate / ".git").is_file():
            return load_dotenv(candidate / ".env")
    return load_dotenv(current / ".env")
