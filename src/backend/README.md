# Quant MAS v4 Backend

FastAPI backend skeleton for the Quant MAS v4 full-stack phase.

Quant MAS v4 全栈阶段的 FastAPI 后端骨架。

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

## Safety / 安全边界

The backend is an API boundary around Quant MAS core services. It must not expose broker, order, secrets, shell, or live-trading paths.

后端是 Quant MAS 核心服务外侧的 API 边界，不应暴露 broker、order、secrets、shell 或实盘交易路径。

Phase 2 uses local fixtures and controlled metadata. It is intended for UI/API integration before connecting real Agent, Tool, Memory, and RAG backends.

Phase 2 使用本地夹具和受控元数据，目的是先完成 UI/API 联调，再接入真实 Agent、Tool、Memory 和 RAG 后端。

Phase 3 adds Backtest, OOS, and Risk summary endpoints. Backtest summaries are marked as non-OOS, while `EXP-20260602-008` is marked as the audited OOS baseline.

Phase 3 增加 Backtest、OOS 和 Risk 摘要接口。回测摘要被标注为非 OOS，而 `EXP-20260602-008` 被标注为经过审计的 OOS 基线。

Phase 4 adds optional database and deployment status endpoints. Postgres, pgvector, and Neo4j are documented as optional services, while local files remain the default test-safe backend.

Phase 4 增加可选数据库和部署状态接口。Postgres、pgvector 和 Neo4j 被记录为可选服务，本地文件仍是默认的测试安全后端。
