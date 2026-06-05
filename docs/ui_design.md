# Quant MAS v4 UI Design / UI 设计

This document records the Phase 1-2 UI direction for the Quant MAS v4 full-stack interface.

本文档记录 Quant MAS v4 全栈界面的 Phase 1-2 UI 方向。

---

## Design Goal / 设计目标

The first UI should behave like a research operations dashboard, not a marketing page. It should make system status, research baselines, safety boundaries, and planned modules easy to scan.

第一版 UI 应该像研究运营仪表盘，而不是营销页。它需要让系统状态、研究基线、安全边界和规划模块易于快速浏览。

---

## Phase 1-2 Screen / Phase 1-2 页面

| Area | English | 中文 |
|---|---|---|
| Header | Shows Quant MAS v4 full-stack preview and API connection state. | 展示 Quant MAS v4 全栈预览和 API 连接状态。 |
| Research Baseline | Shows `361 passed`, `EXP-20260602-008`, and OOS Sharpe `0.586`. | 展示 `361 passed`、`EXP-20260602-008` 和 OOS Sharpe `0.586`。 |
| Safety Boundary | Shows no direct live trading, OOS-only paper conclusions, and metric separation. | 展示不直接实盘交易、论文结论只使用 OOS 指标，以及指标分离。 |
| Planned Modules | Lists Dashboard, Agent Console, Tool Console, Memory/RAG Search, Backtest View, Walk-forward View, Audit Review, and Paper Export. | 列出 Dashboard、Agent Console、Tool Console、Memory/RAG Search、Backtest View、Walk-forward View、Audit Review 和 Paper Export。 |
| Agents | Shows mock-safe SupervisorAgent, ResearchAgent, and ReportAgent metadata. | 展示 mock-safe 的 SupervisorAgent、ResearchAgent 和 ReportAgent 元数据。 |
| Controlled Tools | Shows approved tool names and allowed operations. | 展示已批准工具名称和允许操作。 |
| Memory/RAG Search | Shows local fixture search results for OOS baseline and safety context. | 展示 OOS 基线和安全上下文的本地夹具检索结果。 |

---

## Visual Direction / 视觉方向

Use a quiet, utilitarian research-tool style: dense but readable panels, restrained colors, clear typography, and stable responsive grids.

采用安静、实用的研究工具风格：信息密度适中但易读，颜色克制，排版清晰，响应式网格稳定。

---

## Interaction Direction / 交互方向

Phase 1 only needs the Dashboard to fetch `/api/status`. Phase 2 adds read-only Agent, Tool, and Memory/RAG panels plus a mock-safe agent run API. Later phases should add dedicated pages for Backtest charts, Walk-forward windows, Audit logs, and Human Review.

Phase 1 只需要 Dashboard 请求 `/api/status`。Phase 2 增加只读 Agent、Tool、Memory/RAG 面板，以及 mock-safe 智能体运行 API。后续阶段再增加回测图表、Walk-forward 窗口、审计日志和人工审查页面。
