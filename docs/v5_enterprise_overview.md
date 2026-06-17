# Quant MAS v5 Enterprise Overview / 企业级总览

Quant MAS v5 is a research-only full-stack version of the project. It keeps the original deterministic quant research pipeline, then adds a server-ready backend, React dashboard, API key access control, audit records, optional database/RAG integrations, human review gates, job status, and observability.

Quant MAS v5 是本项目的研究型全栈版本。它保留原有的确定性量化研究流水线，并加入可部署后端、React 仪表盘、API Key 访问控制、审计记录、可选数据库/RAG 集成、人工审核关卡、任务状态和可观测性能力。

## What Is Complete / 已完成内容

| Area | English | 中文 |
|---|---|---|
| Backend boundary | FastAPI APIs expose status, agents, tools, memory, backtest summaries, OOS baseline, risk gates, experiments, artifacts, audit logs, database status, review queue, jobs, RAG, graph metadata, health, metrics, logs, and redacted config. | FastAPI API 已提供状态、智能体、工具、记忆、回测摘要、OOS 基线、风险关卡、实验、产物、审计日志、数据库状态、审核队列、任务、RAG、图谱元数据、健康检查、指标、日志和脱敏配置。 |
| Frontend dashboard | React + Vite dashboard displays the system as a research operations console with local fallback data. | React + Vite 仪表盘以研究运维控制台方式展示系统，并支持本地 fallback 数据。 |
| Server mode | Environment variables can point the backend to real server artifacts while local tests remain fallback-safe. | 可通过环境变量让后端读取服务器真实产物，同时本地测试保持 fallback-safe。 |
| Access control | API key mode supports viewer, researcher, reviewer, and admin roles. | API Key 模式支持 viewer、researcher、reviewer、admin 四类角色。 |
| Human gate | Review APIs model approval/rejection gates before any candidate moves forward. | 审核 API 用于表达候选结果进入下一步之前的批准/拒绝关卡。 |
| Observability | Health, deep health, metrics summary, recent logs, and effective config APIs support server smoke testing. | 健康状态、深度健康、指标摘要、近期日志和有效配置 API 支持服务器 smoke 测试。 |
| Help guide | In-app Help page (`Help.tsx` + `helpGuide.ts`) with bilingual step-by-step workflows and CLI cross-links. | 应用内 Help 页（中英文分步指南，链至各功能页与 CLI）。 |
| Executable jobs | `POST /api/jobs` for backtest, walk_forward_oos, and paper_export with progress polling. | `POST /api/jobs` 提交回测、Walk-forward OOS、论文导出并轮询进度。 |
| Presentation pack | `Quant_MAS_ZJU_CS_Premium_PPT.html` (31 slides), script, and `docs/ppt_data` server exports. | Premium PPT（31 页）、讲解稿及 `docs/ppt_data` 实验导出。 |

## MAS Layer Summary / MAS 分层速览

| Layer | Key modules | Role |
|---|---|---|
| L5 Tools | `ToolRegistry`, `BaseTool`, 7 quant tools | Agent 访问 Engine 的唯一入口 |
| L6 Agents | `SupervisorAgent`, `ResearchAgent`, `ReportAgent` | 路由、解读、报告；不下单 |
| L7 Protocol | `ToolPolicy`, MCP adapter, `MCPScheduler` | 白名单鉴权、recipe 调度、audit.jsonl |
| L4 RAG | `ContextBuilder`, `HybridRetriever` | 为 ResearchAgent 装配上下文 |
| L3 Memory | `ExperimentMemory`, `BaselineRegistry` | 实验注册与 baseline 锁定 |

See [docs/index.md](index.md#agent-设计--agent-design) for call flow details.

详见 [docs/index.md](index.md#agent-设计--agent-design) 中的调用链说明。

## Enterprise Design Boundary / 企业级设计边界

The system is intentionally a server-first monolith for v5. It is suitable for internship practice, engineering demonstration, and team review without introducing premature microservices.

v5 有意采用 server-first monolith。它适合实习项目练习、工程展示和团队评审，不提前引入复杂微服务。

Safety is a first-class part of the design:

安全边界是设计的一部分：

- LLM agents do not place live orders.
- LLM 智能体不直接下单。
- No broker/order endpoint is exposed.
- 不暴露 broker/order 接口。
- Backtest summaries are not OOS conclusions.
- 回测摘要不是 OOS 结论。
- Paper-grade claims must use audited walk-forward OOS metrics.
- 论文级结论必须使用经审计的 Walk-forward OOS 指标。
- Every trading candidate must pass backtest, risk check, audit log, and human confirmation.
- 每个交易候选都必须经过回测、风险检查、审计日志和人工确认。

## Recommended Server Shape / 推荐服务器形态

| Layer | Recommended v5 setup | 中文 |
|---|---|---|
| Frontend | Build React assets and serve through Nginx/Caddy or the provided frontend image. | 构建 React 静态资源，并通过 Nginx/Caddy 或前端镜像托管。 |
| Backend | Run FastAPI with `QUANT_MAS_AUTH_MODE=api_key`. | 使用 `QUANT_MAS_AUTH_MODE=api_key` 运行 FastAPI。 |
| Artifacts | Point artifact env variables to server output directories. | 将产物环境变量指向服务器输出目录。 |
| Data | Keep local files as default; enable Postgres/pgvector/Neo4j only when available. | 默认使用本地文件；只有在可用时启用 Postgres/pgvector/Neo4j。 |
| Logs | Write backend audit JSONL outside public static directories. | 将后端审计 JSONL 写到公网静态目录之外。 |
| Final verification | Cursor/server should run npm build, browser smoke, Docker/compose checks, real artifact smoke, and full pytest. | Cursor/服务器侧负责 npm build、浏览器 smoke、Docker/compose 检查、真实产物 smoke 和全量 pytest。 |

## Remaining Work / 后续工作

The main remaining work is environment validation, not architecture invention: run the dashboard against the server backend, validate real artifacts, verify optional database connections, and capture screenshots for presentation.

后续主要是环境验证，而不是重新发明架构：让仪表盘连接服务器后端、验证真实产物、验证可选数据库连接，并为展示准备截图。
