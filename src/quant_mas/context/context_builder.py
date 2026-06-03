"""Build structured context bundles from memory, RAG, and workflow state."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from quant_mas.context.compression import (
    DEFAULT_METRIC_KEYS,
    compress_metrics,
    compress_rag_chunks,
)
from quant_mas.context.context_schema import (
    AgentContextBundle,
    ExperimentContextSnapshot,
    RagContextChunk,
    RiskContextSnapshot,
)
from quant_mas.data import DataCatalog
from quant_mas.memory import ExperimentMemory
from quant_mas.memory.store_base import MemoryStore
from quant_mas.rag import HybridRetriever, SimpleRetriever


class ContextBuilder:
    """Assemble bounded context for research interpretation."""

    def __init__(
        self,
        *,
        memory_store: MemoryStore | None = None,
        retriever: SimpleRetriever | HybridRetriever | None = None,
        storage_config: str | Path = "configs/storage.yaml",
        context_config: str | Path = "configs/context.yaml",
    ) -> None:
        self.storage_config = Path(storage_config)
        self.context_config = Path(context_config)
        self.config = _load_context_config(self.context_config)
        self.memory_store = memory_store or _default_memory_store(self.storage_config)
        self.retriever = retriever

    def build(
        self,
        *,
        task: str,
        experiment_name: str | None = None,
        rag_query: str | None = None,
        workflow_state: dict | None = None,
        metric_keys: list[str] | None = None,
    ) -> AgentContextBundle:
        """Build one AgentContextBundle without calling any LLM."""
        keys = metric_keys or self.config["metric_keys"]
        experiments = self._experiment_snapshots(experiment_name, keys)
        baseline = self._baseline_snapshot(keys)
        rag_chunks = self._rag_chunks(rag_query or task)
        workflow = _workflow_summary(workflow_state or {}, keys)
        risk = _risk_from_workflow(workflow_state or {})
        if risk is None and isinstance(workflow.get("metrics"), dict):
            risk_payload = workflow["metrics"].get("risk")
            if isinstance(risk_payload, dict):
                risk = _risk_from_payload(risk_payload)
        return AgentContextBundle(
            task=task,
            experiments=experiments,
            baseline=baseline,
            risk=risk,
            rag_chunks=rag_chunks,
            workflow=workflow,
            baseline_ref=self.config["baseline_experiment_hint"],
        )

    def _experiment_snapshots(
        self,
        experiment_name: str | None,
        metric_keys: list[str],
    ) -> list[ExperimentContextSnapshot]:
        records = []
        try:
            if experiment_name:
                records = self.memory_store.search_by_name(experiment_name)
            else:
                records = self.memory_store.list()[-1:]
        except (FileNotFoundError, ValueError):
            records = []
        return [_snapshot_from_record(record, metric_keys) for record in records]

    def _baseline_snapshot(self, metric_keys: list[str]) -> ExperimentContextSnapshot | None:
        try:
            record = self.memory_store.find_best("oos.sharpe")
        except (FileNotFoundError, ValueError):
            return None
        return _snapshot_from_record(record, metric_keys)

    def _rag_chunks(self, query: str) -> list[RagContextChunk]:
        retriever = self.retriever
        if retriever is None:
            retriever = SimpleRetriever.from_directories()
        results = retriever.search(query, top_k=self.config["max_rag_chunks"])
        chunks: list[RagContextChunk] = []
        for result in results:
            document = result.document
            chunks.append(
                RagContextChunk(
                    doc_id=document.doc_id,
                    path=str(document.path),
                    title=document.title,
                    snippet=document.content,
                    score=float(result.score),
                )
            )
        return compress_rag_chunks(
            chunks,
            max_chunks=self.config["max_rag_chunks"],
            max_chars=self.config["max_snippet_chars"],
        )


def _load_context_config(path: Path) -> dict[str, Any]:
    defaults = {
        "max_rag_chunks": 5,
        "max_snippet_chars": 400,
        "max_bundle_chars": 8000,
        "metric_keys": DEFAULT_METRIC_KEYS,
        "baseline_experiment_hint": "EXP-20260602-008",
    }
    if not path.exists():
        return defaults
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    context = payload.get("context", payload)
    return {**defaults, **context}


def _default_memory_store(storage_config: Path) -> ExperimentMemory:
    catalog = DataCatalog.from_yaml(storage_config)
    return ExperimentMemory(catalog.path_for("reports_dir", "experiments.json"))


def _snapshot_from_record(record, metric_keys: list[str]) -> ExperimentContextSnapshot:
    return ExperimentContextSnapshot(
        experiment_id=record.experiment_id,
        name=record.name,
        family=_infer_family(record.name),
        metrics=compress_metrics(record.metrics, keep_keys=metric_keys),
        artifacts={key: str(value) for key, value in record.artifacts.items()},
        status=record.status,
        created_at=record.created_at,
    )


def _infer_family(name: str) -> str:
    lower = name.lower()
    if "walk" in lower:
        return "walk_forward"
    if "ml" in lower or "lightgbm" in lower:
        return "ml_backtest"
    if "ma" in lower or "cross" in lower:
        return "ma_cross"
    return "unknown"


def _workflow_summary(state: dict[str, Any], metric_keys: list[str]) -> dict[str, Any]:
    if not state:
        return {}
    metrics = state.get("metrics", {})
    return {
        "completed_nodes": list(state.get("completed_nodes", [])),
        "errors": list(state.get("errors", [])),
        "metrics": compress_metrics(metrics, keep_keys=metric_keys)
        if isinstance(metrics, dict)
        else {},
        "artifacts": {
            key: str(value)
            for key, value in (state.get("artifacts") or {}).items()
        },
    }


def _risk_from_workflow(state: dict[str, Any]) -> RiskContextSnapshot | None:
    risk_payload = state.get("risk")
    if isinstance(risk_payload, dict):
        return _risk_from_payload(risk_payload)
    metrics = state.get("metrics")
    if isinstance(metrics, dict) and isinstance(metrics.get("risk"), dict):
        return _risk_from_payload(metrics["risk"])
    return None


def _risk_from_payload(payload: dict[str, Any]) -> RiskContextSnapshot:
    return RiskContextSnapshot(
        approved=payload.get("approved"),
        status=str(payload.get("status", "unknown")),
        violations=[str(item) for item in payload.get("violations", [])],
    )
