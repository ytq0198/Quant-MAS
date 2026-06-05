# Quant MAS v4 Full-stack Quick Start / 全栈快速开始

This document describes the Phase 1-2 full-stack skeleton: a FastAPI backend, status endpoint, mock-safe Agent/Tool/Memory APIs, and a React + Vite dashboard.

本文档说明 Phase 1-2 全栈骨架：FastAPI 后端、状态接口、mock-safe Agent/Tool/Memory API 和 React + Vite 仪表盘。

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

## 5. Next Phases / 下一阶段

- Phase 3: Backtest / Walk-forward / Risk visualization.
- Phase 3：Backtest / Walk-forward / Risk 可视化。

- Phase 4: Database / RAG / server deployment.
- Phase 4：数据库 / RAG / 服务器部署。
