# Quant MAS 数据源说明（Plus M2）

更新时间：2026-06-02

> 机器可读配置：`configs/data_sources.yaml`  
> CLI：`python scripts/download_data.py --help`

## 总览

| source | kind | 环境变量 | 状态 | 说明 |
|--------|------|----------|------|------|
| `stooq` | ohlcv | `STOOQ_API_KEY` | **verified** | 服务器 EXP-20260601-004 |
| `yfinance` | ohlcv | — | planned | 易限流，备用 |
| `auto` | ohlcv | `STOOQ_API_KEY` | planned | yfinance → Stooq fallback |
| `alpha_vantage` | ohlcv | `ALPHAVANTAGE_API_KEY` | **verified** | 免费 tier 须 `outputsize=compact` |
| `finnhub` | ohlcv | `FINNHUB_API_KEY` | **blocked（免费 tier）** | `/stock/candle` 403，需付费 |
| `fred` | macro | `FRED_API_KEY` | **verified** | DGS10 262 rows |
| `sec_edgar` | filings | `SEC_EDGAR_USER_AGENT` | 待验证 | 需真实 User-Agent |

**pytest**：`tests/test_data_sources.py` 全部 mock HTTP，不联网。  
**真实 API**：仅服务器手工 smoke test（见 EXP-DATA-001，待验证）。

## OHLCV 源（输出 parquet）

```bash
python scripts/download_data.py \
  --symbols AAPL MSFT \
  --start 2018-01-01 --end 2025-12-31 \
  --source stooq \
  --storage-config configs/storage.server.yaml
```

`--source` 可选：`yfinance` | `stooq` | `auto` | `alpha_vantage` | `finnhub`

## FRED 宏观序列

```bash
python scripts/download_data.py \
  --source fred \
  --series-id DGS10 \
  --start 2020-01-01 --end 2025-12-31 \
  --storage-config configs/storage.server.yaml
```

输出：`{raw_data_dir}/macro/{series_id}.parquet`

## SEC EDGAR

```bash
python scripts/download_data.py \
  --source sec_edgar \
  --cik 0000320193 \
  --storage-config configs/storage.server.yaml
```

输出：`{raw_data_dir}/sec/{cik}_{kind}.json`  
`SEC_EDGAR_USER_AGENT` 格式：`YourName your@email.com`（SEC 强制）

### Finnhub 403（免费账户）

免费 tier 调用 `/stock/candle` 会返回：

```json
{"error":"You don't have access to this resource."}
```

**非代码 bug**；需升级 Finnhub 付费计划，或继续用 **Stooq / Alpha Vantage** 作 OHLCV。

### Alpha Vantage 免费 tier

- 默认 **`outputsize=auto`**：先 `full`，再 `compact`
- **`compact` 仅含最近 ~100 个交易日** — 请求 2024 年区间会得到 0 行（不是 key 坏了）
- **历史 OHLCV** 请用 **Stooq**；AV smoke 请用**最近 3 个月**，例如：

```bash
python scripts/download_data.py --source alpha_vantage \
  --symbols AAPL --start 2026-01-01 --end 2026-06-01 \
  --storage-config configs/storage.server.yaml
```

## API Key 注册

| 变量 | 注册 |
|------|------|
| `STOOQ_API_KEY` | https://stooq.com/q/d/?s=aapl.us&get_apikey |
| `ALPHAVANTAGE_API_KEY` | https://www.alphavantage.co/support/#api-key |
| `FINNHUB_API_KEY` | https://finnhub.io/register |
| `FRED_API_KEY` | https://fred.stlouisfed.org/docs/api/api_key.html |
| `SEC_EDGAR_USER_AGENT` | 无需 key，填合规 User-Agent |

Key 只放 `.env`，不入 git。
