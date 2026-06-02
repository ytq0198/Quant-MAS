# Quant MAS 实验记录

更新时间：2026-06-01

本文件用于记录真实实验和重要验证。不要记录未经实际运行的数据结果；尚未真实运行的项目标记为“待验证”。

## 实验记录模板

```markdown
## 实验编号：EXP-YYYYMMDD-001

- 日期：
- 阶段：
- 数据：
- 策略 / 模型：
- 参数：
- 指标：
  - total_return：
  - sharpe：
  - max_drawdown：
  - final_equity：
  - 其他：
- 产物路径：
  - metrics：
  - equity_curve：
  - trades：
  - summary：
  - model：
- 问题：
- 下一步：
```

## 当前验证记录

### EXP-20260601-009：Prompt 18 基础风控层本地验证 ✅

- 日期：2026-06-01
- 阶段：第二阶段扩展（Prompt 18）
- 数据：synthetic `target_weight` parquet（pytest `tmp_path`）
- 模块：`RiskLimits`、`RiskDecision`、`check_position_limits`、`check_drawdown`、`RiskTool`
- 配置：`configs/risk.yaml`（`max_position_weight`、`max_total_exposure`、`allow_short`）
- 指标：
  - `tests/test_risk.py`：**5 passed**
  - 全量 `python -m pytest -v`：**76 passed**
- 验收：
  - 超限时 `clip=True` → status=`clipped`，`adjusted_targets` 可审计
  - `clip=False` → status=`rejected`
  - 回撤超限 → `max_drawdown_exceeded`
  - `RiskTool` 可注册 `ToolRegistry`，返回 metadata 含 `decisions` / `violations`
- 产物路径：代码 `src/quant_mas/risk/`、`src/quant_mas/tools/quant/risk_tool.py`
- 问题：无（兼容保留原 `tools/quant.py` 导出）
- 下一步：Prompt 19 Supervisor 接入 `risk_check` 路由

### EXP-20260601-010：服务器 Prompt 18 pull 后全量 pytest ✅

- 日期：2026-06-01
- 阶段：第二阶段扩展（Prompt 18 服务器验证）
- 环境：a6000-9961，`git` @ `60c2ee7`，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令：`git pull origin main` → `python -m pip install -e .` → `python -m pytest -v`
- 指标：
  - 全量：**76 passed** in **1.76s**
  - 含 `tests/test_risk.py` 5 项全部通过
- 问题：无
- 下一步：Codex Prompt 19（Supervisor 路由增强）

### EXP-20260602-001：最小端到端 synthetic pipeline 测试

- 日期：2026-06-02
- 阶段：Phase 1 工程验证
- 数据：pytest 中生成的 synthetic OHLCV 数据
- 策略 / 模型：MovingAverageCrossStrategy
- 参数：测试内固定小窗口参数
- 指标：测试仅验证指标字段存在，不记录具体收益数值
- 产物路径：pytest `tmp_path` 临时目录
- 问题：无
- 下一步：使用 sample parquet 或真实小规模数据验证 `scripts/run_pipeline.py`

### EXP-20260602-002：本地 synthetic CLI pipeline smoke test

- 日期：2026-06-02
- 阶段：Phase 1 CLI 验证
- 数据：本地 synthetic OHLCV parquet
- 策略 / 模型：MovingAverageCrossStrategy
- 参数：`--skip-download --strategy ma_cross --experiment-name synthetic_pipeline_cli`
- 指标：已由脚本输出，但该记录不作为真实研究实验结果
- 产物路径：`outputs/reports/synthetic_pipeline_cli/`
- 问题：仅为 smoke test，不代表真实市场表现
- 下一步：用 sample parquet 或真实小规模数据验证

### EXP-20260602-008：服务器 Walk-forward 真实实验 ✅（Prompt 17）

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.4（Prompt 17 服务器验证）
- 环境：a6000-9961，CUDA LightGBM，`git` @ `1f4df61`
- 数据：`/mnt/localDisk3/weizian/datasets/features/features.parquet`（6033 rows，865K）
- 配置：`walk_forward.yaml` — train 504 / val 126 / test 126 / oos 63 / step 63
- 参数：`--experiment-name server_walk_forward_001`；`device_requested=auto`，`device_resolved=cuda`，`device_fallback=false`
- 运行：约 **17s**，**19 个窗口**
- OOS 汇总（`metrics.json` → `oos` 块，**主记录指标**）：
  - sharpe：**0.586**
  - total_return：**0.443**（≈ +44%）
  - annualized_return：**0.080**
  - max_drawdown：**-0.255**
  - final_equity：**144,261**
  - bars：**1197**
  - auc_mean：**0.472**；accuracy_mean：**0.479**
  - window_count：**19**
- 与单段 ML 回测对比（EXP-20260602-005，**非 OOS，勿混用**）：

  | 指标 | Walk-forward OOS | server_ml_backtest_001 |
  |------|------------------|------------------------|
  | sharpe | **0.586** | 2.78 |
  | total_return | 0.443 | 68.27 |
  | annualized_return | 0.080 | 0.701 |
  | max_drawdown | -0.255 | -0.246 |
  | bars | 1197 | 2011 |

- 解读：单段 sharpe 2.78 **不能代表样本外**；OOS sharpe ≈ 0.59、收益 ≈ +44% 与 val/test AUC ≈ 0.47–0.49 一致，更接近真实泛化。各窗 `oos_sharpe` 有盈有亏（如 window 5/7 为负）属滚动 OOS 正常；`backtest_sharpe_mean` ≈ 0.86 为分窗均值，**报告以拼接 OOS `oos.sharpe` 为准**。
- 产物路径：
  - 报告：`/mnt/localDisk3/weizian/Quant-MAS/outputs/reports/walk_forward_latest/`
  - metrics / windows / oos_equity / oos_trades / summary
  - 日志：`/mnt/localDisk3/weizian/logs/walk_forward_server_001.log`
- 前置：`python -m pytest -v` → **71 passed**（1.65s）
- 问题：无
- 下一步：**Prompt 18** 风控层；可选 CPU 对照（EXP-TODO-006）

### EXP-20260602-007：Prompt 17 Walk-forward 本地验证 ✅

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.4（Prompt 17）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic features + mock model（测试不依赖真实金融数据）
- 模块：`walk_forward.py`、`save_walk_forward_report()`、`run_walk_forward.py`
- 参数：
  - `python -m pytest tests/test_walk_forward.py -v` → **3 passed**
  - `python -m pytest -v` → **71 passed**
  - `python scripts/run_walk_forward.py --help` → 正常
- 验证点：按时间推进 train/val/test/oos 窗口；模型仅 train 拟合；OOS 接入 MLSignalStrategy + BacktestEngine；metrics 区分 train/val/test/oos
- 产物（测试 tmp_path）：metrics.json、windows.csv、oos_equity_curve.csv、oos_trades.csv、summary.md
- 问题：无
- 下一步：服务器真实 walk-forward（EXP-TODO-007）

### EXP-20260602-005：服务器 ML 信号回测 ✅（Prompt 16）

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.3（Prompt 16 服务器验证）
- 环境：a6000-9961，CUDA LightGBM 4.6.0
- 数据：真实 features + GPU 训练模型（`server_lgbm_gpu_001`）
- 策略 / 模型：`MLSignalStrategy` + `LightGBMDirectionModel` pred_proba
- 参数：`run_ml_backtest.py --experiment-name server_ml_backtest_001`
- 指标（2011 bars）：
  - total_return：**68.27**（脚本输出比例，非百分号）
  - annualized_return：**0.701**
  - sharpe：**2.78**
  - max_drawdown：**-0.246**
  - final_equity：**6,927,128.57**
- 产物路径：
  - 报告：`outputs/reports/ml_backtest_latest/summary.md`
  - 日志：`/mnt/localDisk3/weizian/logs/ml_backtest_server_001.log`
- 问题：无（链路验证通过；收益数值需后续 walk-forward 样本外复核）
- 下一步：walk-forward 服务器 ✅ → 见 EXP-20260602-008

### EXP-20260602-004：服务器 GPU LightGBM 训练 ✅（Prompt 15b）

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.2b（Prompt 15b 服务器验证）
- 环境：a6000-9961，4× RTX A6000，驱动 580，CUDA 13.0
- 数据：真实 features（6033 rows，与 EXP-20260601-006 相同）
- 策略 / 模型：`LightGBMDirectionModel`，`--device cuda`，`future_direction_5`
- 参数：`configs/train.gpu.yaml`，`--experiment-name server_lgbm_gpu_001`
- device（metadata / metrics）：
  - `device_requested`: cuda
  - `device_resolved`: cuda
  - `device_fallback`: false
  - `device_reason`: null
- 指标：
  - train：accuracy **0.869**，AUC **0.961**，4170 samples
  - val：accuracy **0.445**，AUC **0.457**，894 samples
  - test：accuracy **0.456**，AUC **0.479**，894 samples
  - feature_count：15
- 产物路径：`/mnt/localDisk3/weizian/models/lightgbm_direction_latest/`
- 问题：首次训练失败 — PyPI CPU-only LightGBM（见 M-010）；源码编译 CUDA 版后成功
- 与 CPU 基线（EXP-20260601-006）：val/test AUC 仍 ~0.46–0.48，属模型过拟合问题，非 GPU 链路问题
- 下一步：可选 `server_lgbm_cpu_001` 对照；Prompt 17

### EXP-20260602-003：服务器全量 pytest 验证

- 日期：2026-06-02
- 阶段：Phase 1 服务器部署验证
- 环境：
  - 主机：a6000-9961
  - 路径：`/mnt/localDisk3/weizian/Quant-MAS`
  - Conda：`/mnt/localDisk3/weizian/conda_envs/quant-mas`
  - Python：3.11.15
- 数据：synthetic（pytest 内置，不联网）
- 策略 / 模型：全模块单元 / 集成测试
- 参数：`python -m pytest -v`
- 指标：**44 passed in 1.19s**（2026-06-02 初验；同日后 pull GPU 代码并重装 CUDA LightGBM 后为 **68 passed**）
- 产物路径：无（测试不产生持久产物）
- 问题：无
- 下一步：真实数据下载与 pipeline

### EXP-20260601-008：Prompt 15b LightGBM GPU/CUDA 本地验证 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.2b（GPU 训练支持）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic / mock（无真实 GPU）
- 模型：`LightGBMDirectionModel` + `resolve_training_device`
- 参数：
  - `python -m pytest tests/test_device.py -v` → **10 passed**
  - `python -m pytest tests/test_train_model.py -v` → **5 passed**
  - `python -m pytest -v` → **68 passed**
  - `python scripts/train_model.py --help` → 含 `--device {auto,cpu,gpu,cuda}`
- 验证点：auto/cuda/gpu/cpu 解析；无 GPU 安全 fallback；metrics/metadata 含 device 字段
- 问题：无
- 下一步：服务器验证完成 → 见 EXP-20260602-004

### EXP-20260601-007：Prompt 16 MLSignalStrategy 本地验证 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.3（Prompt 16）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic features + mock model
- 策略 / 模型：`MLSignalStrategy`（buy/sell threshold → target_weight）
- 参数：`python -m pytest tests/test_ml_signal_strategy.py -v`；`python -m pytest -v`
- 指标：**4 passed**（ML 专项）；**57 passed**（全量）
- 验证点：pred_proba → signal；下一根 bar 成交；报告产物；禁止 future label 进特征
- 问题：无
- 下一步：服务器验证完成 → 见 EXP-20260602-005

### EXP-20260601-006：服务器真实 LightGBM 训练 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.2（Prompt 15 服务器验证）
- 环境：a6000-9961，`/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 数据：真实 features（6033 rows，AAPL/MSFT/SPY，来自 Step 2.1 pipeline）
- 策略 / 模型：`LightGBMDirectionModel`，label `future_direction_5`，15 features
- 参数：
  - `configs/train.yaml`（n_estimators=100，70/15/15 时间切分）
  - `--experiment-name server_lgbm_001`
- 指标：
  - train：accuracy **0.876**，AUC **0.965**，4170 samples（2018-01-31 — 2023-08-09）
  - val：accuracy **0.445**，AUC **0.458**，894 samples（2023-08-10 — 2024-10-15）
  - test：accuracy **0.455**，AUC **0.466**，894 samples（2024-10-16 — 2025-12-23）
  - train_positive_rate：0.695 / val：0.403 / test：0.311
- 产物路径：
  - 模型目录：`/mnt/localDisk3/weizian/models/lightgbm_direction_latest/`
  - metrics：`.../metrics.json`
  - feature_importance：`.../feature_importance.csv`
  - model：`.../model.pkl`
  - feature_columns / metadata：同目录
  - ExperimentMemory：`/mnt/localDisk3/weizian/reports/experiments.json`（`server_lgbm_001`）
- 问题：**明显过拟合** — 训练集 AUC 高、val/test AUC 接近随机（~0.46）；标签正负比例随时间漂移。属 MVP 基线结果，非脚本故障。
- 下一步：**Prompt 16** — MLSignalStrategy + 样本外 ML 回测；后续可调参 / 特征 / 类别权重

### EXP-20260601-005：Prompt 15 ML 训练模块本地验证 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.2（Prompt 15）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic features（mock 模型，不依赖真实 LightGBM）
- 策略 / 模型：`train_direction_model()` + mock direction model
- 参数：`python -m pytest -v`
- 指标：**53 passed**
- 验证产物（测试 `tmp_path`）：
  - `metrics.json`（train/val/test accuracy、auc、时间范围、样本数）
  - `feature_importance.csv`
  - `model.pkl`
  - `feature_columns.json`、`metadata.json`
  - ExperimentMemory 记录
- 问题：无
- 下一步：git push → 服务器 `requirements-ml.txt` + 真实 `train_model.py`

### EXP-20260601-004：服务器真实数据 Stooq 下载 + ma_cross pipeline ✅

- 日期：2026-06-01
- 阶段：Phase 1 Step 1.5 / Phase 2 Step 2.1
- 环境：
  - 主机：a6000-9961
  - 路径：`/mnt/localDisk3/weizian/Quant-MAS`
  - Conda：`/mnt/localDisk3/weizian/conda_envs/quant-mas`
  - 数据源：**Stooq**（`STOOQ_API_KEY` in `.env`）
- 数据：
  - 标的：AAPL、MSFT、SPY
  - 区间：2018-01-01 — 2025-12-31（按年 parquet，合并）
  - 原始行数：**6033 rows** → `/mnt/localDisk3/weizian/datasets/raw/market_data.parquet`
- 策略 / 模型：MovingAverageCrossStrategy（`ma_cross`）
- 参数：
  - `SOURCE=stooq bash server/download_data_resilient.sh`
  - `run_pipeline.py --skip-download --experiment-name server_ma_cross_real_001`
- 指标（回测约 2011 bars）：
  - total_return：≈ 2.02
  - annualized_return：≈ 0.149
  - sharpe：≈ 1.00
  - max_drawdown：≈ -0.21
  - final_equity：≈ 302,453
- 产物路径：
  - raw：`/mnt/localDisk3/weizian/datasets/raw/market_data.parquet`
  - reports：`/mnt/localDisk3/weizian/reports/server_ma_cross_real_001/`
  - metrics：`.../metrics.json`
  - equity_curve：`.../equity_curve.csv`
  - trades：`.../trades.csv`
  - summary：`.../summary.md`
  - 日志（MSFT+SPY 下载）：`/mnt/localDisk3/weizian/logs/resilient_msft_spy.log`
- 问题：Yahoo yfinance 限流；Stooq 需 API Key（见 `mistakes.md` M-009）
- 下一步：Prompt 15 / 16 已完成

## 待验证实验

### EXP-TODO-006：CPU 对照训练（可选）

- 目的：与 EXP-20260601-006 / EXP-20260602-004 在同一 features 上对比 CPU vs GPU metrics
- 命令：`train_model.py --device cpu --experiment-name server_lgbm_cpu_001`
- 状态：可选，未跑

## 实验里程碑速查

| 编号 | 日期 | 内容 | 关键结果 |
|------|------|------|----------|
| EXP-20260601-004 | 2026-06-01 | Stooq 真实数据 + ma_cross | 6033 rows，sharpe ≈ 1.00 |
| EXP-20260601-006 | 2026-06-01 | CPU LightGBM 训练 | test AUC 0.466 |
| EXP-20260602-004 | 2026-06-02 | GPU LightGBM 训练 | device=cuda，test AUC 0.479 |
| EXP-20260602-005 | 2026-06-02 | ML 信号回测（单段） | sharpe 2.78（in-sample 风格） |
| EXP-20260602-007 | 2026-06-02 | Walk-forward 本地 | 71 passed |
| EXP-20260602-008 | 2026-06-02 | Walk-forward 服务器 | **OOS sharpe 0.586**，+44%，19 窗 |
