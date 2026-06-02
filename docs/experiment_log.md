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
- 指标：**44 passed in 1.19s**
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
- 下一步：服务器 `nvidia-smi` + `--device cuda` 真实训练（EXP-TODO-005）

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
- 下一步：git push → 服务器 `run_ml_backtest.py` 真实模型回测

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
- 下一步：**Codex Prompt 16** — ML 信号策略 + 回测

## 待验证实验

### EXP-TODO-003：ML 信号真实回测（Prompt 16 服务器）

- 日期：待定
- 数据：真实 features + `server_lgbm_001` 模型
- 命令：
  ```bash
  python scripts/run_ml_backtest.py \
    --config configs/backtest_ml.yaml \
    --storage-config configs/storage.server.yaml \
    --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
    --model-path /mnt/localDisk3/weizian/models/lightgbm_direction_latest/model.pkl \
    --experiment-name server_ml_backtest_001
  ```
- 状态：待验证

### EXP-TODO-005：服务器 GPU LightGBM 训练（Prompt 15b）

- 日期：待定
- 数据：真实 features（6033 rows）
- 命令：
  ```bash
  nvidia-smi
  python scripts/train_model.py \
    --config configs/train.gpu.yaml \
    --storage-config configs/storage.server.yaml \
    --device cuda \
    --experiment-name server_lgbm_gpu_001
  cat /mnt/localDisk3/weizian/models/lightgbm_direction_latest/metadata.json | grep device
  ```
- 验收：`device_resolved` 为 `cuda`（非 fallback）；对比 EXP-20260601-006 CPU 指标
- 状态：待验证

### EXP-TODO-004：Walk-forward 样本外（Prompt 17）
