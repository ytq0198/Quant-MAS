# PPT 实验数据清单（服务器导出）

> 来源：a6000-9961 `/mnt/localDisk3/weizian/`  
> 导出时间：2026-06-04  
> **不含**：`.env`、API Key、`.parquet` 原始行情、模型权重 `.pkl`  
> **论文主指标**：仅使用 `oos.sharpe` / `oos.total_return`（walk-forward）；勿将 ML 单段 sharpe 2.78 与 OOS 混比

## 一、PPT 优先引用（核心表）

| 文件 | 用途 | 关键数字 |
|------|------|----------|
| `paper/paper_main_results.csv` | **主结果表**（OOS only） | baseline **0.586** sharpe |
| `paper/paper_text_ablation.csv` | 文本特征 ablation | WF-001/002/003 |
| `paper/paper_population_ablation.csv` | 策略种群 ablation | 见 CSV |
| `paper/paper_rl_ablation.csv` | RL 仿真 ablation | simulation only |
| `paper/paper_experiment_index.md` | 实验索引说明 | 人类可读 |
| `research/comparison.md` | 全实验对比表（8 行） | 含 ma_cross / ML / WF |

### OOS Sharpe 速查（vs baseline 0.586）

| 实验 | oos.sharpe | oos.total_return | 说明 |
|------|------------|------------------|------|
| server_walk_forward_001 | **0.586** | 0.443 | **主 baseline** |
| server_walk_forward_text_001 | 0.563 | 0.420 | smoke 200 条 + fillna(0) |
| server_walk_forward_text_002 | 0.579 | 0.443 | 100% 占位文本覆盖 |
| server_walk_forward_text_003 | 0.565 | 0.421 | Finnhub 真实新闻 ~2.4% 覆盖 |

### 非 OOS（仅作对照，勿作主结论）

| 实验 | sharpe | 说明 |
|------|--------|------|
| server_ma_cross_real_001 | 1.00 | 规则策略 in-sample |
| server_ml_backtest_001 | **2.78** | ML 单段回测，**非 OOS** |
| server_lgbm_gpu_001 | test_auc 0.479 | 训练集指标 |

---

## 二、目录结构（45 个文件，约 888 KB）

```
docs/ppt_data/
├── DATA_MANIFEST.md          ← 本清单
├── experiments/
│   └── experiments.json      ← ExperimentMemory 全量（8 条）
├── paper/                    ← M13.3 论文级导出（6 文件）
├── research/
│   ├── comparison.md
│   └── comparison.csv
├── walk_forward/
│   ├── baseline_walk_forward_latest/   ← OOS baseline 明细
│   ├── walk_forward_text_001/
│   ├── walk_forward_text_002/
│   └── walk_forward_text_003/
├── ma_cross/
│   └── server_ma_cross_real_001/       ← 均线交叉回测
├── ml_backtest/
│   └── ml_backtest_latest/             ← ML 单段（对照用）
├── lgbm/
│   └── metrics.json, metadata.json, feature_importance.csv
├── text/
│   ├── text_signal_audit_wf001|002|003/
│   └── real_news_alignment_wf003/
└── llm/
    └── EXP-LLM-002*.json
```

---

## 三、分目录文件说明

### `paper/` — 论文/PPT 主表

| 文件 | 格式 | 内容 |
|------|------|------|
| `paper_main_results.csv` | CSV | OOS walk-forward 主结果 |
| `paper_text_ablation.csv` | CSV | 文本实验 OOS 对比 |
| `paper_population_ablation.csv` | CSV | 种群策略 ablation |
| `paper_rl_ablation.csv` | CSV | RL 仿真（非真实交易） |
| `paper_experiment_index.md` | MD | 实验 ID 与说明索引 |
| `audit_summary.json` | JSON | M13 审计摘要 |

### `walk_forward/*/` — 各实验明细

每个子目录典型含：

| 文件 | PPT 用途 |
|------|----------|
| `metrics.json` | OOS/train/val/test 汇总指标 |
| `summary.md` | 人类可读摘要表 |
| `windows.csv` | 19 窗滚动明细（每窗 sharpe/return） |
| `oos_equity_curve.csv` | OOS 权益曲线（画图） |

### `ma_cross/` — 规则基线

| 文件 | 用途 |
|------|------|
| `metrics.json` | total_return≈2.02, sharpe≈1.00 |
| `equity_curve.csv` | 权益曲线 |
| `trades.csv` | 成交记录 |
| `summary.md` | 摘要 |

### `ml_backtest/` — ML 单段（⚠️ 非 OOS）

| 文件 | 用途 |
|------|------|
| `metrics.json` | sharpe 2.78（in-sample 对照） |
| `equity_curve.csv` | 权益曲线 |

### `lgbm/` — LightGBM 训练

| 文件 | 用途 |
|------|------|
| `metrics.json` | train/val/test AUC |
| `metadata.json` | device=cuda 等 |
| `feature_importance.csv` | 特征重要性柱状图 |

### `text/` — 文本信号审计

| 目录 | 用途 |
|------|------|
| `text_signal_audit_wf001` | 200 条 smoke 覆盖率 |
| `text_signal_audit_wf002` | 100% 占位覆盖 |
| `text_signal_audit_wf003` | Finnhub 真实新闻 |
| `real_news_alignment_wf003` | 新闻对齐 metrics |

### `llm/` — LLM 实验记录

| 文件 | 用途 |
|------|------|
| `EXP-LLM-002.json` | ResearchAgent 输出 |
| `EXP-LLM-002-constrained.json` | 约束版 |

---

## 四、未纳入（体积大或含敏感信息）

| 路径 | 原因 |
|------|------|
| `datasets/raw/*.parquet` | 原始 OHLCV，~250KB+，gitignore |
| `datasets/features/*.parquet` | 特征表，gitignore |
| `models/**/*.pkl` | 模型权重，gitignore |
| `.env` | API Key / DSN |
| `logs/` | 运行日志 |

如需本地复现，在服务器执行：

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS
python scripts/export_paper_artifacts.py \
  --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
  --output-dir docs/ppt_data/paper
```

---

## 五、PPT 建议图表

1. **主结论**：`paper_main_results.csv` → 柱状图 oos.sharpe（4 条 WF）
2. **baseline vs text**：`walk_forward/baseline_*` vs `walk_forward_text_*` 的 `oos_equity_curve.csv`
3. **窗口稳定性**：`windows.csv` → 每窗 oos_sharpe 折线
4. **ML 过拟合对照**：同一页展示 ML sharpe 2.78 vs OOS 0.586（标注 in-sample / OOS）
5. **特征重要性**：`lgbm/feature_importance.csv`
6. **文本覆盖**：`text/text_signal_audit_wf003/summary.md`
