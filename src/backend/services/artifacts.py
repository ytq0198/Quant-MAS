from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.services.config import get_paper_dir


def list_paper_artifacts(artifact_root: str | Path | None = None) -> dict[str, Any]:
    """List paper artifacts from configured server/local directory.

    从配置的服务器/本地目录列出论文产物。
    """
    paper_dir = get_paper_dir(artifact_root)
    if not paper_dir.exists():
        return {"source": "fallback_empty", "path": str(paper_dir), "artifacts": []}
    artifacts = [
        {
            "name": item.name,
            "path": str(item),
            "suffix": item.suffix,
            "size_bytes": item.stat().st_size,
        }
        for item in sorted(paper_dir.iterdir())
        if item.is_file()
    ]
    return {
        "source": "server_artifact" if artifacts else "fallback_empty",
        "path": str(paper_dir),
        "artifacts": artifacts,
    }
