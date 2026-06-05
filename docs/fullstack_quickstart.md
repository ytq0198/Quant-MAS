# Quant MAS v4 Full-stack Quick Start / 全栈快速开始

This document describes the Phase 1-5 full-stack skeleton: a FastAPI backend, status endpoint, mock-safe Agent/Tool/Memory APIs, Backtest/OOS/Risk summary APIs, optional database/deployment status APIs, server-ready artifact APIs, and a React + Vite dashboard.

本文档说明 Phase 1-5 全栈骨架：FastAPI 后端、状态接口、mock-safe Agent/Tool/Memory API、Backtest/OOS/Risk 摘要 API、可选数据库/部署状态 API、服务器可用产物 API 和 React + Vite 仪表盘。

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
| Frontend | Dashboard fetches `/api/status` and displays the v4 full-stack preview. | Dashboard 请求 `/api/status` 并展示 v4 全栈预览。 |
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

## 8. Next Phases / 下一阶段

- Later: dedicated charts, audit log pages, human review queues, and real ExperimentMemory integration.
- 后续：专门图表、审计日志页面、人工审查队列和真实 ExperimentMemory 集成。
