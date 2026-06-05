# Quant MAS v5 Full-stack Quick Start / 全栈快速开始

This document describes the Phase 1-10 full-stack skeleton: a FastAPI backend, React + Vite dashboard, mock-safe Agent/Tool/Memory APIs, Backtest/OOS/Risk summaries, server-ready artifacts, API key/RBAC, human review, optional RAG/database/graph, observability, and enterprise handoff docs.

本文档说明 Phase 1-10 全栈骨架：FastAPI 后端、React + Vite 仪表盘、mock-safe Agent/Tool/Memory API、Backtest/OOS/Risk 摘要、服务器产物 API、API Key/RBAC、人工审核、可选 RAG/数据库/图谱、可观测性和企业级交接文档。

---

## 1. Backend / 后端

Install the API extras and start the backend from the repository root.

在仓库根目录安装 API 可选依赖并启动后端。

```bash
python -m pip install -e ".[api]"
python -m uvicorn backend.app:app --reload
```

Default backend URL:

默认后端地址：

```text
http://127.0.0.1:8000/api/status
```

---

## 2. Frontend / 前端

Start the frontend from the `frontend/` directory.

进入 `frontend/` 目录启动前端。

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL:

默认前端地址：

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

Vite 开发服务器会把 `/api` 代理到 `http://127.0.0.1:8000`。

---

## 3. Phase 1 Scope / Phase 1 范围

| Item | English | 中文 |
|---|---|---|
| Backend | `GET /api/status` returns project status, baselines, safety boundaries, and planned UI modules. | `GET /api/status` 返回项目状态、基线、安全边界和规划 UI 模块。 |
| Frontend | Dashboard fetches `/api/status` and displays the v5 enterprise preview. | Dashboard 请求 `/api/status` 并展示 v5 企业级预览。 |
| Fallback | UI has a local fallback payload for frontend-only iteration. | UI 带有本地 fallback 数据，方便前端单独迭代。 |
| Safety | The skeleton keeps the no direct live trading boundary visible. | 骨架持续展示不直接实盘交易的边界。 |

---

## 4. Phase 2 Scope / Phase 2 范围

| Endpoint | English | 中文 |
|---|---|---|
| `GET /api/agents` | Lists mock-safe agents for the Agent Console. | 为 Agent Console 列出 mock-safe 智能体。 |
| `POST /api/agents/run` | Returns a controlled, auditable mock agent response. | 返回受控、可审计的 mock 智能体响应。 |
| `GET /api/tools` | Lists controlled tools and allowed operations. | 列出受控工具和允许操作。 |
| `GET /api/memory/search?q=OOS` | Searches local fixture memory for UI/RAG integration. | 检索本地夹具记忆，用于 UI/RAG 联调。 |

The Phase 2 APIs are intentionally mock-safe. They do not call a real broker, send orders, access secrets, or depend on a real LLM service.

Phase 2 API 有意保持 mock-safe：不调用真实 broker，不发送订单，不访问 secrets，也不依赖真实 LLM 服务。

---

## 5. Phase 3 Scope / Phase 3 范围

| Endpoint | English | 中文 |
|---|---|---|
| `GET /api/backtests/demo-backtest` | Returns a research-only, non-OOS backtest summary. | 返回仅用于研究展示的非 OOS 回测摘要。 |
| `GET /api/oos/EXP-20260602-008` | Returns the audited OOS baseline with Sharpe `0.586` and 19 windows. | 返回经过审计的 OOS 基线，Sharpe 为 `0.586`，共 19 个窗口。 |
| `GET /api/risk/demo-risk` | Returns risk gates and human confirmation requirements. | 返回风险关卡和人工确认要求。 |

Backtest summaries are displayed for workflow understanding only. Paper-grade conclusions must use audited walk-forward OOS metrics.

回测摘要只用于理解流程。论文级结论必须使用经过审计的 Walk-forward 样本外指标。

---

## 6. Phase 4 Scope / Phase 4 范围

| Endpoint / Artifact | English | 中文 |
|---|---|---|
| `GET /api/database/status` | Lists local files, SQLite, Postgres, pgvector, and Neo4j as optional backends. | 将本地文件、SQLite、Postgres、pgvector 和 Neo4j 列为可选后端。 |
| `GET /api/deployment/status` | Lists frontend/backend stacks and Docker artifacts. | 列出前后端技术栈和 Docker 产物。 |
| `docker-compose.yml` | Provides backend, frontend, Postgres/pgvector, and Neo4j service skeletons. | 提供 backend、frontend、Postgres/pgvector 和 Neo4j 服务骨架。 |
| `Dockerfile.backend` | Builds the FastAPI backend image. | 构建 FastAPI 后端镜像。 |
| `Dockerfile.frontend` | Builds the React frontend and serves it with Nginx. | 构建 React 前端并用 Nginx 托管。 |

Postgres, pgvector, and Neo4j are optional. Local files remain the default backend for tests and lightweight development.

Postgres、pgvector 和 Neo4j 都是可选项。本地文件仍是测试和轻量开发的默认后端。

---

## 7. Phase 5 Server Backend Mode / Phase 5 服务器后端模式

| Endpoint | English | 中文 |
|---|---|---|
| `GET /api/experiments` | Lists experiments from configured server artifacts, with fallback baseline. | 从配置的服务器产物列出实验，并支持基线回退。 |
| `GET /api/experiments/{id}` | Returns one experiment record. | 返回单个实验记录。 |
| `GET /api/artifacts/paper` | Lists paper artifacts from `outputs/paper` or configured path. | 从 `outputs/paper` 或配置路径列出论文产物。 |
| `GET /api/audit/logs` | Lists JSONL audit events from `outputs/pipelines` or configured path. | 从 `outputs/pipelines` 或配置路径列出 JSONL 审计事件。 |

Server environment variables:

服务器环境变量：

```bash
export QUANT_MAS_ARTIFACT_ROOT=/path/to/Quant-MAS
export QUANT_MAS_EXPERIMENT_MEMORY_PATH=/path/to/outputs/reports/experiments.json
export QUANT_MAS_PAPER_DIR=/path/to/outputs/paper
export QUANT_MAS_AUDIT_DIR=/path/to/outputs/pipelines
```

Local development can omit these variables. The API will return fallback-safe baseline or empty artifact lists.

本地开发可以不设置这些变量。API 会返回安全回退基线或空产物列表。

---

## 8. Phase 6 Auth / RBAC / Audit / Phase 6 认证、权限与审计

Local mode can run without API keys:

本地模式可以不配置 API key：

```bash
export QUANT_MAS_AUTH_MODE=open
```

Server mode should use API keys:

服务器模式建议使用 API key：

```bash
export QUANT_MAS_AUTH_MODE=api_key
export QUANT_MAS_API_KEYS="viewer-secret:viewer,research-secret:researcher,reviewer-secret:reviewer,admin-secret:admin"
```

Frontend users can enter the key in the Dashboard API Access panel. The frontend stores it in browser localStorage and sends `X-Quant-MAS-Key` with API requests.

前端用户可以在 Dashboard 的 API Access 面板输入 key。前端会把 key 存入浏览器 localStorage，并在 API 请求中发送 `X-Quant-MAS-Key`。

Protected endpoints:

受保护接口：

| Endpoint | Required role | 中文 |
|---|---|---|
| `POST /api/agents/run` | `researcher+` | 运行受控智能体任务。 |
| `GET /api/audit/logs` | `reviewer+` | 查看审计日志。 |

---

## 9. Phase 7 Human Review + Job Queue / Phase 7 人工审查与任务队列

Phase 7 adds fallback-safe review and job APIs:

Phase 7 增加 fallback-safe 的审查和任务 API：

```text
GET  /api/review/queue
GET  /api/review/{id}
POST /api/review/{id}/approve
POST /api/review/{id}/reject
GET  /api/jobs
GET  /api/jobs/{id}
```

Review decisions require `reviewer+` in api_key mode and may write audit JSONL when `QUANT_MAS_AUDIT_WRITE_PATH` is configured.

在 api_key 模式下，审查决策需要 `reviewer+` 权限；配置 `QUANT_MAS_AUDIT_WRITE_PATH` 后可写入 JSONL 审计事件。

---

## 10. Phase 8 Optional RAG / DB / Graph / Phase 8 可选 RAG、数据库与图谱

Phase 8 adds fallback-safe optional endpoints:

Phase 8 增加 fallback-safe 的可选接口：

```text
GET /api/database/tables
GET /api/rag/documents
GET /api/rag/query?q=...
GET /api/graph/relationships
```

Local file mode remains the default. Postgres, pgvector, and Neo4j are server enhancements.

本地文件模式仍是默认模式。Postgres、pgvector 和 Neo4j 是服务器增强项。

---

## 11. Phase 9 Observability / Phase 9 可观测性

Phase 9 adds server smoke-test endpoints:

Phase 9 增加服务器 smoke 测试接口：

```text
GET /api/health
GET /api/health/deep
GET /api/metrics/summary
GET /api/logs/recent
GET /api/config/effective
```

These endpoints help Cursor/server verify that the backend is alive, optional services are visible, logs are readable, and secrets are redacted.

这些接口帮助 Cursor/服务器验证后端存活、可选服务可见、日志可读、密钥已脱敏。

---

## 12. Phase 10 Enterprise Handoff / Phase 10 企业级交接

Phase 10 adds the handoff documents for enterprise-style review:

Phase 10 增加企业级评审交接文档：

```text
docs/v5_enterprise_overview.md
docs/api_reference.md
docs/security_model.md
docs/metric_family_policy.md
docs/demo_script.md
docs/server_deployment.md
docs/server_env.md
docs/release_checklist.md
```

Codex-owned local checks focus on targeted backend tests and static scans. Cursor/server-owned checks include `npm run build`, browser screenshots, Docker/compose, real artifact smoke, optional database connections, and full pytest.

Codex 负责本地目标后端测试和静态扫描。Cursor/服务器负责 `npm run build`、浏览器截图、Docker/compose、真实产物 smoke、可选数据库连接和全量 pytest。
