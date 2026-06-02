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
download_data.py    数据下载接口
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
- yfinance fetcher 接口，真实联网下载待验证
- 技术指标特征
- future return / direction label
- 按 symbol 分组的特征 pipeline
- Moving Average Cross 策略
- 下一根 bar 成交的轻量回测引擎
- 回测指标和报告保存
- LightGBM 模型封装，真实训练待验证
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

### Phase 1 收口

- [x] 服务器 Python 3.11 环境部署
- [x] 全量 pytest 验证（44 passed，2026-06-02）
- [ ] 安装 data/ml 可选依赖
- [ ] 用真实或 sample parquet 验证完整 pipeline
- [ ] 增加风险检查模块
- [ ] 完善报告格式

### Phase 2 机器学习实验

- 真实安装和验证 LightGBM
- 样本外训练与评估
- 特征重要性
- ML signal 回测

### Phase 3 Agent 增强

- 增强任务解析
- 增强报告 Agent
- 增加实验审计事件
- 后续评估 RAG / Memory / LangGraph

