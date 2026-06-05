# Quant MAS v5 UI Design / UI 设计

This document records the Phase 1-10 UI direction for the Quant MAS v5 full-stack interface.

本文档记录 Quant MAS v5 全栈界面的 Phase 1-10 UI 方向。

---

## Design Goal / 设计目标

The first UI should behave like a research operations dashboard, not a marketing page. It should make system status, research baselines, safety boundaries, and planned modules easy to scan.

第一版 UI 应该像研究运营仪表盘，而不是营销页。它需要让系统状态、研究基线、安全边界和规划模块易于快速浏览。

---

## Phase 1-10 Screen / Phase 1-10 页面

| Area | English | 中文 |
|---|---|---|
| Header | Shows Quant MAS v5 enterprise preview and API connection state. | 展示 Quant MAS v5 企业级预览和 API 连接状态。 |
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
| Human Review Queue | Shows pending review items and required gates. | 展示待审查项和必要关卡。 |
| Job Status | Shows lightweight job progress and events. | 展示轻量任务进度和事件。 |
| Database Tables | Shows optional table readiness for local/Postgres modes. | 展示 local/Postgres 模式的可选表准备状态。 |
| RAG Documents | Shows fallback or configured RAG documents. | 展示回退或配置的 RAG 文档。 |
| Graph Relationships | Shows optional Neo4j-style relationship metadata. | 展示可选 Neo4j 风格关系元数据。 |

---

## Visual Direction / 视觉方向

Use a quiet, utilitarian research-tool style: dense but readable panels, restrained colors, clear typography, and stable responsive grids.

采用安静、实用的研究工具风格：信息密度适中但易读，颜色克制，排版清晰，响应式网格稳定。

---

## Interaction Direction / 交互方向

Phase 1 only needs the Dashboard to fetch `/api/status`. Phase 2 adds read-only Agent, Tool, and Memory/RAG panels plus a mock-safe agent run API. Phase 3 adds Backtest, Walk-forward OOS, and Risk Review summary panels. Phase 4 adds database and deployment status panels. Phase 5 adds server-ready Experiment, Paper Artifact, and Audit Log panels. Phase 6 adds API Access. Phase 7 adds Human Review Queue and Job Status panels. Phase 8 adds optional Database Tables, RAG Documents, and Graph Relationships panels. Phase 9 adds System Health, Metrics Summary, Server Logs, and Effective Config panels. Phase 10 keeps the dashboard as a demo-ready research operations console, while later product work can split it into dedicated pages.

Phase 1 只需要 Dashboard 请求 `/api/status`。Phase 2 增加只读 Agent、Tool、Memory/RAG 面板，以及 mock-safe 智能体运行 API。Phase 3 增加 Backtest、Walk-forward OOS 和 Risk Review 摘要面板。Phase 4 增加数据库和部署状态面板。Phase 5 增加服务器可用的 Experiment、Paper Artifact 和 Audit Log 面板。Phase 6 增加 API Access。Phase 7 增加 Human Review Queue 和 Job Status 面板。Phase 8 增加可选 Database Tables、RAG Documents 和 Graph Relationships 面板。后续阶段再拆成专门页面。

Phase 9 增加 System Health、Metrics Summary、Server Logs 和 Effective Config 面板。Phase 10 将仪表盘收口为可演示的研究运维控制台，后续产品化再拆成专门页面。

---

## Phase 9-10 Panels / Phase 9-10 面板

| Area | English | 中文 |
|---|---|---|
| System Health | Shows backend service status, research-only flag, and component readiness. | 展示后端服务状态、research-only 标记和组件准备状态。 |
| Metrics Summary | Shows readiness counters and baseline gauges without implying future results. | 展示准备度计数和基线数值，不暗示未来结果。 |
| Server Logs | Shows recent event count and configured log root. | 展示近期事件数量和配置日志目录。 |
| Effective Config | Shows redacted auth/storage/vector configuration. | 展示脱敏后的认证、存储和向量配置。 |
| Demo Readiness | Keeps all major v5 capabilities visible on one page for review. | 将 v5 主要能力集中在一页，便于评审展示。 |
