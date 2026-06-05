# Quant MAS v5 UI Design / UI 设计

This document records the v5 enterprise UI refactor: a multi-page research workbench instead of a single long dashboard.

本文档记录 v5 企业级 UI 重构：多页面研究工作台，而非单页长列表仪表盘。

---

## Design Goal / 设计目标

The UI should behave like a **professional quantitative research workbench**, not a marketing page or live-trading console. Users navigate by module via a fixed sidebar; the Overview page shows only the most important summary information.

UI 应像**专业量化研究工作台**，而非营销页或实盘控制台。用户通过左侧固定 Sidebar 按模块导航；Overview 首页只展示最关键摘要。

---

## Layout / 布局结构

| Area | English | 中文 |
|---|---|---|
| Sidebar | Fixed left navigation: Overview, Experiments, Backtests, OOS, Risk, Agents, Tools, Memory/RAG, Audit, Paper, Database, Observability, Settings | 左侧固定导航 |
| Header | Project name, page title, backend connection badge, auth mode, safety badge, refresh | 顶栏：项目名、页面标题、连接状态、认证模式、安全标记 |
| Main Content | One module per page (React state routing, no react-router required) | 每页一个模块 |
| Context Panel | Safety boundary, current experiment, metric family reminder (desktop) | 右侧上下文面板（桌面端） |

---

## Pages / 页面

| Page | Purpose |
|---|---|
| Overview | Hero summary, KPI row, workflow stepper, safety card, module shortcuts |
| Experiments | Experiment registry table + selected experiment summary |
| Backtests | Research-only backtest summary with non-OOS warning |
| Walk-forward OOS | Paper-grade OOS metrics (`oos.*`) |
| Risk Review | Checklist, review queue, human confirmation gates |
| Agents | Agent cards + mock run console |
| Tools | Tool catalog + ToolPolicy allowed/denied badges |
| Memory / RAG | Search input, results, metric family separation reminder |
| Audit Logs | Event table or empty state |
| Paper Artifacts | Export jobs / files or empty state |
| Database | Backend mode, vector store, graph, table chips |
| Observability | Health, jobs, metrics, logs, effective config |
| Settings | API key, backend URL, env reminder, research disclaimer |

API Key input lives **only** on Settings — not on Overview.

API Key 输入框**仅**在 Settings 页面，不在首页。

---

## Visual System / 视觉系统

- Background: `#F6F8FB`
- Surface: `#FFFFFF`
- Primary: `#0F766E` / dark sidebar `#0F172A`
- Accent: `#2563EB`
- Border: `#E2E8F0`
- Font: Inter / system-ui stack
- Cards: 14px radius, light shadow, 20–24px padding

### Metric family badges

| Family | Color |
|---|---|
| `oos.*` | Blue |
| `simulation.*` | Purple |
| `training.*` | Gray |
| `population.*` | Orange |
| `audit.*` | Green |

### Safety copy (required)

- Live trading disabled
- Human review required
- OOS only for paper conclusions
- No profit guarantee, auto trading, or financial advice language

---

## File Structure / 文件结构

```
frontend/src/
├── App.tsx
├── main.tsx
├── styles.css
├── api/           # client.ts + phase2–phase9
├── components/    # AppShell, Sidebar, Header, Card, Badge, …
├── pages/         # Overview, Experiments, Backtests, …
├── hooks/         # useDashboardData.ts
└── types/         # navigation.ts
```

---

## API Integration / API 对接

All existing backend endpoints are preserved. The shared hook `useDashboardData` loads data in parallel; on failure the UI falls back to local fixtures without breaking the page.

保留全部现有后端 API。`useDashboardData` 并行加载；失败时优雅回退到本地 fixture。

Key endpoints: `/api/status`, `/api/agents`, `/api/tools`, `/api/memory/search`, `/api/backtests/{id}`, `/api/oos/{id}`, `/api/risk/{id}`, `/api/database/status`, `/api/deployment/status`, plus Phase 5–9 artifact and observability routes.

---

## Responsive / 响应式

- Desktop: sidebar + main + context panel
- Tablet: collapsed sidebar, context panel hidden
- Mobile: stacked layout, compact navigation

---

## Validation / 验收

1. `npm run build` passes
2. No backend logic changes required
3. Overview is concise; modules are split into pages
4. Safety boundary visible; API key only in Settings
5. Fallback mode clearly indicated

---

## Research Console (v5.1+) / 研究控制台

The UI is now an **actionable research console**, not only a read-only dashboard.

UI 现已升级为**可执行的研究控制台**，不仅是只读仪表盘。

### Submit jobs / 提交任务

| UI Page | Action | Backend |
|---|---|---|
| Experiments / Backtests | Run backtest job | `POST /api/jobs` type `backtest` |
| Walk-forward OOS | Run OOS job | `POST /api/jobs` type `walk_forward_oos` |
| Paper Artifacts | Export paper job | `POST /api/artifacts/export` |
| Risk Review | Approve / Reject | `POST /api/review/{id}/approve` |
| Observability | Refresh job list | `GET /api/jobs` |

Jobs execute Quant Engine tasks in background threads (`BacktestTool`, walk-forward, paper export).

任务在后台线程中调用 Quant Engine（`BacktestTool`、walk-forward、论文导出）。

### Prerequisites / 前置条件

1. Backend running with `QUANT_MAS_ARTIFACT_ROOT` pointing to repo root
2. Market data: `data/raw/market_data.parquet` (run `scripts/download_data.py` first)
3. OOS jobs need `data/features/features.parquet` (run feature pipeline first)
4. API key with `researcher` role when `QUANT_MAS_AUTH_MODE=api_key`

### After job completes / 任务完成后

- Backtest results → `outputs/reports/backtest_latest/`
- Experiments registry updates → `outputs/reports/experiments.json`
- UI auto-refreshes summaries on completion
