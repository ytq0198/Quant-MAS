from __future__ import annotations

from typing import Any

_LOCAL_MEMORY: list[dict[str, Any]] = [
    {
        "id": "memory-oos-baseline",
        "title": "EXP-20260602-008 OOS baseline",
        "type": "experiment",
        "snippet": "Walk-forward OOS Sharpe = 0.586. Paper-grade baseline, not a trading promise.",
        "中文": "Walk-forward 样本外 Sharpe = 0.586。论文级基线，不是交易承诺。",
    },
    {
        "id": "memory-safety-boundary",
        "title": "Safety boundary",
        "type": "policy",
        "snippet": "LLM agents do not place live orders. Candidates require backtest, risk check, audit log, and human confirmation.",
        "中文": "LLM 智能体不直接下单。候选策略必须经过回测、风控、审计日志和人工确认。",
    },
    {
        "id": "memory-metric-separation",
        "title": "Metric separation",
        "type": "research_protocol",
        "snippet": "Do not mix oos.* with simulation.*, training.*, population.*, or audit.* metrics.",
        "中文": "不要混用 oos.* 与 simulation.*、training.*、population.* 或 audit.* 指标。",
    },
]


def search_memory(query: str) -> dict[str, Any]:
    """Search local fixture memory for Phase 2.

    搜索 Phase 2 本地夹具记忆。
    """
    normalized_query = query.strip().lower()
    if not normalized_query:
        matches = _LOCAL_MEMORY
    else:
        matches = [
            item
            for item in _LOCAL_MEMORY
            if normalized_query in item["title"].lower()
            or normalized_query in item["snippet"].lower()
            or normalized_query in item["type"].lower()
        ]
    if not matches:
        matches = _LOCAL_MEMORY[:1]

    return {
        "query": query,
        "mode": "local-fixture",
        "results": matches,
    }
