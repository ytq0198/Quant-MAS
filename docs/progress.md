# Quant MAS 开发进度

更新时间：2026-06-01（Prompt 13 文档收口）

## 当前所处阶段

**Prompt 1–20 主链路 ✅ 已完成**（第零～四阶段）。

第五～六阶段（LangGraph / Paper Trading）**暂缓**。

## 阶段总览

| 阶段 | 名称 | 状态 | 关键交付 |
|------|------|------|----------|
| 第零阶段 | 项目骨架 | ✅ | Prompt 1 |
| 第一阶段 | 量化核心 MVP | ✅ | Prompt 2–7、11–12、14 |
| 第二阶段 | 机器学习实验 | ✅ | Prompt 15–17、15b |
| 第二阶段扩展 | 基础风控 | ✅ | Prompt 18 |
| 第三阶段 | Agent 增强 | ✅ | Prompt 8–10、19 |
| 第四阶段 | Memory + RAG | ✅ | Prompt 20 |
| 第五～六阶段 | 编排 / 模拟交易 | ⏸ | 暂缓 |

## Prompt 任务状态

- [x] Prompt 1–10：骨架 → Agent Core
- [x] Prompt 11–12：端到端 pipeline + 测试
- [x] Prompt 13：文档收口（2026-06-01，EXP-20260601-015）
- [x] Prompt 14：服务器部署脚本
- [x] Prompt 15–17、15b：ML 训练 / 回测 / walk-forward
- [x] Prompt 18：基础风控
- [x] Prompt 19：Supervisor 7 类路由
- [x] Prompt 20：Memory + RAG

## 当前 pytest 状态

| 环境 | Python | 结果 | 日期 | 实验 |
|------|--------|------|------|------|
| 本地 Windows | 3.11+ | **98 passed** | 2026-06-01 | EXP-20260601-013 |
| 服务器 a6000-9961 | 3.11.15 | **98 passed**（1.93s） | 2026-06-01 | EXP-20260601-014 |

命令：`python -m pytest -v`（勿裸敲 `pytest` / `pip`）。

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

### Quant Engine

- 数据：Parquet、Stooq/yfinance、OHLCV 校验
- 特征：技术指标、future label、按 symbol 分组
- 策略 / 回测：MA Cross、MLSignalStrategy、walk-forward OOS
- 模型：LightGBM（CPU + GPU/CUDA）
- 风控：RiskLimits、持仓裁剪/拒绝、回撤守卫

### Agent Layer

- 7 个 Quant Tools + Supervisor 规则路由（中英文关键词）
- 路由：ml_backtest / risk_check / pipeline / backtest / train_model / report / data_summary

### Memory / RAG

- ExperimentMemory：get / search / sort_by_metric / find_best（含嵌套 metric）
- TradeMemory：JSONL 空壳
- SimpleRetriever：关键词检索 docs（无向量库、无 LLM）

## 服务器真实实验（研究用）

| 实验 | 关键结果 | 备注 |
|------|----------|------|
| EXP-20260601-004 | Stooq 6033 rows；ma_cross sharpe ≈ 1.00 | 真实 pipeline |
| EXP-20260601-006 | CPU LightGBM test AUC 0.466 | 过拟合基线 |
| EXP-20260602-004 | GPU LightGBM device=cuda | 见 M-010 |
| EXP-20260602-005 | ML 单段回测 sharpe **2.78** | **非 OOS，勿混用** |
| EXP-20260602-008 | Walk-forward **OOS sharpe 0.586** | **报告主指标** |

## 研究解读

1. 单段 ML 回测 sharpe 2.78 ≫ walk-forward OOS sharpe 0.586 → **论文/报告以 OOS 为准**。
2. OOS auc_mean 0.472 与 val/test AUC ≈ 0.46–0.48 一致；模型调参留作后续研究。
3. Agent 可编排 ML 回测、风控、pipeline；Memory/RAG 可检索历史实验与文档。

## 后续工作

- 科研：特征/模型调参、更多 walk-forward 窗口
- 可选：CPU 对照 `server_lgbm_cpu_001`（EXP-TODO-006）
- 暂缓：第五阶段 LangGraph / 第六阶段 Paper Trading
