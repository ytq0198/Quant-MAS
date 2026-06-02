# Quant MAS 架构

更新时间：2026-06-01（Prompt 13 文档收口）

Quant MAS 采用「确定性量化引擎 + 轻量 Agent 编排 + Memory/RAG」架构。Agent 不替代回测、训练、风控和执行，也不允许直接实盘下单。

## 核心边界

- **Quant Engine Layer**：确定性计算（数据、特征、模型、策略、回测、风控）。
- **Tool Layer**：将引擎能力封装为 Agent 可调用工具。
- **Agent Layer**：规则路由、编排、报告和解释（当前不调用真实 LLM）。
- **Memory Layer**：实验元数据、产物路径；TradeMemory 空壳（Paper Trading 预留）。
- **RAG Layer**：关键词文档检索（无向量库）。
- LLM Agent **不允许**直接实盘下单。
- 所有交易信号须经过回测、风控、审计和人工确认。

## 当前架构图

```text
Quant MAS
├── Quant Engine Layer
│   ├── data          ParquetStorage, DataCatalog, fetchers, validate_ohlcv
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
└── RAG Layer
    document_loader, simple_retriever（关键词检索）
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
- **TradeMemory**：append-only JSONL（第五～六阶段预留）
- **SimpleRetriever**：从 docs/、outputs/reports/ 关键词检索

## 测试与部署

- **pytest**：**98 passed**（本地 + 服务器，2026-06-01）
- **服务器**：`/mnt/localDisk3/weizian/Quant-MAS`，conda `quant-mas`，Python 3.11.15
- **GitHub**：https://github.com/ytq0198/Quant-MAS

## 后续计划（暂缓）

- **第五阶段**：LangGraph 流程编排
- **第六阶段**：Paper Trading（仍不做实盘）
