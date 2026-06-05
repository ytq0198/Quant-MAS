# Quant MAS v5 Backend

FastAPI backend skeleton for the Quant MAS v5 full-stack phase.

Quant MAS v5 全栈阶段的 FastAPI 后端骨架。

## Run Locally / 本地运行

```bash
python -m pip install -e ".[api]"
python -m uvicorn backend.app:app --reload
```

## Current Endpoints / 当前接口

| Endpoint | English | 中文 |
|---|---|---|
| `GET /api/status` | Returns project status, baseline metadata, safety boundaries, and planned UI modules. | 返回项目状态、基线元数据、安全边界和规划中的 UI 模块。 |
| `GET /api/agents` | Lists mock-safe research agents. | 列出 mock-safe 研究智能体。 |
| `POST /api/agents/run` | Runs a controlled mock-safe agent task. | 运行受控的 mock-safe 智能体任务。 |
| `GET /api/tools` | Lists controlled quant tools and allowed operations. | 列出受控量化工具和允许操作。 |
| `GET /api/memory/search?q=...` | Searches local fixture research memory. | 检索本地夹具研究记忆。 |
| `GET /api/backtests/{id}` | Returns a research-only backtest summary fixture. | 返回仅用于研究展示的回测摘要夹具。 |
| `GET /api/oos/{id}` | Returns the audited walk-forward OOS baseline summary. | 返回经过审计的 Walk-forward 样本外基线摘要。 |
| `GET /api/risk/{id}` | Returns risk review gates and human confirmation requirements. | 返回风险审查关卡和人工确认要求。 |
| `GET /api/database/status` | Returns optional database backend readiness metadata. | 返回可选数据库后端准备状态元数据。 |
| `GET /api/deployment/status` | Returns deployment skeleton metadata and artifacts. | 返回部署骨架元数据和产物列表。 |
| `GET /api/experiments` | Lists artifact-backed experiment records with fallback baseline. | 列出产物驱动的实验记录，并支持基线回退。 |
| `GET /api/experiments/{id}` | Returns one artifact-backed experiment record. | 返回单个产物驱动的实验记录。 |
| `GET /api/artifacts/paper` | Lists paper artifacts from the configured paper directory. | 从配置的论文产物目录列出论文产物。 |
| `GET /api/audit/logs` | Lists JSONL audit events from the configured audit directory. | 从配置的审计目录列出 JSONL 审计事件。 |
| `GET /api/auth/me` | Returns the current auth mode, role, and key fingerprint. | 返回当前认证模式、角色和 key 指纹。 |
| `POST /api/auth/validate-key` | Validates the current API key. | 验证当前 API key。 |
| `GET /api/review/queue` | Lists human review items. | 列出人工审查项。 |
| `GET /api/review/{id}` | Returns one human review item. | 返回单个人工审查项。 |
| `POST /api/review/{id}/approve` | Approves a review item; requires reviewer+. | 批准审查项，需要 reviewer+。 |
| `POST /api/review/{id}/reject` | Rejects a review item; requires reviewer+. | 拒绝审查项，需要 reviewer+。 |
| `GET /api/jobs` | Lists lightweight job statuses. | 列出轻量任务状态。 |
| `GET /api/jobs/{id}` | Returns one job and events. | 返回单个任务及事件。 |
| `GET /api/database/tables` | Lists optional database table readiness. | 列出可选数据库表准备状态。 |
| `GET /api/rag/documents` | Lists fallback or configured RAG documents. | 列出回退或配置的 RAG 文档。 |
| `GET /api/rag/query` | Returns fallback or configured RAG query results. | 返回回退或配置的 RAG 查询结果。 |
| `GET /api/graph/relationships` | Returns optional graph relationship metadata. | 返回可选图谱关系元数据。 |

## Safety / 安全边界

The backend is an API boundary around Quant MAS core services. It must not expose broker, order, secrets, shell, or live-trading paths.

后端是 Quant MAS 核心服务外侧的 API 边界，不应暴露 broker、order、secrets、shell 或实盘交易路径。

Phase 2 uses local fixtures and controlled metadata. It is intended for UI/API integration before connecting real Agent, Tool, Memory, and RAG backends.

Phase 2 使用本地夹具和受控元数据，目的是先完成 UI/API 联调，再接入真实 Agent、Tool、Memory 和 RAG 后端。

Phase 3 adds Backtest, OOS, and Risk summary endpoints. Backtest summaries are marked as non-OOS, while `EXP-20260602-008` is marked as the audited OOS baseline.

Phase 3 增加 Backtest、OOS 和 Risk 摘要接口。回测摘要被标注为非 OOS，而 `EXP-20260602-008` 被标注为经过审计的 OOS 基线。

Phase 4 adds optional database and deployment status endpoints. Postgres, pgvector, and Neo4j are documented as optional services, while local files remain the default test-safe backend.

Phase 4 增加可选数据库和部署状态接口。Postgres、pgvector 和 Neo4j 被记录为可选服务，本地文件仍是默认的测试安全后端。

Phase 5 adds server-ready artifact APIs. On the server, set `QUANT_MAS_ARTIFACT_ROOT`, `QUANT_MAS_EXPERIMENT_MEMORY_PATH`, `QUANT_MAS_PAPER_DIR`, or `QUANT_MAS_AUDIT_DIR` to point the backend at real experiment outputs.

Phase 5 增加服务器可用的产物 API。在服务器上可设置 `QUANT_MAS_ARTIFACT_ROOT`、`QUANT_MAS_EXPERIMENT_MEMORY_PATH`、`QUANT_MAS_PAPER_DIR` 或 `QUANT_MAS_AUDIT_DIR`，让后端读取真实实验输出。

## Server Artifact Environment / 服务器产物环境变量

```bash
set QUANT_MAS_ARTIFACT_ROOT=D:\path\to\Quant-MAS
set QUANT_MAS_EXPERIMENT_MEMORY_PATH=D:\path\to\outputs\reports\experiments.json
set QUANT_MAS_PAPER_DIR=D:\path\to\outputs\paper
set QUANT_MAS_AUDIT_DIR=D:\path\to\outputs\pipelines
```

On Linux servers, use `export` instead of `set`.

Linux 服务器使用 `export` 替代 `set`。

## Auth / RBAC / Audit / 认证、权限与审计

Local development defaults to open mode. Server deployments should use api_key mode.

本地开发默认使用 open mode。服务器部署建议使用 api_key mode。

```bash
export QUANT_MAS_AUTH_MODE=api_key
export QUANT_MAS_API_KEYS="viewer-secret:viewer,research-secret:researcher,reviewer-secret:reviewer,admin-secret:admin"
export QUANT_MAS_AUDIT_WRITE_PATH=/opt/quant-mas/logs/backend_audit.jsonl
```

Use the following request header:

使用以下请求头：

```text
X-Quant-MAS-Key: <api-key>
```

Protected examples:

受保护示例：

- `POST /api/agents/run` requires `researcher` or higher.
- `POST /api/agents/run` 需要 `researcher` 或更高角色。
- `GET /api/audit/logs` requires `reviewer` or higher.
- `GET /api/audit/logs` 需要 `reviewer` 或更高角色。

Raw API keys must not be written to audit logs.

审计日志不得写入明文 API key。

## Human Review and Jobs / 人工审查与任务

Phase 7 adds fallback-safe review and job APIs. They are intended to model enterprise workflow gates before adding Redis/Celery or database-backed queues.

Phase 7 增加 fallback-safe 的审查和任务 API。它们用于在引入 Redis/Celery 或数据库队列前，先表达企业级工作流关卡。

Review decisions do not enable live trading.

审查决策不会启用实盘交易。

## Optional RAG / Database / Graph / 可选 RAG、数据库与图谱

Phase 8 adds optional status and fallback endpoints for Postgres, pgvector, RAG, and Neo4j. Local file mode remains the default.

Phase 8 增加 Postgres、pgvector、RAG 和 Neo4j 的可选状态与回退接口。本地文件模式仍是默认模式。

```bash
export QUANT_MAS_STORAGE_MODE=local_files
export VECTOR_STORE=in_memory
export POSTGRES_DSN=
export PGVECTOR_DSN=
export NEO4J_URI=
```

These services are optional and not required for pytest.

这些服务都是可选项，不是 pytest 的强制依赖。

## Observability / 可观测性

Phase 9 adds lightweight observability endpoints for server smoke tests. They are intentionally safe for local development and do not expose raw secrets.

Phase 9 增加轻量可观测性接口，用于服务器 smoke 测试。它们对本地开发保持安全，并且不会暴露明文密钥。

```text
GET /api/health
GET /api/health/deep
GET /api/metrics/summary
GET /api/logs/recent
GET /api/config/effective
```

`/api/config/effective` must redact API keys and secret-like values.

`/api/config/effective` 必须脱敏 API Key 和类似密钥的值。
