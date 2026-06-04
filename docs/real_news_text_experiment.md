# EXP-TEXT-WF-003 Real Financial News Text Experiment

更新时间：2026-06-04  
状态：设计 + 本地工具实现；服务器真实新闻跑数待验证

## 目标

EXP-TEXT-WF-003 replaces feature-aligned placeholder headlines with real timestamped financial news. The goal is to test whether real text content adds incremental information beyond deterministic technical features under the same walk-forward OOS protocol.

EXP-TEXT-WF-003 用真实、带发布时间戳的金融新闻替代 feature-aligned 占位标题。目标是在相同 walk-forward OOS 协议下，检验真实文本内容是否能提供超出确定性技术特征的信息增量。

## 背景

| Experiment | Text Coverage | OOS Sharpe | OOS Total Return | Interpretation |
|------------|---------------|------------|------------------|----------------|
| EXP-20260602-008 | n/a | **0.586** | **0.443** | ML main baseline |
| EXP-TEXT-WF-001 | 3.32% | **0.563** | **0.420** | sparse FinBERT smoke |
| EXP-TEXT-WF-002 | 100% | **0.579** | **0.443** | placeholder headlines |

WF-002 narrowed the gap from `-0.023` to `-0.007`, but it used placeholder headlines. Therefore it can only support the claim that coverage matters, not that real news sentiment improves the baseline.

WF-002 将差距从 `-0.023` 收窄到 `-0.007`，但使用的是占位标题。因此它只能说明覆盖率重要，不能证明真实新闻情绪已提升主基线。

## Input Schema

Input path: JSONL or parquet. One record per news item.
Minimal schema example: [examples/real_news_wf003.sample.jsonl](examples/real_news_wf003.sample.jsonl).

```json
{
  "published_at": "2021-03-15T13:20:00",
  "symbol": "AAPL",
  "source": "provider_or_dataset_name",
  "title": "Apple shares rise after supplier report",
  "text": "Optional full text or article snippet.",
  "url": "https://example.com/article",
  "metadata": {
    "provider": "example",
    "language": "en"
  }
}
```

Required fields:

- `published_at`
- `symbol`
- `source`
- `title` or `text`

Secrets, API keys, and private provider credentials must not be stored in JSONL.

The sample file is only a schema fixture. It is not real news data and must not
be used for OOS conclusions.

## Alignment Rule

Real news must be aligned by publication availability:

- News before or during market hours maps to the same trading bar.
- News after `market_close` maps to the next available feature bar for that symbol.
- News with unknown symbols is dropped and counted.
- News without a future available bar is dropped and counted.

This prevents future text leakage. The aligned output is ordinary `FinancialTextRecord` JSONL and can be passed into `scripts/train_text_model.py`.

## Local Tools

| Tool | Purpose |
|------|---------|
| `scripts/fetch_real_news.py` | Download Finnhub company news JSONL |
| `scripts/align_real_news.py` | Align real news JSONL/parquet to feature dates |
| `scripts/audit_text_signals.py` | Audit text signal coverage after FinBERT signal generation |
| `scripts/train_text_model.py` | Generate FinBERT/mock sentiment signals |
| `scripts/run_walk_forward.py` | Produce OOS metrics |

## Server Flow

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[ml,text]"
python -m pytest tests/test_text_signals.py -v

# 0) Fetch real news from Finnhub (requires FINNHUB_API_KEY in .env).
python scripts/fetch_real_news.py \
  --source finnhub \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --output-path /mnt/localDisk3/weizian/datasets/text/real_news_wf003.jsonl

# 1) Align real news to tradable feature bars.
python scripts/align_real_news.py \
  --news-path /mnt/localDisk3/weizian/datasets/text/real_news_wf003.jsonl \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/real_news_alignment_wf003 \
  --market-close 16:00

# 2) Generate text signals from aligned news.
python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml \
  --text-path /mnt/localDisk3/weizian/reports/real_news_alignment_wf003/aligned_news.jsonl \
  --output-dir /mnt/localDisk3/weizian/models/text/exp_text_wf003 \
  --signals-output /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf003.parquet

# 3) Audit coverage.
python scripts/audit_text_signals.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --signals-path /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf003.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/text_signal_audit_wf003

# 4) Build text-enhanced features.
# Edit configs/features.text.yaml so text_signals_path points to signals_finbert_wf003.parquet.
python scripts/build_features.py \
  --config configs/features.text.yaml \
  --storage-config configs/storage.server.yaml \
  --input /mnt/localDisk3/weizian/datasets/raw/market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/features/features_with_text_wf003.parquet

# 5) Walk-forward OOS.
python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text_wf003.parquet \
  --experiment-name server_walk_forward_text_003 \
  --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_003
```

## Reporting Rules

Every report must include:

- real news source and record count
- aligned record count
- dropped record count and reasons
- coverage ratio after signal generation
- OOS sharpe / total return / max drawdown
- comparison to EXP-20260602-008 (`oos.sharpe = 0.586`)
- comparison to EXP-TEXT-WF-002 (`oos.sharpe = 0.579`, placeholder text)

Correct wording:

> EXP-TEXT-WF-003 evaluates real timestamped financial news under the same walk-forward protocol. Its result should be interpreted together with coverage and alignment statistics.

Incorrect wording:

> FinBERT or LLM text signals are useful without OOS validation.

## Current Status

Implemented locally:

- `RealNewsRecord`
- `load_real_news_records()`
- `align_real_news_to_features()`
- `write_real_news_alignment_report()`
- `scripts/align_real_news.py`
- synthetic tests for after-close alignment and leakage prevention

Pending:

- acquire or prepare real financial news JSONL
- run server EXP-TEXT-WF-003
- compare against `0.586`, `0.579`, and `0.563`
