"""Index local documents for lightweight RAG."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quant_mas.rag import HashEmbeddingClient, InMemoryVectorStore, chunk_text, load_documents
from quant_mas.rag.faiss_store import FaissVectorStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Index local documents for RAG.")
    parser.add_argument("--dirs", nargs="*", default=["docs", "outputs/reports"])
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--overlap", type=int, default=64)
    parser.add_argument("--vector-store", choices=("in_memory", "faiss"), default="in_memory")
    parser.add_argument("--output", default="outputs/rag/index.json")
    parser.add_argument("--embedding-dimensions", type=int, default=64)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = index_documents(
            dirs=[Path(value).expanduser() for value in args.dirs],
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            vector_store=args.vector_store,
            output=Path(args.output).expanduser(),
            embedding_dimensions=args.embedding_dimensions,
        )
    except Exception as exc:
        print(f"[index] ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"[index] documents={result['documents']} chunks={result['chunks']}")
    print(f"[index] output={result['output']}")
    return 0


def index_documents(
    *,
    dirs: list[Path],
    chunk_size: int,
    overlap: int,
    vector_store: str,
    output: Path,
    embedding_dimensions: int = 64,
) -> dict[str, int | str]:
    documents = []
    for directory in dirs:
        documents.extend(load_documents(directory))
    ids: list[str] = []
    texts: list[str] = []
    metadata: list[dict] = []
    for document in documents:
        for index, chunk in enumerate(chunk_text(document.content, chunk_size, overlap)):
            id_ = f"{document.doc_id}::{index}"
            ids.append(id_)
            texts.append(chunk)
            metadata.append(
                {
                    "id": id_,
                    "doc_id": document.doc_id,
                    "path": str(document.path),
                    "title": document.title,
                    "content": chunk,
                    **document.metadata,
                }
            )
    embeddings = HashEmbeddingClient(dimensions=embedding_dimensions).embed(texts)
    if vector_store == "faiss":
        FaissVectorStore()
    store = InMemoryVectorStore()
    store.upsert(ids, embeddings, metadata)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "vector_store": vector_store,
                "embedding_provider": "hash",
                "records": store.to_records(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return {"documents": len(documents), "chunks": len(ids), "output": str(output)}


if __name__ == "__main__":
    raise SystemExit(main())
