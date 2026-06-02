# Quant MAS 开发进度

更新时间：2026-06-02（Plus M1 研究基线本地验收）

## 当前所处阶段

**Prompt 1–20 主链路 ✅ 已完成**（第零～四阶段）。

**Plus v2**：**M1 研究基线 ✅ 本地验收**（102 passed，EXP-20260602-009）；服务器 pull / 比较表 **待验证**（EXP-TODO-008）。

第五～六阶段见 [项目plus设计.md](../项目plus设计.md)（M4 LangGraph / M7 模拟，非实盘）。

## 阶段总览

| 阶段 | 名称 | 状态 | 关键交付 |
|------|------|------|----------|
| 第零阶段 | 项目骨架 | ✅ | Prompt 1 |
| 第一阶段 | 量化核心 MVP | ✅ | Prompt 2–7、11–12、14 |
| 第二阶段 | 机器学习实验 | ✅ | Prompt 15–17、15b |
| 第二阶段扩展 | 基础风控 | ✅ | Prompt 18 |
| 第三阶段 | Agent 增强 | ✅ | Prompt 8–10、19 |
| 第四阶段 | Memory + RAG | ✅ | Prompt 20 |
| **Plus M1** | 研究基线 | ✅ 本地 | BaselineRegistry、compare_experiments（EXP-20260602-009） |
| **Plus M2** | 数据扩展 | 📋 待做 | 见 项目plus设计.md |
| 第五～六阶段 | 编排 / RL 模拟 | 📋 | Plus M4 / M7 |

## Quant MAS v2：M1 研究基线

> 设计细节见 [项目plus设计.md §M1](../项目plus设计.md#m1研究基线与实验规范)；实验规范见 [docs/research_protocol.md](research_protocol.md)。

### 目标

建立统一实验基线管理，**后续所有新实验必须与 EXP-20260602-008 Walk-forward OOS baseline 对比**后再写结论。

### 已交付（代码）

| 组件 | 路径 | 说明 |
|------|------|------|
| BaselineRegistry | `src/quant_mas/research/baseline.py` | `BaselineRun`、`add_baseline`、`compare_runs`、`get_best("oos.sharpe")` |
| MetricsTable | `src/quant_mas/research/metrics_table.py` | `collect_experiment_metrics`、`build_comparison_table` |
| CLI | `scripts/compare_experiments.py` | 从 ExperimentMemory 输出 `comparison.csv` / `comparison.md` |
| 实验规范 | `docs/research_protocol.md` | 必填字段、OOS 主指标、比较族 |
| 测试 | `tests/test_research_baseline.py` | 4 项（嵌套 metric、空 memory） |

### 状态

| 项目 | 状态 | 备注 |
|------|------|------|
| M1 模块代码 | ✅ | baseline / metrics_table / compare_experiments / research_protocol |
| `python scripts/compare_experiments.py --help` | ✅ | EXP-20260602-009 |
| `tests/test_research_baseline.py` | ✅ **4 passed** | 嵌套 metric、best baseline、CLI 输出 |
| 全量 pytest（本地） | ✅ **102 passed** | +4（98→102），EXP-20260602-009 |
| 全量 pytest（服务器） | 待验证 | 上次 **98 passed**（EXP-20260601-014） |
| 服务器 `compare_experiments` + 比较表核对 | 待验证 | EXP-TODO-008 |

### 下一步

1. git push → 服务器 pull → `python -m pytest -v`（预期 **102 passed**）
2. 服务器 `compare_experiments.py` → 更新 `experiment_log.md` 比较表
3. 进入 **M2 数据扩展**

### OOS 主 baseline（不可遗忘）

| 实验 | 主指标 | 用途 |
|------|--------|------|
| **EXP-20260602-008** | **OOS sharpe 0.586** | 论文 / 报告 **唯一主指标** |
| EXP-20260602-005 | sharpe 2.78（单段 ML） | ⚠️ in-sample，**禁止**与 OOS 混比 |
| EXP-20260601-004 | ma_cross sharpe ≈ 1.00 | 传统策略参考 |
| EXP-20260601-006 | test AUC 0.466 | ML 训练参考 |

## Prompt 任务状态

- [x] Prompt 1–10：骨架 → Agent Core
- [x] Prompt 11–12：端到端 pipeline + 测试
- [x] Prompt 13：文档收口（2026-06-01，EXP-20260601-015）
- [x] Prompt 14：服务器部署脚本
- [x] Prompt 15–17、15b：ML 训练 / 回测 / walk-forward
- [x] Prompt 18：基础风控
- [x] Prompt 19：Supervisor 7 类路由
- [x] Prompt 20：Memory + RAG
- [x] **Plus M1**：研究基线与实验规范（EXP-20260602-009，**102 passed**）

## 当前 pytest 状态

| 环境 | Python | 结果 | 日期 | 实验 |
|------|--------|------|------|------|
| 本地 Windows | 3.11+ | **102 passed** | 2026-06-02 | EXP-20260602-009 |
| 服务器 a6000-9961 | 3.11.15 | **98 passed**（1.93s） | 2026-06-01 | EXP-20260601-014（M1 pull 后待验证） |

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
python scripts/compare_experiments.py --help
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

### Research Layer（Plus M1）

- BaselineRegistry / BaselineRun：命名 baseline 与实验 run 的统一比较
- MetricsTable：`collect_experiment_metrics` → `build_comparison_table`
- `compare_experiments.py`：从 ExperimentMemory 导出 CSV / Markdown 比较表
- **规则**：新实验结论须与 **EXP-20260602-008 OOS sharpe 0.586** 对比（见 `research_protocol.md`）

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
4. **Plus M1**：任何新实验写入 ExperimentMemory 后，须用 `compare_experiments.py` 生成比较表，并与 **EXP-20260602-008** 对照后再下结论。

## 后续工作

- **M1 服务器**：pull → pytest **102** → `compare_experiments.py`（EXP-TODO-008）
- **M2 起**：见 [项目plus设计.md](../项目plus设计.md)（数据扩展 → RAG v2 → LangGraph …）
- 科研：特征/模型调参、更多 walk-forward 窗口（**必须标注 OOS**）
- 可选：CPU 对照 `server_lgbm_cpu_001`（EXP-TODO-006）
