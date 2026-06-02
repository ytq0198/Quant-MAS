# Quant MAS 实验记录

更新时间：2026-06-02

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

## 待验证实验

### EXP-TODO-001：真实数据下载验证

- 日期：待定
- 数据：AAPL / MSFT / SPY 等真实行情
- 策略 / 模型：MovingAverageCrossStrategy
- 状态：待验证
- 说明：需要网络和真实数据源可用。

### EXP-TODO-002：LightGBM 真实训练实验

- 日期：待定
- 数据：真实或 sample feature parquet
- 策略 / 模型：LightGBMDirectionModel
- 状态：待验证
- 说明：需要服务器或本地环境安装 LightGBM。

