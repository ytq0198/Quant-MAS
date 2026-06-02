# Quant MAS 架构

更新时间：2026-06-02

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
│   │   └── MovingAverageCrossStrategy
│   ├── backtest
│   │   ├── BacktestEngine
│   │   ├── CommissionModel / SlippageModel
│   │   ├── metrics
│   │   └── save_backtest_report
│   ├── models
│   │   ├── BasePredictiveModel
│   │   ├── LightGBMDirectionModel
│   │   └── time-series training helpers
│   └── pipeline
│       └── run_quant_pipeline
│
├── Tool Layer
│   ├── BaseTool / ToolResult
│   ├── ToolRegistry
│   ├── DataSummaryTool
│   ├── BacktestTool
│   ├── TrainModelTool
│   └── ReportTool
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
    └── ExperimentMemory
```

## 当前 CLI 入口

```text
download_data.py    数据下载（yfinance / Stooq）
merge_parquet.py    合并分年 parquet
build_features.py   特征构建
run_backtest.py     均线策略回测
train_model.py      模型训练
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
- LightGBM GPU/CUDA 训练（Prompt 15b：`device.py`、`--device`、auto fallback）
- MLSignalStrategy + ML 回测脚本（Prompt 16；服务器真实回测待验证）
- 时间序列切分和 label 泄露防护
- 统一端到端 pipeline

### Tool Layer

已实现：

- `DataSummaryTool`
- `BacktestTool`
- `TrainModelTool`
- `ReportTool`

工具返回摘要、指标和路径，不返回完整 DataFrame。

### Agent Layer

已实现：

- `Message`
- `MockLLMClient`
- `BaseAgent`
- `ReportAgent`
- `SupervisorAgent`
- Agent 事件类型

当前 SupervisorAgent 使用规则路由，不调用真实 LLM。

### Memory Layer

已实现：

- `ExperimentMemory`
- JSON 记录实验元数据、指标、参数和产物路径

## 后续计划

### Phase 1 收口 ✅

- [x] 服务器 Python 3.11 环境部署
- [x] 全量 pytest 验证（44 passed，2026-06-02）
- [x] Stooq 真实数据下载（6033 rows，AAPL/MSFT/SPY 2018–2025）
- [x] 服务器真实 pipeline（`server_ma_cross_real_001`）
- [ ] 增加风险检查模块
- [ ] 完善报告格式

### Phase 2 机器学习实验 🔄 当前

- [x] Step 2.1 真实数据 + ma_cross pipeline
- [x] Prompt 15：训练 artifacts + ExperimentMemory（本地 53 passed）
- [x] 服务器真实 LightGBM 训练（EXP-20260601-006）
- [x] Prompt 16：MLSignalStrategy + `run_ml_backtest.py`（本地 68 passed）
- [x] Prompt 15b：GPU/CUDA 训练支持（`tests/test_device.py` 10 passed）
- [ ] 服务器 GPU 训练（EXP-TODO-005）
- [ ] Walk-forward（Prompt 17）

### Phase 3 Agent 增强

- 增强任务解析
- 增强报告 Agent
- 增加实验审计事件
- 后续评估 RAG / Memory / LangGraph

