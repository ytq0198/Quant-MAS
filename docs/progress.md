# Quant MAS 开发进度

更新时间：2026-06-02

## 当前阶段

Phase 1 收口中：当前已经完成最小量化闭环的主要工程模块，并新增端到端 pipeline 与端到端测试。

## Prompt 任务状态

- [x] Prompt 1：项目骨架
- [x] Prompt 2：数据存储与目录管理
- [x] Prompt 3：数据下载接口与 OHLCV 校验
- [x] Prompt 4：特征工程
- [x] Prompt 5：均线策略与回测
- [x] Prompt 6：实验记忆和报告
- [x] Prompt 7：模型训练框架
- [x] Prompt 8：轻量 Agent Core
- [x] Prompt 9：量化 Tools
- [x] Prompt 10：SupervisorAgent 和内部任务流
- [x] 统一端到端 pipeline：`scripts/run_pipeline.py`
- [x] 最小端到端测试：`tests/test_end_to_end_pipeline.py`

## 当前 pytest 状态

最近一次本地验证：

```text
pytest
44 passed
```

说明：

- 测试使用 synthetic data。
- 测试不访问真实网络。
- 测试不调用真实 LLM API。
- 测试不要求真实 LightGBM。

## 当前可用 CLI

```powershell
python scripts/download_data.py --help
python scripts/build_features.py --help
python scripts/run_backtest.py --help
python scripts/train_model.py --help
python scripts/generate_report.py --help
python scripts/run_agent.py --help
python scripts/run_pipeline.py --help
```

## 当前已实现能力

- [x] Parquet 数据存储
- [x] YAML 路径配置和目录管理
- [x] OHLCV 数据校验
- [x] yfinance 下载接口，真实下载待验证
- [x] 技术指标特征
- [x] future return / direction label
- [x] 按 symbol 分组构建特征，避免多标的污染
- [x] Moving Average Cross 策略
- [x] 下一根 bar 成交的轻量回测引擎
- [x] 交易成本模型：commission / slippage
- [x] 回测指标：total_return、sharpe、max_drawdown、final_equity 等
- [x] 回测报告保存：metrics、equity curve、trades、summary
- [x] ExperimentMemory JSON 记录
- [x] LightGBM 模型封装，真实训练待验证
- [x] 时间序列切分 70/15/15
- [x] label 泄露防护
- [x] Message / LLMClient / MockLLMClient / BaseAgent
- [x] BaseTool / ToolRegistry / ToolResult
- [x] DataSummaryTool / BacktestTool / TrainModelTool / ReportTool
- [x] SupervisorAgent 规则路由
- [x] AgentEvent / ToolCallEvent / AgentFinishEvent
- [x] 端到端 pipeline

## 下一阶段目标

### Phase 1：最小量化闭环收口

- [ ] 在服务器或稳定 Python 3.11 环境中完整安装依赖
- [ ] 用小规模真实或 sample 数据验证 `run_pipeline.py`
- [ ] 整理一份真实 pipeline 运行报告
- [ ] 增加基础风险检查模块
- [ ] 完善 README 的运行示例

### Phase 2：机器学习真实实验

- [ ] 安装并验证 LightGBM
- [ ] 使用真实特征数据训练方向模型
- [ ] 输出样本外指标
- [ ] 输出特征重要性
- [ ] 将模型训练结果写入 ExperimentMemory
- [ ] 对 ML 信号做样本外回测

### Phase 3：Agent 增强

- [ ] 增强 SupervisorAgent 的任务解析能力
- [ ] 增加 Agent 事件审计报告
- [ ] 将 ReportAgent 与真实报告产物对接
- [ ] 在不直接交易的前提下扩展研究和解释能力
- [ ] 后续再评估是否引入 LangGraph / RAG / Memory 扩展

