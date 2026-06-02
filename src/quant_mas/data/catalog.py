"""Storage directory catalog loaded from YAML config."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DIRECTORY_KEYS = (
    "raw_data_dir",
    "processed_data_dir",
    "features_dir",
    "models_dir",
    "reports_dir",
    "logs_dir",
)


@dataclass(frozen=True)
class DataCatalog:
    """Resolve and create project storage directories from YAML config."""

    project_root: Path
    raw_data_dir: Path
    processed_data_dir: Path
    features_dir: Path
    models_dir: Path
    reports_dir: Path
    logs_dir: Path

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "DataCatalog":
        config_file = Path(config_path).expanduser().resolve()
        with config_file.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        project_root = cls._resolve_project_root(config, config_file)
        values: dict[str, Path] = {"project_root": project_root}

        for key in DIRECTORY_KEYS:
            if key not in config:
                raise KeyError(f"Missing storage config key: {key}")
            values[key] = cls._resolve_path(config[key], project_root)

        catalog = cls(**values)
        catalog.ensure_directories()
        return catalog

    def ensure_directories(self) -> None:
        """Create all configured storage directories."""
        for directory in self.directories().values():
            directory.mkdir(parents=True, exist_ok=True)

    def directories(self) -> dict[str, Path]:
        """Return configured storage directories without project_root."""
        return {key: getattr(self, key) for key in DIRECTORY_KEYS}

    def path_for(self, key: str, *parts: str) -> Path:
        """Return a path under one configured directory."""
        if key not in DIRECTORY_KEYS:
            raise KeyError(f"Unknown storage directory key: {key}")
        return getattr(self, key).joinpath(*parts)

    @staticmethod
    def _resolve_project_root(config: dict[str, Any], config_file: Path) -> Path:
        configured_root = config.get("project_root", ".")
        root = Path(configured_root).expanduser()
        if not root.is_absolute():
            root = config_file.parent / root
        return root.resolve()

    @staticmethod
    def _resolve_path(value: Any, project_root: Path) -> Path:
        path = Path(str(value)).expanduser()
        if not path.is_absolute():
            path = project_root / path
        return path.resolve()
