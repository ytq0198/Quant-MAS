# Quant MAS 开发进度

更新时间：2026-06-01

## 当前阶段

**Phase 2**：Prompt 16 + GPU 训练支持 ✅（本地 **68 passed**）。**当前：服务器 GPU 训练 / ML 回测 + Prompt 17**。

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
- [x] **Prompt 15**：ML 训练完整产物
- [x] **Prompt 16**：MLSignalStrategy + `run_ml_backtest.py`
- [x] **Prompt 15b**：LightGBM GPU/CUDA 训练（`device.py`、`--device`）

## 当前 pytest 状态

| 环境 | Python | 结果 | 日期 |
|------|--------|------|------|
| 本地 Windows | 3.11+ | **68 passed** | 2026-06-01 |
| 服务器 Linux | 3.11.15 | 待 pull 后复测 | 2026-06-02 |

服务器验证环境：

```text
主机：a6000-9961
项目路径：/mnt/localDisk3/weizian/Quant-MAS
Conda 环境：/mnt/localDisk3/weizian/conda_envs/quant-mas
命令：python -m pytest -v
```

说明：

- 测试使用 synthetic data。
- 测试不访问真实网络。
- 测试不调用真实 LLM API。
- 测试不要求真实 LightGBM。
- 服务器上必须使用 `python -m pytest`，不能裸敲 `pytest`（否则会误用 Python 3.9）。
- 服务器上必须使用 `python -m pip`，不能裸敲 `pip`。

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
```

## 当前已实现能力

- [x] Parquet 数据存储
- [x] YAML 路径配置和目录管理
- [x] OHLCV 数据校验
- [x] Stooq 下载接口（`StooqFetcher` + `STOOQ_API_KEY`），服务器真实下载已验证
- [x] yfinance 下载接口（服务器 IP 易限流，备用）
- [x] 技术指标特征
- [x] future return / direction label
- [x] 按 symbol 分组构建特征，避免多标的污染
- [x] Moving Average Cross 策略
- [x] 下一根 bar 成交的轻量回测引擎
- [x] 交易成本模型：commission / slippage
- [x] 回测指标：total_return、sharpe、max_drawdown、final_equity 等
- [x] 回测报告保存：metrics、equity curve、trades、summary
- [x] ExperimentMemory JSON 记录
- [x] LightGBM 真实训练（服务器 `server_lgbm_001`，EXP-20260601-006）
- [x] 时间序列切分 70/15/15
- [x] label 泄露防护
- [x] Message / LLMClient / MockLLMClient / BaseAgent
- [x] BaseTool / ToolRegistry / ToolResult
- [x] DataSummaryTool / BacktestTool / TrainModelTool / ReportTool
- [x] SupervisorAgent 规则路由
- [x] AgentEvent / ToolCallEvent / AgentFinishEvent
- [x] LightGBM GPU/CUDA 训练支持（`resolve_training_device`，auto fallback CPU）
- [x] MLSignalStrategy + ML 信号回测（Prompt 16，mock 测试通过）

## 下一阶段目标

### Phase 1：最小量化闭环收口 ✅

- [x] 在服务器 Python 3.11 环境中完整安装核心依赖
- [x] 服务器全量 pytest 验证（44 passed）
- [x] Stooq 真实数据下载（AAPL / MSFT / SPY，2018–2025，6033 rows）
- [x] 服务器真实 `run_pipeline.py`（`server_ma_cross_real_001`）
- [x] 在服务器验证真实 LightGBM 训练与 artifacts
- [ ] 增加基础风险检查模块

### Phase 2：机器学习真实实验 🔄 当前

- [x] Step 2.1 真实数据 pipeline（服务器 Stooq + ma_cross 回测）
- [x] Step 2.3 Prompt 16：MLSignalStrategy + ML 回测（本地 57 passed）
- [x] Step 2.2b Prompt 15b：GPU/CUDA 训练支持（本地 68 passed）
- [ ] Step 2.3 服务器真实 ML 回测（EXP-TODO-003）
- [ ] Step 2.2b 服务器 GPU 训练（EXP-TODO-005，`server_lgbm_gpu_001`）
- [ ] Step 2.4 Prompt 17：Walk-forward 样本外（**当前**）

### Phase 3：Agent 增强

- [ ] 增强 SupervisorAgent 的任务解析能力
- [ ] 增加 Agent 事件审计报告
- [ ] 将 ReportAgent 与真实报告产物对接
- [ ] 在不直接交易的前提下扩展研究和解释能力
- [ ] 后续再评估是否引入 LangGraph / RAG / Memory 扩展

