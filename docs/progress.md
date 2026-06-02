# Quant MAS 开发进度

更新时间：2026-06-01

## 当前所处阶段

**第三阶段** ✅ 已完成（Prompt 19，EXP-20260601-011）。

**当前：第四阶段 Prompt 20**（Memory + RAG）。

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
- [x] **Prompt 17**：Walk-forward 样本外
- [x] **Prompt 18**：基础风控层
- [x] **Prompt 19**：Supervisor 路由（MLBacktestTool / PipelineTool / RiskTool）

## 当前 pytest 状态

| 环境 | Python | 结果 | 日期 |
|------|--------|------|------|
| 本地 Windows | 3.11+ | **87 passed** | 2026-06-01 |
| 服务器 Linux | 3.11.15 | **87 passed** | 2026-06-01 |

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
- 服务器上必须使用 `python -m pytest`，不能裸敲 `pytest`。
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
python scripts/run_walk_forward.py --help
```

## 当前已实现能力

- [x] Parquet 数据存储
- [x] YAML 路径配置和目录管理
- [x] OHLCV 数据校验
- [x] Stooq 下载接口（服务器真实下载已验证）
- [x] yfinance 下载接口（备用）
- [x] 技术指标特征 / future label / 按 symbol 分组特征
- [x] Moving Average Cross 策略 + 轻量回测引擎
- [x] 回测报告 + ExperimentMemory
- [x] LightGBM 训练（CPU + GPU/CUDA）
- [x] MLSignalStrategy + ML 回测 + walk-forward OOS
- [x] RiskLimits / RiskTool 基础风控
- [x] Agent Core + 7 个 Quant Tools + Supervisor 7 类路由

## 分阶段目标

### 第零～第二阶段 ✅

- [x] 量化核心 MVP + ML 实验链路（Prompt 1–17、15b）
- [x] 服务器 walk-forward OOS sharpe 0.586（EXP-20260602-008）

### 第二阶段扩展 ✅

- [x] Prompt 18 风控（76 passed，EXP-20260601-009/010）

### 第三阶段 ✅

- [x] Prompt 19：MLBacktestTool、PipelineTool、Supervisor 扩展（87 passed，EXP-20260601-011）

### 第四阶段 🔄 当前

- [ ] Prompt 20：Memory + RAG 雏形

### 第五～六阶段

- [ ] LangGraph 编排（暂缓）
- [ ] Paper Trading（暂缓）

## 研究解读（2026-06-02）

- **第二阶段 ML 链路已全部跑通**；报告以 walk-forward OOS 为准（sharpe 0.586）。
- **Agent 层** 现已可路由 ML 回测、风控、pipeline；下一步 **Prompt 20** Memory/RAG。
