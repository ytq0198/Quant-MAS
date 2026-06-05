# Quant MAS Metric Family Policy / 指标分层策略

The project separates metric families so that research evidence is not overstated.

本项目将不同指标族分开，避免夸大研究证据。

## Families / 指标族

| Family | Use | 中文 |
|---|---|---|
| `oos.*` | Audited walk-forward out-of-sample evaluation. This is the only family suitable for paper-grade baseline comparison. | 经审计的 Walk-forward 样本外评估。只有这一类适合论文级基线对比。 |
| `backtest.*` | In-sample or workflow-oriented backtest summaries. Useful for debugging and understanding strategy behavior. | 样本内或流程理解用回测摘要。适合调试和理解策略行为。 |
| `simulation.*` | Simulated environment signals that do not represent audited OOS evidence. | 仿真环境信号，不代表经审计 OOS 证据。 |
| `training.*` | Model training loss, validation, or RL training metrics. | 模型训练损失、验证指标或 RL 训练指标。 |
| `population.*` | Candidate population or self-play metrics. | 候选种群或自博弈指标。 |
| `audit.*` | Workflow, safety, human review, and reproducibility records. | 工作流、安全、人工审核和可复现记录。 |

## Rules / 规则

- Do not mix `oos.*` with `backtest.*`, `simulation.*`, `training.*`, `population.*`, or `audit.*`.
- 不要将 `oos.*` 与 `backtest.*`、`simulation.*`、`training.*`、`population.*` 或 `audit.*` 混用。
- UI labels must clearly mark non-OOS backtest summaries.
- UI 标签必须清楚标注非 OOS 回测摘要。
- Reports must state the source and family of every metric.
- 报告必须说明每个指标的来源和指标族。
- No metric should be written as a real-world execution promise.
- 任何指标都不应被表述为现实执行承诺。

## Current Audited Baseline / 当前经审计基线

The current documented OOS baseline is `EXP-20260602-008`, Sharpe `0.586`, with 19 walk-forward windows. This is a recorded research baseline, not a future-result claim.

当前文档记录的 OOS 基线是 `EXP-20260602-008`，Sharpe `0.586`，包含 19 个 Walk-forward 窗口。这是已记录的研究基线，不是未来结果声明。
