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
- 下一步：**Codex Prompt 15** — 真实 LightGBM 训练（`requirements-ml.txt`）

## 待验证实验

### EXP-TODO-002：LightGBM 真实训练实验

- 日期：待定
- 数据：真实 feature parquet（Step 2.1 已具备 raw + pipeline 特征链）
- 策略 / 模型：LightGBMDirectionModel
- 状态：待验证
- 说明：服务器安装 `requirements-ml.txt` 后执行 Prompt 15
