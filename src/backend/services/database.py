from __future__ import annotations

from typing import Any


def get_database_status() -> dict[str, Any]:
    """Return optional database backend status for Phase 4.

    返回 Phase 4 可选数据库后端状态。
    """
    return {
        "mode": "optional",
        "default_backend": "local_files",
        "summary": "Phase 4 documents database-ready paths without requiring live services for tests.",
        "中文": "Phase 4 记录数据库接入路径，但测试不强制依赖真实服务。",
        "backends": [
            {
                "name": "local_files",
                "purpose": "Parquet and JSONL local data, reports, audit logs, and fixtures.",
                "required_for_tests": True,
                "status": "available_by_default",
            },
            {
                "name": "sqlite",
                "purpose": "Lightweight local ExperimentMemory and development metadata.",
                "required_for_tests": False,
                "status": "optional",
            },
            {
                "name": "postgres",
                "purpose": "Server-side experiments, task state, and metadata tables.",
                "required_for_tests": False,
                "status": "optional",
            },
            {
                "name": "pgvector",
                "purpose": "Vector search for RAG over documents, reports, and experiment memory.",
                "required_for_tests": False,
                "status": "optional",
            },
            {
                "name": "neo4j",
                "purpose": "Optional graph relationships across agents, tools, experiments, and documents.",
                "required_for_tests": False,
                "status": "optional",
            },
        ],
    }
