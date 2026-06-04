# 金融文本模型计划（Plus M6）

更新时间：2026-06-04（EXP-TEXT-001 / EXP-TEXT-WF-001 / **EXP-TEXT-WF-002 ✅** 服务器）

> Codex 任务：[codex_prompt_M6.md](codex_prompt_M6.md) · 设计：[项目plus设计.md §M6](../项目plus设计.md#m6金融文本大模型--开源模型微调)

## 定位

M6 **不**用生成式 LLM / FinBERT **直接**预测价格或下单。路线：

```
FinancialTextRecord → sentiment/classifier → TextSignalRecord
    → merge_text_signals_into_features → LightGBM + walk-forward OOS
```

## 已验证（服务器）

| 实验 | 结果 |
|------|------|
| **EXP-TEXT-001** | ModelScope 本地 FinBERT；200 signals → `signals_finbert.parquet` |
| **EXP-TEXT-WF-001** | `features_with_text.parquet` 6033×20；OOS sharpe **0.563** vs baseline **0.586**（Δ **-0.023**；3.32% 覆盖） |
| **EXP-TEXT-WF-002** | 100% 覆盖 + 占位 JSONL；OOS sharpe **0.579** vs baseline **0.586**（Δ **-0.007**） |

**Exploratory 结论**：wf001 低覆盖（200/6033）下 OOS sharpe **0.563**；wf002 将覆盖率提至 **100%** 后回升至 **0.579**，仍略低于 baseline **0.586**。占位文本非真实新闻；覆盖率是重要因素，但尚不足以超越 ML 主基线。

## EXP-TEXT-WF-002 设计

EXP-TEXT-WF-002 的目标不是直接证明文本信号一定有效，而是用更高覆盖率、更清晰时间对齐和同一 walk-forward 协议，重新检验文本增强是否能超过 EXP-20260602-008 的 **0.586** 主基线。

第一步必须先做覆盖率审计：

```bash
# 若尚无 news_wf002.jsonl，先从 features 生成全量对齐占位 JSONL
python scripts/build_text_records_from_features.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --output-path /mnt/localDisk3/weizian/datasets/text/news_wf002.jsonl

python scripts/audit_text_signals.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --signals-path /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf002.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/text_signal_audit_wf002
```

审计输出：

- `metrics.json`：`feature_rows`、`signal_rows`、`matched_rows`、`coverage_ratio`、日期范围、symbol 覆盖
- `summary.md`：可直接写入实验日志的覆盖率摘要

论文记录时必须同时报告：

- 文本覆盖率 `coverage_ratio`
- 覆盖 symbol 数量
- 文本信号日期范围
- OOS sharpe 与 baseline **0.586** 的差值
- 是否仍使用 `fillna(0)` 或其他缺失值策略

## 服务器配置示例（不入库 secrets）

| 文件 | 说明 |
|------|------|
| [configs/text_model.server.yaml.example](../configs/text_model.server.yaml.example) | 本地 FinBERT 路径 |
| [configs/features.text.server.yaml.example](../configs/features.text.server.yaml.example) | text_signals merge |

复制为 `configs/text_model.server.yaml`、`configs/features.text.yaml` 并按路径调整。

## HuggingFace / ModelScope

- 服务器上 **huggingface.co 常不可达** → 见 [mistakes.md M-018](../mistakes.md#m-018-服务器-huggingface-hub-不可达)
- `.env`：`HF_TOKEN`、`HF_HOME=/mnt/localDisk3/weizian/models/hf`（**不入库**）

## 服务器验收流程（已跑通）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[ml,text]"
python -m pytest -v   # 161 passed

# 1) FinBERT signals (EXP-TEXT-001)
python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml ...

# 2) Features + fillna(0) on finbert_sentiment
python scripts/build_features.py --config configs/features.text.yaml \
  --storage-config configs/storage.server.yaml \
  --output /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet

# 3) Walk-forward (EXP-TEXT-WF-001)
python scripts/run_walk_forward.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet \
  --experiment-name server_walk_forward_text_001 \
  --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_001 \
  --storage-config configs/storage.server.yaml

python scripts/compare_experiments.py \
  --storage-config configs/storage.server.yaml \
  --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
  --output-dir /mnt/localDisk3/weizian/reports/research
```

## OOS 对比流程

1. Baseline：**EXP-20260602-008** / `server_walk_forward_001` → **oos.sharpe 0.586**
2. Text run：`server_walk_forward_text_001` → **oos.sharpe 0.563**（EXP-TEXT-WF-001）
3. 仅 walk-forward **OOS** 可写论文结论；单段 ML sharpe 2.78 **禁止**混比

## 待验证

| 编号 | 内容 |
|------|------|
| EXP-TEXT-WF-003 | 真实新闻 + 时间对齐 + walk-forward | 待服务器；见 [real_news_text_experiment.md](real_news_text_experiment.md) |

## 相关文档

- [experiment_log.md](experiment_log.md)
- [server_commands.md](server_commands.md) §6.9+
- [research_protocol.md](research_protocol.md)
