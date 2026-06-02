# Quant MAS 架构

更新时间：2026-06-02（Plus M1 Research Layer）

Quant MAS 采用「确定性量化引擎 + 轻量 Agent 编排 + Memory/RAG + **Research 基线层**」架构。Agent 不替代回测、训练、风控和执行，也不允许直接实盘下单。

## 核心边界

- **Quant Engine Layer**：确定性计算（数据、特征、模型、策略、回测、风控）。
- **Tool Layer**：将引擎能力封装为 Agent 可调用工具。
- **Agent Layer**：规则路由、编排、报告和解释（当前不调用真实 LLM）。
- **Memory Layer**：实验元数据、产物路径；TradeMemory 空壳（Paper Trading 预留）。
- **RAG Layer**：关键词文档检索（无向量库）。
- **Research Layer（Plus M1）**：实验基线注册、指标汇总、跨实验比较；**后续实验须与 EXP-20260602-008 OOS baseline 对比**。
- LLM Agent **不允许**直接实盘下单。
- 所有交易信号须经过回测、风控、审计和人工确认。

## 当前架构图

```text
Quant MAS
├── Quant Engine Layer
│   ├── data          ParquetStorage, DataCatalog, fetchers/（M2 子包）, validate_ohlcv
│   ├── features      technical, labels, build_feature_table
│   ├── strategies    MovingAverageCrossStrategy, MLSignalStrategy
│   ├── backtest      BacktestEngine, walk_forward, metrics, report
│   ├── models        LightGBMDirectionModel, time-series helpers
│   ├── risk          RiskLimits, exposure, drawdown_guard
│   ├── utils         device.py（GPU/CUDA）
│   └── pipeline      run_quant_pipeline
│
├── Tool Layer（7 tools）
│   data_summary | backtest | train_model | report
│   risk_check | ml_backtest | pipeline
│
├── Agent Layer
│   Message, MockLLMClient, BaseAgent, ReportAgent
│   SupervisorAgent（规则路由）, AgentEvent 系列
│
├── Memory Layer
│   ExperimentMemory（增强）, TradeMemory（JSONL 空壳）
│
├── RAG Layer
│   document_loader, simple_retriever（关键词检索）
│
└── Research Layer（Plus M1）
    baseline.py          BaselineRun, BaselineRegistry
    metrics_table.py     collect_experiment_metrics, build_comparison_table
    compare_experiments.py   CLI → comparison.csv / comparison.md
    research_protocol.md     实验规范与 OOS 主指标定义
```

## CLI 入口

```text
download_data.py      数据下载（yfinance / Stooq）
merge_parquet.py      合并分年 parquet
build_features.py     特征构建
run_backtest.py       均线策略回测
train_model.py        模型训练（--device auto/cpu/gpu/cuda）
run_ml_backtest.py    ML 信号回测
run_walk_forward.py   Walk-forward 样本外
compare_experiments.py  实验比较表（ExperimentMemory → CSV/MD）
generate_report.py    报告读取/生成
run_agent.py          Supervisor 规则路由
run_pipeline.py       端到端 pipeline
```

## 模块说明

### Quant Engine

| 模块 | 要点 |
|------|------|
| 数据 | Stooq 服务器已验证（EXP-20260601-004）；yfinance 易限流 |
| 回测 | 下一根 bar 成交；commission / slippage |
| ML | Prompt 15 完整 artifacts；GPU/CUDA（M-010） |
| Walk-forward | OOS sharpe **0.586**（EXP-20260602-008） |
| 风控 | 策略只产出 target_weight；风控 clip/reject |

### Tool Layer

工具返回 **摘要 + metrics + 路径**，不返回完整 DataFrame。

### Agent Layer

SupervisorAgent 7 类路由（更具体规则优先，如 ml_backtest 先于 backtest）：

| 关键词示例 | 工具 |
|------------|------|
| ML回测 / ml backtest | ml_backtest |
| 风控 / risk | risk_check |
| 全流程 / pipeline | pipeline |
| 回测 / backtest | backtest |
| 训练 / train | train_model |
| 报告 / report | report |
| 数据 / data | data_summary |

### Memory / RAG

- **ExperimentMemory**：add / list / latest / get / search_by_name / sort_by_metric / find_best
- **TradeMemory**：append-only JSONL（Plus M7 模拟预留）
- **SimpleRetriever**：从 docs/、outputs/reports/ 关键词检索

### Research Layer（Plus M1）

| 组件 | 职责 |
|------|------|
| **BaselineRegistry** | 注册命名 baseline（`BaselineRun`）；`compare_runs()`、`get_best("oos.sharpe")` |
| **MetricsTable** | 从 `ExperimentRecord` 抽取指标 → `build_comparison_table()` |
| **compare_experiments.py** | CLI：读 ExperimentMemory → 写 `outputs/research/comparison.csv` 与 `comparison.md` |
| **research_protocol.md** | 必填实验字段；**论文主指标 = Walk-forward OOS** |

**数据流：**

```text
run_* / train_* / walk_forward
        ↓
ExperimentMemory（metrics 含嵌套 oos.*）
        ↓
collect_experiment_metrics → BaselineRegistry / comparison table
        ↓
与 EXP-20260602-008（OOS sharpe 0.586）对照 → docs/experiment_log.md
```

**比较族（family）**：`ma_cross` | `lightgbm` | `ml_backtest` | `walk_forward` | `other`

**OOS 主 baseline**：EXP-20260602-008，`oos.sharpe = 0.586`。单段 ML 回测（ml_backtest family）**不可**替代 OOS 结论。

## 测试与部署

- **pytest**：本地 **114 passed**（EXP-20260602-011）；服务器 102（M2 pull 后待验证 **114**）
- **服务器**：`/mnt/localDisk3/weizian/Quant-MAS`，conda `quant-mas`，Python 3.11.15
- **GitHub**：https://github.com/ytq0198/Quant-MAS

## 后续计划（Plus v2）

| 模块 | 内容 | 状态 |
|------|------|------|
| **M1** 研究基线 | BaselineRegistry、compare_experiments | ✅ EXP-20260602-009/010 |
| **M2** 数据扩展 | 多数据源 fetcher + registry | ✅ 本地（EXP-20260602-011）；API smoke 待验证 |
| **M3** Memory/RAG v2 | SQLite / 向量检索 | 📋 待做 |
| **M4** LangGraph | 实验性 DAG（不替换 Supervisor） | 📋 待做 |
| **M5–M8** | LLM、文本模型、RL、MCP | 📋 待做 |

详见 [项目plus设计.md](../项目plus设计.md)。
