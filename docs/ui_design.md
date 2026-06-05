# Quant MAS v4 UI Design / UI 设计

This document records the Phase 1-5 UI direction for the Quant MAS v4/v5 full-stack interface.

本文档记录 Quant MAS v4/v5 全栈界面的 Phase 1-5 UI 方向。

---

## Design Goal / 设计目标

The first UI should behave like a research operations dashboard, not a marketing page. It should make system status, research baselines, safety boundaries, and planned modules easy to scan.

第一版 UI 应该像研究运营仪表盘，而不是营销页。它需要让系统状态、研究基线、安全边界和规划模块易于快速浏览。

---

## Phase 1-5 Screen / Phase 1-5 页面

| Area | English | 中文 |
|---|---|---|
| Header | Shows Quant MAS v4 full-stack preview and API connection state. | 展示 Quant MAS v4 全栈预览和 API 连接状态。 |
| Research Baseline | Shows `361 passed`, `EXP-20260602-008`, and OOS Sharpe `0.586`. | 展示 `361 passed`、`EXP-20260602-008` 和 OOS Sharpe `0.586`。 |
| Safety Boundary | Shows no direct live trading, OOS-only paper conclusions, and metric separation. | 展示不直接实盘交易、论文结论只使用 OOS 指标，以及指标分离。 |
| Planned Modules | Lists Dashboard, Agent Console, Tool Console, Memory/RAG Search, Backtest View, Walk-forward View, Audit Review, and Paper Export. | 列出 Dashboard、Agent Console、Tool Console、Memory/RAG Search、Backtest View、Walk-forward View、Audit Review 和 Paper Export。 |
| Agents | Shows mock-safe SupervisorAgent, ResearchAgent, and ReportAgent metadata. | 展示 mock-safe 的 SupervisorAgent、ResearchAgent 和 ReportAgent 元数据。 |
| Controlled Tools | Shows approved tool names and allowed operations. | 展示已批准工具名称和允许操作。 |
| Memory/RAG Search | Shows local fixture search results for OOS baseline and safety context. | 展示 OOS 基线和安全上下文的本地夹具检索结果。 |
| Backtest Summary | Shows a non-OOS research-only backtest preview with a small equity shape. | 展示非 OOS、仅用于研究理解的回测预览和小型权益形态。 |
| Walk-forward OOS | Shows the audited OOS baseline, Sharpe `0.586`, and 19 windows. | 展示经过审计的 OOS 基线、Sharpe `0.586` 和 19 个窗口。 |
| Risk Review | Shows required gates before any candidate can move forward. | 展示候选策略进入下一步前必须经过的关卡。 |
| Database Backends | Shows local files, SQLite, Postgres, pgvector, and Neo4j readiness metadata. | 展示本地文件、SQLite、Postgres、pgvector 和 Neo4j 准备状态元数据。 |
| Deployment Skeleton | Shows FastAPI, React/Vite, Docker Compose, backend Dockerfile, and frontend Dockerfile artifacts. | 展示 FastAPI、React/Vite、Docker Compose、后端 Dockerfile 和前端 Dockerfile 产物。 |
| Experiment Registry | Shows artifact-backed experiment records or fallback baseline. | 展示产物驱动的实验记录或回退基线。 |
| Paper Artifacts | Shows paper export files from configured server artifact directory. | 展示来自服务器配置产物目录的论文导出文件。 |
| Audit Logs | Shows JSONL audit event count and source mode. | 展示 JSONL 审计事件数量和来源模式。 |

---

## Visual Direction / 视觉方向

Use a quiet, utilitarian research-tool style: dense but readable panels, restrained colors, clear typography, and stable responsive grids.

采用安静、实用的研究工具风格：信息密度适中但易读，颜色克制，排版清晰，响应式网格稳定。

---

## Interaction Direction / 交互方向

Phase 1 only needs the Dashboard to fetch `/api/status`. Phase 2 adds read-only Agent, Tool, and Memory/RAG panels plus a mock-safe agent run API. Phase 3 adds Backtest, Walk-forward OOS, and Risk Review summary panels. Phase 4 adds database and deployment status panels. Phase 5 adds server-ready Experiment, Paper Artifact, and Audit Log panels. Later phases should add dedicated pages for charts, audit logs, and human review queues.

Phase 1 只需要 Dashboard 请求 `/api/status`。Phase 2 增加只读 Agent、Tool、Memory/RAG 面板，以及 mock-safe 智能体运行 API。Phase 3 增加 Backtest、Walk-forward OOS 和 Risk Review 摘要面板。Phase 4 增加数据库和部署状态面板。Phase 5 增加服务器可用的 Experiment、Paper Artifact 和 Audit Log 面板。后续阶段再增加专门图表、审计日志和人工审查队列。
