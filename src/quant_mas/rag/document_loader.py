"""Small document loading helpers for keyword retrieval."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Document:
    """Plain-text document loaded from local research artifacts."""

    doc_id: str
    path: Path
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


def load_document(path: str | Path, *, max_chars: int = 50_000) -> Document:
    """Load a supported text document and truncate oversized content."""
    source = Path(path).expanduser()
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if source.suffix.lower() not in {".md", ".txt", ".json"}:
        raise ValueError(f"Unsupported document extension: {source.suffix}")
    content = _read_content(source)
    truncated = len(content) > max_chars
    if truncated:
        content = content[:max_chars]
    return Document(
        doc_id=str(source),
        path=source,
        title=_title_for(source, content),
        content=content,
        metadata={
            "source": str(source),
            "extension": source.suffix.lower(),
            "char_count": len(content),
            "truncated": truncated,
        },
    )


def load_documents(
    directory: str | Path,
    *,
    patterns: tuple[str, ...] = ("*.md", "*.txt", "*.json"),
    recursive: bool = True,
    max_chars: int = 50_000,
) -> list[Document]:
    """Load supported documents under a directory."""
    root = Path(directory).expanduser()
    if not root.exists():
        return []
    documents: list[Document] = []
    seen: set[Path] = set()
    for pattern in patterns:
        iterator = root.rglob(pattern) if recursive else root.glob(pattern)
        for path in iterator:
            if path in seen or not path.is_file() or _should_skip(path):
                continue
            seen.add(path)
            document = load_document(path, max_chars=max_chars)
            documents.append(
                Document(
                    doc_id=str(path.relative_to(root)),
                    path=document.path,
                    title=document.title,
                    content=document.content,
                    metadata={**document.metadata, "root": str(root)},
                )
            )
    return sorted(documents, key=lambda document: str(document.path))


def _read_content(path: Path) -> str:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("text"), str):
            return data["text"]
        return json.dumps(data, indent=2, ensure_ascii=False)
    return path.read_text(encoding="utf-8")


def _title_for(path: Path, content: str) -> str:
    if path.suffix.lower() == ".md":
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip() or path.stem
    return path.stem


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if "__pycache__" in parts:
        return True
    return path.name.startswith(".")
