# Quant MAS 开发进度

更新时间：2026-06-01

## 当前所处阶段

**Prompt 1–20 主链路 ✅ 已完成**（第四阶段 Memory/RAG，EXP-20260601-013）。

第五～六阶段（LangGraph / Paper Trading）暂缓。

## Prompt 任务状态

- [x] Prompt 1–10：骨架 → Agent Core
- [x] Prompt 11–14：Pipeline + 服务器部署
- [x] Prompt 15–17、15b：ML 训练 / 回测 / walk-forward
- [x] Prompt 18：基础风控
- [x] Prompt 19：Supervisor 7 类路由
- [x] **Prompt 20**：Memory 增强 + SimpleRetriever
- [ ] Prompt 13：文档收口（可选）

## 当前 pytest 状态

| 环境 | Python | 结果 | 日期 |
|------|--------|------|------|
| 本地 Windows | 3.11+ | **98 passed** | 2026-06-01 |
| 服务器 Linux | 3.11.15 | **98 passed** | 2026-06-01 |

## 当前可用 CLI

```powershell
python scripts/download_data.py --help
python scripts/build_features.py --help
python scripts/run_backtest.py --help
python scripts/train_model.py --help
python scripts/generate_report.py --help
python scripts/run_agent.py --help
python scripts/run_pipeline.py --help
python scripts/run_ml_backtest.py --help
python scripts/run_walk_forward.py --help
```

## 当前已实现能力

- [x] 完整 Quant Engine：数据 → 特征 → 策略 → 回测 → ML → walk-forward OOS
- [x] 风控层 + 7 个 Agent Tools + Supervisor 路由
- [x] ExperimentMemory 查询/搜索/排序 + TradeMemory 空壳
- [x] 关键词 RAG（Document loader + SimpleRetriever）

## 分阶段目标

### 第零～四阶段 ✅

全部完成（Prompt 1–20）。

### 第五～六阶段 ⏸

LangGraph / Paper Trading 暂缓。

## 研究解读

- 报告以 walk-forward **OOS sharpe 0.586** 为准（EXP-20260602-008）。
- Agent 可编排 ML 回测、风控、pipeline；Memory/RAG 可检索实验与文档。
