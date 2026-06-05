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

## Safety / 安全边界

The backend is an API boundary around Quant MAS core services. It must not expose broker, order, secrets, shell, or live-trading paths.

后端是 Quant MAS 核心服务外侧的 API 边界，不应暴露 broker、order、secrets、shell 或实盘交易路径。

Phase 2 uses local fixtures and controlled metadata. It is intended for UI/API integration before connecting real Agent, Tool, Memory, and RAG backends.

Phase 2 使用本地夹具和受控元数据，目的是先完成 UI/API 联调，再接入真实 Agent、Tool、Memory 和 RAG 后端。
