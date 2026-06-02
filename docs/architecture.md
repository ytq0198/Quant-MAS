# Quant MAS 架构

更新时间：2026-06-01

Quant MAS 当前采用“确定性量化引擎 + 轻量 Agent 编排”的架构。Agent 不替代回测、训练、风控和执行，也不允许直接实盘下单。

## 核心边界

- Quant Engine Layer 负责确定性计算。
- Tool Layer 将确定性能力封装成 Agent 可调用工具。
- Agent Layer 负责规则路由、编排、报告和解释。
- Memory Layer 记录实验元数据和产物路径。
- LLM Agent 不允许直接实盘下单。
- 所有交易信号必须经过回测、风控、审计和人工确认。

## 当前架构图

```text
Quant MAS
├── Quant Engine Layer
│   ├── data
│   │   ├── ParquetStorage
│   │   ├── DataCatalog
│   │   ├── MarketDataFetcher / YFinanceFetcher
│   │   └── validate_ohlcv
│   ├── features
│   │   ├── technical indicators
│   │   ├── labels
│   │   └── build_feature_table
│   ├── strategies
│   │   ├── Strategy
│   │   ├── MovingAverageCrossStrategy
│   │   └── MLSignalStrategy
│   ├── backtest
│   │   ├── BacktestEngine
│   │   ├── CommissionModel / SlippageModel
│   │   ├── metrics
│   │   ├── save_backtest_report / save_walk_forward_report
│   │   └── walk_forward（Prompt 17）
│   ├── models
│   │   ├── BasePredictiveModel
│   │   ├── LightGBMDirectionModel
│   │   └── time-series training helpers
│   ├── utils
│   │   └── device.py（GPU/CUDA 解析）
│   ├── risk（Prompt 18）
│   │   ├── RiskLimits / RiskDecision
│   │   ├── exposure（持仓 / 总敞口）
│   │   └── drawdown_guard
│   └── pipeline
│       └── run_quant_pipeline
│
├── Tool Layer
│   ├── BaseTool / ToolResult
│   ├── ToolRegistry
│   ├── DataSummaryTool
│   ├── BacktestTool
│   ├── TrainModelTool
│   ├── ReportTool
│   ├── RiskTool（risk_check）
│   ├── MLBacktestTool（ml_backtest）
│   └── PipelineTool（pipeline）
│
├── Agent Layer
│   ├── Message
│   ├── LLMClient / MockLLMClient
│   ├── BaseAgent
│   ├── ReportAgent
│   ├── SupervisorAgent
│   └── AgentEvent / ToolCallEvent / AgentFinishEvent
│
└── Memory Layer
    ├── ExperimentMemory（增强：搜索/排序/artifact）
    └── TradeMemory（JSONL 空壳）

└── RAG Layer（Prompt 20）
    ├── document_loader
    └── simple_retriever（关键词检索）
```

## 当前 CLI 入口

```text
download_data.py    数据下载（yfinance / Stooq）
merge_parquet.py    合并分年 parquet
build_features.py   特征构建
run_backtest.py     均线策略回测
train_model.py      模型训练（--device auto/cpu/gpu/cuda）
run_ml_backtest.py  ML 信号回测（Prompt 16）
run_walk_forward.py  Walk-forward 样本外（Prompt 17）
generate_report.py  报告读取/生成
run_agent.py        规则路由 Agent 工作流
run_pipeline.py     端到端 pipeline
```

## 当前已实现模块

### Quant Engine Layer

已实现：

- Parquet 数据读写
- YAML 存储目录管理
- OHLCV 数据校验
- `YFinanceFetcher`（接口；服务器 IP 易 Yahoo 限流）
- `StooqFetcher` + `STOOQ_API_KEY`（**服务器真实下载已验证**，EXP-20260601-004）
- 技术指标特征
- future return / direction label
- 按 symbol 分组的特征 pipeline
- Moving Average Cross 策略
- 下一根 bar 成交的轻量回测引擎
- 回测指标和报告保存
- LightGBM 模型封装 + Prompt 15 完整训练产物（**本地 68 passed**；服务器 CPU 训练 EXP-20260601-006）
- LightGBM GPU/CUDA 训练（Prompt 15b；服务器 EXP-20260602-004，见 M-010）
- MLSignalStrategy + ML 回测（Prompt 16；服务器 EXP-20260602-005）
- Walk-forward 样本外（Prompt 17；服务器 EXP-20260602-008，OOS sharpe 0.586）
- 基础风控层（Prompt 18）：RiskLimits、持仓限制裁剪/拒绝、回撤守卫
- 时间序列切分和 label 泄露防护
- 统一端到端 pipeline

### Tool Layer

已实现：

- `DataSummaryTool`
- `BacktestTool`
- `TrainModelTool`
- `ReportTool`
- `RiskTool`（`risk_check`）
- `MLBacktestTool`（`ml_backtest`，Prompt 19）
- `PipelineTool`（`pipeline`，Prompt 19）

工具返回摘要、指标和路径，不返回完整 DataFrame。

### Agent Layer

已实现：

- `Message`
- `MockLLMClient`
- `BaseAgent`
- `ReportAgent`
- `SupervisorAgent`
- Agent 事件类型

当前 SupervisorAgent 使用规则路由，支持 7 类任务（含 ml_backtest / risk_check / pipeline），不调用真实 LLM。

### Memory Layer

已实现：

- `ExperimentMemory`：add / list / latest / **get / search_by_name / sort_by_metric / find_best**
- `TradeMemory`：JSONL append-only 空壳（Prompt 20）
- JSON 记录实验元数据、指标、参数和产物路径

### RAG Layer（Prompt 20）

已实现：

- `Document` + `document_loader`（md/txt/json）
- `SimpleRetriever` 关键词检索（无向量库、无 LLM）

## 后续计划

### 第一～二阶段 ✅

- [x] 服务器 Python 3.11 环境部署
- [x] 全量 pytest 验证（**98 passed** 含 Prompt 20，2026-06-01）
- [x] Stooq 真实数据下载（6033 rows，AAPL/MSFT/SPY 2018–2025）
- [x] 服务器真实 pipeline（`server_ma_cross_real_001`）
- [x] Prompt 15–17：ML 训练、ML 回测、walk-forward OOS

### 第二阶段扩展 ✅

- [x] Prompt 18：基础风控层（RiskLimits / RiskTool，EXP-20260601-009）

### 第三阶段 ✅

- [x] Prompt 19：Supervisor 7 类路由 + MLBacktestTool + PipelineTool

### 第四阶段 ✅

- [x] Prompt 20：Memory + RAG（ExperimentMemory 增强、TradeMemory、SimpleRetriever）

### 第五～六阶段 ⏸

- **第五阶段**：LangGraph 编排（暂缓）
- **第六阶段**：Paper Trading（暂缓）

