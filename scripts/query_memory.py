"""Query experiment memory and local documents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quant_mas.memory import create_memory_store
from quant_mas.rag import SimpleRetriever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query Quant MAS memory or RAG documents.")
    parser.add_argument("--backend", choices=("json", "sqlite", "postgres"), default="json")
    parser.add_argument("--json-path", default="outputs/reports/experiments.json")
    parser.add_argument("--sqlite-path", default="outputs/reports/experiments.db")
    parser.add_argument("--postgres-dsn", help="Postgres DSN; defaults to POSTGRES_DSN env.")
    parser.add_argument("--query", help="Experiment name keyword.")
    parser.add_argument("--best-metric", help="Metric path, e.g. oos.sharpe.")
    parser.add_argument("--rag-query", help="Keyword query over documents.")
    parser.add_argument("--dirs", nargs="*", default=["docs", "outputs/reports"])
    parser.add_argument("--top-k", type=int, default=5)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.rag_query:
            results = query_rag(
                args.rag_query,
                dirs=[Path(value).expanduser() for value in args.dirs],
                top_k=args.top_k,
            )
        else:
            results = query_memory(
                backend=args.backend,
                json_path=Path(args.json_path).expanduser(),
                sqlite_path=Path(args.sqlite_path).expanduser(),
                postgres_dsn=args.postgres_dsn,
                query=args.query,
                best_metric=args.best_metric,
            )
    except Exception as exc:
        print(f"[query] ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def query_memory(
    *,
    backend: str,
    json_path: Path,
    sqlite_path: Path,
    postgres_dsn: str | None,
    query: str | None,
    best_metric: str | None,
) -> list[dict]:
    store = create_memory_store(
        backend,
        json_path=json_path,
        sqlite_path=sqlite_path,
        postgres_dsn=postgres_dsn,
    )
    if best_metric:
        records = [store.find_best(best_metric)]
    elif query:
        records = store.search_by_name(query)
    else:
        records = store.list()
    return [record.__dict__ for record in records]


def query_rag(query: str, *, dirs: list[Path], top_k: int) -> list[dict]:
    retriever = SimpleRetriever.from_directories(dirs)
    return [
        {
            "doc_id": result.document.doc_id,
            "path": str(result.document.path),
            "title": result.document.title,
            "score": result.score,
            "matched_terms": result.matched_terms,
        }
        for result in retriever.search(query, top_k=top_k)
    ]


if __name__ == "__main__":
    raise SystemExit(main())
