"""Run the Quant MAS research agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quant_mas.agents import ResearchAgent
from quant_mas.context import ContextBuilder
from quant_mas.core import resolve_llm_client
from quant_mas.data import DataCatalog
from quant_mas.memory import create_memory_store
from quant_mas.rag import SimpleRetriever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ResearchAgent with bounded context.")
    parser.add_argument("--task", required=True, help="Research question or task.")
    parser.add_argument(
        "--use-llm",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Use real LLM provider when env is configured; default is mock.",
    )
    parser.add_argument(
        "--provider",
        choices=["mock", "openai_compatible", "local_vllm"],
        help="LLM provider override. local_vllm requires VLLM_BASE_URL.",
    )
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--context-config", default="configs/context.yaml")
    parser.add_argument("--memory-backend", choices=["json", "sqlite"], default="json")
    parser.add_argument("--json-path", help="ExperimentMemory JSON path.")
    parser.add_argument("--sqlite-path", help="SQLite memory path.")
    parser.add_argument("--rag-query", help="Optional RAG query.")
    parser.add_argument("--experiment-name", help="Experiment name keyword.")
    parser.add_argument("--workflow-json", help="Optional workflow state JSON path.")
    parser.add_argument("--output-json", help="Write output JSON to this path.")
    return parser


def main() -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        catalog = DataCatalog.from_yaml(args.storage_config)
        json_path = args.json_path or str(catalog.path_for("reports_dir", "experiments.json"))
        sqlite_path = args.sqlite_path or str(catalog.path_for("reports_dir", "experiments.db"))
        memory_store = create_memory_store(
            args.memory_backend,
            json_path=json_path,
            sqlite_path=sqlite_path,
        )
        workflow_state = _load_json(args.workflow_json) if args.workflow_json else None
        retriever = SimpleRetriever.from_directories()
        bundle = ContextBuilder(
            memory_store=memory_store,
            retriever=retriever,
            storage_config=args.storage_config,
            context_config=args.context_config,
        ).build(
            task=args.task,
            experiment_name=args.experiment_name,
            rag_query=args.rag_query,
            workflow_state=workflow_state,
        )
        agent = ResearchAgent(resolve_llm_client(provider=args.provider, use_llm=args.use_llm))
        output = agent.run_research(bundle)
        payload = {"output": output.to_dict(), "context": bundle.to_dict()}
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if args.output_json:
            output_path = Path(args.output_json).expanduser()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    except Exception as exc:
        print(f"[research-agent] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_json(path: str) -> dict:
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
