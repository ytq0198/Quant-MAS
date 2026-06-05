from __future__ import annotations

import os
from pathlib import Path


def get_artifact_root() -> Path:
    """Return the root containing Quant MAS artifacts.

    返回包含 Quant MAS 产物的根目录。
    """
    return Path(os.getenv("QUANT_MAS_ARTIFACT_ROOT", ".")).expanduser().resolve()


def get_experiment_memory_path(artifact_root: str | Path | None = None) -> Path:
    """Return configured ExperimentMemory path.

    返回配置的 ExperimentMemory 路径。
    """
    configured = os.getenv("QUANT_MAS_EXPERIMENT_MEMORY_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    root = Path(artifact_root).expanduser().resolve() if artifact_root else get_artifact_root()
    return root / "outputs" / "reports" / "experiments.json"


def get_paper_dir(artifact_root: str | Path | None = None) -> Path:
    """Return configured paper artifact directory.

    返回配置的论文产物目录。
    """
    configured = os.getenv("QUANT_MAS_PAPER_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    root = Path(artifact_root).expanduser().resolve() if artifact_root else get_artifact_root()
    return root / "outputs" / "paper"


def get_audit_dir(artifact_root: str | Path | None = None) -> Path:
    """Return configured audit log directory.

    返回配置的审计日志目录。
    """
    configured = os.getenv("QUANT_MAS_AUDIT_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    root = Path(artifact_root).expanduser().resolve() if artifact_root else get_artifact_root()
    return root / "outputs" / "pipelines"
