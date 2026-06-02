"""Memory store abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from quant_mas.memory.experiment_memory import ExperimentRecord


class MemoryStore(ABC):
    """Abstract experiment memory backend."""

    @abstractmethod
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
        """Add one experiment record."""

    @abstractmethod
    def get(self, experiment_id: str) -> ExperimentRecord:
        """Return one experiment by id."""

    @abstractmethod
    def list(self) -> list[ExperimentRecord]:
        """Return all experiment records."""

    @abstractmethod
    def search_by_name(
        self,
        keyword: str,
        *,
        case_sensitive: bool = False,
    ) -> list[ExperimentRecord]:
        """Search records by name."""

    @abstractmethod
    def sort_by_metric(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> list[ExperimentRecord]:
        """Sort by a metric path."""

    @abstractmethod
    def find_best(
        self,
        metric: str,
        *,
        descending: bool = True,
    ) -> ExperimentRecord:
        """Return best record by metric."""


def resolve_metric(metrics: dict[str, Any], metric: str) -> Any:
    """Resolve flat or dotted metric path."""
    if metric in metrics:
        return metrics[metric]
    current: Any = metrics
    for part in metric.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def sort_records_by_metric(
    records: list[ExperimentRecord],
    metric: str,
    *,
    descending: bool = True,
) -> list[ExperimentRecord]:
    """Sort records by metric while keeping missing values last."""
    present = [record for record in records if resolve_metric(record.metrics, metric) is not None]
    missing = [record for record in records if resolve_metric(record.metrics, metric) is None]
    present.sort(
        key=lambda record: resolve_metric(record.metrics, metric),
        reverse=descending,
    )
    return present + missing
