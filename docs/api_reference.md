# Quant MAS v5 API Reference / API 参考

All endpoints are research-only. They do not expose broker control, order placement, shell execution, or raw secrets.

所有接口都仅用于研究展示，不暴露 broker 控制、下单、shell 执行或明文密钥。

## Public Status / 公共状态

| Method | Path | Purpose | 中文 |
|---|---|---|---|
| GET | `/api/status` | Project status, baseline metadata, safety boundaries, and UI modules. | 项目状态、基线元数据、安全边界和 UI 模块。 |
| GET | `/api/health` | Lightweight health check for smoke testing. | 用于 smoke 测试的轻量健康检查。 |
| GET | `/api/health/deep` | Component-level health with optional backend readiness. | 组件级健康状态和可选后端准备状态。 |
| GET | `/api/metrics/summary` | System readiness metrics, not trading performance promises. | 系统准备度指标，不是交易表现承诺。 |
| GET | `/api/logs/recent` | Recent JSONL events from configured log roots. | 从配置日志目录读取近期 JSONL 事件。 |
| GET | `/api/config/effective` | Redacted runtime config for deployment checks. | 用于部署检查的脱敏运行配置。 |

## Agents, Tools, Memory / 智能体、工具、记忆

| Method | Path | Role | Purpose | 中文 |
|---|---|---|---|---|
| GET | `/api/agents` | viewer | List mock-safe research agents. | 列出 mock-safe 研究智能体。 |
| POST | `/api/agents/run` | researcher+ | Run a controlled agent task and append audit metadata when configured. | 运行受控智能体任务，并在配置后写入审计元数据。 |
| GET | `/api/tools` | viewer | List controlled tools and allowed operations. | 列出受控工具和允许操作。 |
| GET | `/api/memory/search?q=...` | viewer | Search local or configured memory context. | 搜索本地或配置的记忆上下文。 |

## Research Results / 研究结果

| Method | Path | Purpose | 中文 |
|---|---|---|---|
| GET | `/api/backtests/{id}` | Research-only backtest summary; not OOS. | 研究用回测摘要；不是 OOS。 |
| GET | `/api/oos/{id}` | Audited walk-forward OOS baseline summary. | 经审计的 Walk-forward OOS 基线摘要。 |
| GET | `/api/risk/{id}` | Risk gates and human confirmation requirements. | 风险关卡和人工确认要求。 |
| GET | `/api/experiments` | Artifact-backed experiment registry with fallback baseline. | 产物驱动实验注册表，支持 fallback 基线。 |
| GET | `/api/experiments/{id}` | One experiment record. | 单个实验记录。 |
| GET | `/api/artifacts/paper` | Paper artifact list from configured output directory. | 从配置输出目录读取论文产物列表。 |

## Audit, Review, Jobs / 审计、审核、任务

| Method | Path | Role | Purpose | 中文 |
|---|---|---|---|---|
| GET | `/api/audit/logs` | reviewer+ | Read audit JSONL events. | 读取审计 JSONL 事件。 |
| GET | `/api/review/queue` | viewer | List human review items. | 列出人工审核项。 |
| GET | `/api/review/{id}` | viewer | Read one review item. | 读取单个审核项。 |
| POST | `/api/review/{id}/approve` | reviewer+ | Approve a review item and write audit metadata when configured. | 批准审核项，并在配置后写入审计元数据。 |
| POST | `/api/review/{id}/reject` | reviewer+ | Reject a review item and write audit metadata when configured. | 拒绝审核项，并在配置后写入审计元数据。 |
| GET | `/api/jobs` | viewer | List lightweight job statuses. | 列出轻量任务状态。 |
| GET | `/api/jobs/{id}` | viewer | Read one job and events. | 读取单个任务和事件。 |

## Optional Data Services / 可选数据服务

| Method | Path | Purpose | 中文 |
|---|---|---|---|
| GET | `/api/database/status` | Optional database backend readiness. | 可选数据库后端准备状态。 |
| GET | `/api/database/tables` | Optional table readiness for local/Postgres modes. | local/Postgres 模式下的可选表准备状态。 |
| GET | `/api/rag/documents` | Fallback or configured RAG document list. | fallback 或配置的 RAG 文档列表。 |
| GET | `/api/rag/query?q=...` | Fallback or configured RAG query results. | fallback 或配置的 RAG 查询结果。 |
| GET | `/api/graph/relationships` | Optional Neo4j-style relationship metadata. | 可选 Neo4j 风格关系元数据。 |
| GET | `/api/deployment/status` | Deployment skeleton metadata and artifacts. | 部署骨架元数据和产物。 |
