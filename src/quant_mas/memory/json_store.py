"""JSON MemoryStore backend."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quant_mas.memory.experiment_memory import ExperimentMemory, ExperimentRecord
from quant_mas.memory.store_base import MemoryStore


class JsonMemoryStore(MemoryStore):
    """MemoryStore wrapper around ExperimentMemory."""

    def __init__(self, path: str | Path) -> None:
        self.memory = ExperimentMemory(path)

    def add(
        self,
        *,
        name: str,
        status: str = "completed",
        metrics: dict[str, Any] | None = None,
        artifacts: dict[str, str | Path] | None = None,
        params: dict[str, Any] | None = None,
        notes: str = "",
        experiment_id: str | None = None,
    ) -> ExperimentRecord:
        return self.memory.add(
            name=name,
            status=status,
            metrics=metrics,
            artifacts=artifacts,
            params=params,
            notes=notes,
            experiment_id=experiment_id,
        )

    def get(self, experiment_id: str) -> ExperimentRecord:
        return self.memory.get(experiment_id)

    def list(self) -> list[ExperimentRecord]:
        return self.memory.list()

    def search_by_name(
        self,
        keyword: str,
        *,
        case_sensitive: bool = False,
    ) -> list[ExperimentRecord]:
        return self.memory.search_by_name(keyword, case_sensitive=case_sensitive)

    def sort_by_metric(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> list[ExperimentRecord]:
        return self.memory.sort_by_metric(metric, descending=descending)

    def find_best(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> ExperimentRecord:
        return self.memory.find_best(metric, descending=descending)
