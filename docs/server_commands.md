# Quant MAS 服务器操作指令

GitHub 仓库：[https://github.com/ytq0198/Quant-MAS](https://github.com/ytq0198/Quant-MAS)

**推荐服务器路径**：`/mnt/localDisk3/weizian/Quant-MAS`

> **重要**：必须先 `conda activate quant-mas`，再用 `python -m pytest` 和 `python -m pip`，不要裸敲 `pytest` / `pip`。

## 验证记录

| 日期 | 项目 | 结果 | 备注 |
|------|------|------|------|
| 2026-06-03 | v3 M10 local_vLLM smoke | ResearchAgent `local_vllm` ✅ | EXP-LLM-002 |
| 2026-06-01 | v3 M9/M10 服务器 pytest | **212 passed**（11.39s） | EXP-20260602-028 |
| 2026-06-01 | v3 M9 企业 DB（本地） | **207 passed**（+12）；enterprise **12/12** | EXP-20260602-025 |
| 2026-06-01 | Plus M8 MCP/A2A 服务器 | **195 passed**（12.41s）；export_agent_cards ✅ | EXP-20260602-024 |
| 2026-06-01 | Plus M7 服务器 | **180 passed**（10.15s）；RL dry-run ✅ | EXP-20260602-022 |
| 2026-06-01 | Plus M8 MCP/A2A（本地） | **195 passed**（+15） | EXP-20260602-023 |
| 2026-06-01 | Plus M7 RL 模拟（本地） | **180 passed**（+19） | EXP-20260602-021 |
| 2026-06-03 | EXP-TEXT-WF-001 text + walk-forward | oos.sharpe **0.563** vs **0.586** | EXP-TEXT-001 |
| 2026-06-03 | Plus M6 文本信号（服务器） | **161 passed**（22.14s） | EXP-20260602-020 |
| 2026-06-03 | Plus M6 文本信号（本地） | **161 passed** | EXP-20260602-019 |
| 2026-06-03 | Plus M5 上下文/LLM（服务器） | **150 passed**（7.24s） | EXP-20260602-018 |
| 2026-06-03 | Plus M5 上下文/LLM（本地） | **150+1 warning** | EXP-20260602-017 |
| 2026-06-03 | Plus M4 LangGraph 服务器 | langgraph dry-run ✅ | EXP-20260602-016 |
| 2026-06-02 | Plus M3 Memory/RAG v2（本地+服务器） | **126 passed** | EXP-20260602-013/014 |
| 2026-06-02 | Plus M2 数据扩展（本地+服务器） | **115 passed** / test_data_sources **13/13** | EXP-20260602-011/012 |
| 2026-06-02 | Plus M1 research baseline (local) | **102 passed** | EXP-20260602-009 |
| 2026-06-01 | pytest（Prompt 20 后，服务器） | **98 passed**（1.93s） | EXP-20260601-014 |
| 2026-06-01 | pytest（Prompt 20 后，本地） | **98 passed** | EXP-20260601-013 |
| 2026-06-02 | Walk-forward 服务器 | `server_walk_forward_001`；OOS sharpe **0.586** | Prompt 17 ✅ |
| 2026-06-02 | pytest | **71 passed**（Prompt 17 后） |
| 2026-06-02 | Walk-forward 本地 | **71 passed**；Prompt 17 代码 ✅ | 无 |
| 2026-06-02 | GPU 训练 | `server_lgbm_gpu_001`；device=cuda；test AUC 0.479 | 见 M-010 |
| 2026-06-02 | ML 回测 | `server_ml_backtest_001`；sharpe **2.78** | Prompt 16 ✅ |
| 2026-06-02 | pytest（旧） | **44 passed**（Python 3.11.15，1.19s） |
| 2026-06-01 | LightGBM 训练 | `server_lgbm_001`；test AUC 0.466 | 过拟合基线 |
| 2026-06-01 | Prompt 16 + GPU 本地 | **68 passed**；`--device` 可用 | 无 |
| 2026-06-01 | 真实数据 + pipeline | Stooq 6033 rows；`server_ma_cross_real_001` | — |

### pytest

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS
python -m pytest -v
```

## 一、首次部署

```bash
# 1. 创建目录并克隆
mkdir -p /mnt/localDisk3/weizian/conda_envs
cd /mnt/localDisk3/weizian
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS

# 2. 创建数据目录
mkdir -p /mnt/localDisk3/weizian/datasets/{raw,processed,features}
mkdir -p /mnt/localDisk3/weizian/{models,reports,logs}

# 3. 配置服务器路径
cp configs/storage.server.yaml.example configs/storage.server.yaml

# 4. 创建 Python 3.11 环境（必须用 3.11，不能用 3.9）
# 若已有错误版本的 env，先删除：
# rm -rf /mnt/localDisk3/weizian/conda_envs/quant-mas

CONDA_ENV_PREFIX=/mnt/localDisk3/weizian/conda_envs/quant-mas bash server/setup_server.sh

# 5. 激活并验证
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python --version              # 必须 3.11.x
python -m pip --version       # 必须也是 3.11，不能是 3.9

# 6. 若 setup 失败，手动安装（不要用 bare pip）
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip install -r requirements-data.txt   # 下载行情数据需要
python -m pip install -r requirements-ml.txt     # ML 训练需要
python -m pytest -v
```

> **常见错误 A**：`Python 3.9.13 not in '>=3.11'` → 环境是 3.9，需 `rm -rf .../conda_envs/quant-mas` 后重建。
>
> **常见错误 B**：`python` 是 3.11 但 `pip` 来自 `~/.local` 的 3.9 → **永远用 `python -m pip`**，不要直接敲 `pip`：
>
> ```bash
> conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
> python -m pip install -e ".[data,ml]"
> ```

自检：

```bash
which python      # 应指向 /mnt/localDisk3/weizian/conda_envs/quant-mas/bin/python
python --version  # 必须为 3.11.x（不能是 3.9）
which pytest      # 应在同一 conda env 内
```

## 二、日常同步代码

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip install -r requirements-data.txt
python -m pip install -r requirements-ml.txt
python -m pytest -v
```

## 三、下载真实行情数据

**yfinance 限流**：出现 `YFRateLimitError` 时不是配置错误。推荐改用 **Stooq + API Key**。

### 0. 申请 Stooq API Key（一次性）

1. 浏览器打开：https://stooq.com/q/d/?s=aapl.us&get_apikey  
2. 完成 captcha，复制 32 位 apikey  
3. 在服务器项目根目录：

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
cp .env.example .env
nano .env   # 设置 STOOQ_API_KEY=你的key（勿 commit）
```

验证：

```bash
python scripts/download_data.py \
  --symbols AAPL \
  --start 2018-01-01 --end 2019-01-01 \
  --source stooq \
  --storage-config configs/storage.server.yaml \
  --filename AAPL_2018.parquet
```

### 方式 A：一键 resilient 脚本（推荐）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
git pull origin main
python -m pip install -e .

# 需已在 .env 中设置 STOOQ_API_KEY
SOURCE=stooq SYMBOLS="AAPL" bash server/download_data_resilient.sh
SOURCE=stooq SYMBOLS="AAPL MSFT SPY" bash server/download_data_resilient.sh

# Yahoo 限流后若坚持用 yfinance，需等 30–60 分钟：
# INITIAL_COOLDOWN_SECONDS=1800 SOURCE=yfinance SYMBOLS="AAPL" bash server/download_data_resilient.sh
```

脚本会：
1. 自动 `source .env` 读取 `STOOQ_API_KEY`
2. 每个标的 **按年** 单独下载（`AAPL_2018.parquet` …）
3. 已存在文件 **自动跳过**（中断可续传）
4. 最后合并为 `datasets/raw/market_data.parquet`

### 方式 B：手动单条下载

`download_data.py` 启动时会自动加载项目根 `.env`（`STOOQ_API_KEY`）。

```bash
python scripts/download_data.py \
  --symbols AAPL \
  --start 2018-01-01 --end 2019-01-01 \
  --source stooq \
  --storage-config configs/storage.server.yaml \
  --filename AAPL_2018.parquet \
  --skip-existing
sleep 30
```

合并：

```bash
python scripts/merge_parquet.py \
  --input-dir /mnt/localDisk3/weizian/datasets/raw \
  --pattern "*_*.parquet" \
  --exclude market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/raw/market_data.parquet
```

### 方式 C：手动 CSV（限流严重时）

把 CSV 放到 `/mnt/localDisk3/weizian/datasets/raw/manual/`，再自行转为 parquet（Phase 3 可接）。

## 四、端到端 Pipeline

真实数据已下载时（`market_data.parquet` 已存在）：

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas

python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml \
  --skip-download \
  --experiment-name server_ma_cross_real_001
```

**已验证（2026-06-01）**：6033 feature rows；sharpe ≈ 1.00；产物 `/mnt/localDisk3/weizian/reports/server_ma_cross_real_001/`。

Synthetic / 小数据 smoke test：`bash server/run_small_pipeline.sh`

## 五、ML 训练（Prompt 15 + GPU）

### CPU 训练（默认 / 对照）

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS
python -m pip install -r requirements-ml.txt

python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.server.yaml \
  --experiment-name server_lgbm_001
```

### GPU / CUDA 训练（A6000）

**首次 GPU 训练前**必须确认 LightGBM 为 CUDA 编译版。PyPI 默认 wheel 常为 **CPU-only**；仅 `nvidia-smi` 可见 **不能** 保证 `--device cuda` 可用。若未编译 CUDA 版，`fit()` 会直接报错且 **不会** 自动 fallback：

```text
[LightGBM] [Fatal] CUDA Tree Learner was not enabled in this build.
```

详见 [`mistakes.md` M-010](../mistakes.md#m-010-lightgbm-pypi-wheel-为-cpu-only)。

#### 0. 安装 CUDA 版 LightGBM（服务器首次必做，约 5 分钟）

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS

python -m pip uninstall -y lightgbm
python -m pip install --no-binary lightgbm \
  --config-settings=cmake.define.USE_CUDA=ON 'lightgbm==4.6.0'

# 冒烟：应不报错
python -c "from lightgbm import LGBMClassifier; LGBMClassifier(device='cuda').fit([[0],[1]], [0,1])"
```

环境：4× NVIDIA RTX A6000，驱动 580，CUDA 13.0（2026-06-02 已验证）。

#### 1. 训练

```bash
nvidia-smi

python scripts/train_model.py \
  --config configs/train.gpu.yaml \
  --storage-config configs/storage.server.yaml \
  --device cuda \
  --experiment-name server_lgbm_gpu_001

# 确认 device 字段（应为 cuda 且 fallback=false）
grep device /mnt/localDisk3/weizian/models/lightgbm_direction_latest/metadata.json
grep device /mnt/localDisk3/weizian/models/lightgbm_direction_latest/metrics.json
```

#### CPU 对照（可选，与 EXP-20260601-006 对比）

```bash
python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.server.yaml \
  --device cpu \
  --experiment-name server_lgbm_cpu_001
```

~6k 行数据上 GPU 加速可能不明显；对照重点为 metrics 是否一致、metadata 中 `device_resolved` 是否正确。

无 GPU 或 CUDA 不可用时，Quant MAS 在 **设备检测阶段** 可 fallback 到 CPU；但若 `device=cuda` 且 LightGBM 本身无 CUDA 支持，会在 `fit()` 时 **Fatal**（见 M-010）。

## 六、ML 回测 / Walk-forward

**ML 回测（Prompt 16 ✅，服务器已验证 EXP-20260602-005）**：

```bash
git pull origin main
python -m pip install -e .
python -m pytest -v

python scripts/run_ml_backtest.py \
  --config configs/backtest_ml.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --model-path /mnt/localDisk3/weizian/models/lightgbm_direction_latest/model.pkl \
  --experiment-name server_ml_backtest_001
```

产物示例（2026-06-02）：sharpe **2.78**，max_drawdown **-0.246**，2011 bars；报告 `outputs/reports/ml_backtest_latest/summary.md`。

**Walk-forward（Prompt 17 ✅，EXP-20260602-008）**：

已验证（2026-06-02）：19 窗口，约 17s，OOS sharpe **0.586**，total_return **0.443**，auc_mean **0.472**。

```bash
git pull origin main
python -m pip install -e .
python -m pytest -v   # 预期 126 passed（Plus M3 后）

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --experiment-name server_walk_forward_001
```

产物：`metrics.json`（含 train/val/test/oos）、`windows.csv`、`oos_equity_curve.csv`、`oos_trades.csv`、`summary.md`。

## 六点五、Plus M2 数据 API smoke（EXP-DATA-001）✅

> **切勿**把真实 key 写入 `.env.example` 或 commit 到 GitHub。只在服务器 **`/mnt/localDisk3/weizian/Quant-MAS/.env`** 配置（该文件已在 `.gitignore`）。

**已通过**（2026-06-02，EXP-20260602-012）：FRED DGS10 262 行、Stooq 105 行、Alpha Vantage 100 行。Finnhub 免费 tier 403（预期）。SEC 未测。

复现命令：

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest tests/test_data_sources.py -v   # 预期 13 passed

# 首次：从模板创建 .env，用 nano/vim 填入 key（不要 paste 到 .env.example）
cp .env.example .env
nano .env
```

`.env` 需包含（示例，值用你自己的）：

```env
STOOQ_API_KEY=...
ALPHAVANTAGE_API_KEY=...
FINNHUB_API_KEY=...
FRED_API_KEY=...
SEC_EDGAR_USER_AGENT=YourName your@email.com   # SEC 必填；其余 M2 源已填 key 时可先测 FRED/AV/Finnhub
```

`download_data.py` 会通过 `load_repo_dotenv()` 自动加载项目根目录 `.env`。

**建议 smoke 顺序**（有 key 的源）：

```bash
# 1. FRED 宏观（最稳）
python scripts/download_data.py --source fred --series-id DGS10 \
  --start 2024-01-01 --end 2024-12-31 \
  --storage-config configs/storage.server.yaml
ls -la /mnt/localDisk3/weizian/datasets/raw/macro/

# 2. Alpha Vantage OHLCV（免费 tier 仅 ~100 近期交易日，勿用 2024 区间）
python scripts/download_data.py --source alpha_vantage \
  --symbols AAPL --start 2026-01-01 --end 2026-06-01 \
  --storage-config configs/storage.server.yaml

# 3. Finnhub OHLCV
python scripts/download_data.py --source finnhub \
  --symbols AAPL --start 2024-01-01 --end 2024-06-01 \
  --storage-config configs/storage.server.yaml

# 4. Stooq（已有 key，对照）
python scripts/download_data.py --source stooq \
  --symbols AAPL --start 2024-01-01 --end 2024-06-01 \
  --storage-config configs/storage.server.yaml
```

SEC（需先改 `.env` 里 `SEC_EDGAR_USER_AGENT` 为真实姓名+邮箱）：

```bash
python scripts/download_data.py --source sec_edgar --cik 0000320193 \
  --storage-config configs/storage.server.yaml
ls -la /mnt/localDisk3/weizian/datasets/raw/sec/
```

通过后：记录见 `docs/experiment_log.md` **EXP-20260602-012** / **EXP-DATA-001**。

## 六点六、Plus M3 Memory/RAG（EXP-20260602-013）

M3 pull 后全量验收：

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v   # 预期 126 passed

python scripts/index_documents.py --help
python scripts/query_memory.py --help

# 可选 smoke（不联网，hash embedding）
python scripts/index_documents.py --dirs docs --vector-store in_memory
python scripts/query_memory.py --rag-query "walk-forward OOS sharpe"

python scripts/query_memory.py \
  --backend json \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json \
  --best-metric oos.sharpe
```

记录：**EXP-20260602-014**。默认 `--json-path outputs/reports/experiments.json` 非服务器 `reports_dir`。

## 六点七、Plus M4 LangGraph（EXP-20260602-015/016）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main   # 需 >= c0fa5e3（M-016 建边修复）
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pip install -e ".[orchestration]"

python -m pytest tests/test_langgraph_workflow.py::test_langgraph_build_and_dry_run_when_available -v
python scripts/run_langgraph_workflow.py --help
python scripts/run_langgraph_workflow.py --dry-run --backend sequential
python scripts/run_langgraph_workflow.py --dry-run --backend langgraph
# 全量（可选）：核心 137+1 skip；含 orchestration 138 passed
# python -m pytest -v
```

记录：**EXP-20260602-016**（2026-06-03，a6000-9961 @ `c0fa5e3`）。首次 M4 pull 若 langgraph backend 报 `zip() argument 2 is shorter`，见 [`mistakes.md`](../mistakes.md) **M-016**。

## 六点八、Plus M5 上下文/LLM（EXP-20260602-017/018 / EXP-LLM-001）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main   # 须含 43c812a（M-017 pytest 隔离）
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pip install -e ".[llm]"

python -m pytest tests/test_context_engineering.py -v   # 12 passed, 1 warning
python scripts/run_research_agent.py --help
python scripts/run_research_agent.py --task "Summarize OOS baseline vs latest ML run"
python -m pytest -v   # 150 passed（EXP-018：7.24s，含 .env LLM_API_KEY）

# 真实 LLM smoke（DeepSeek，key 在 repo 根 .env，不入库）：
python scripts/run_research_agent.py \
  --storage-config configs/storage.server.yaml \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json \
  --task "Explain walk-forward OOS sharpe baseline and compare to latest ML run" \
  --use-llm
# → EXP-LLM-001：llm_provider=openai_compatible，baseline oos.sharpe ≈ 0.586
```

记录：**EXP-20260602-018**（2026-06-03，a6000-9961 @ `43c812a`）；**EXP-LLM-001**（DeepSeek smoke）。`.env` 导致 mock 测试失败见 [`mistakes.md`](../mistakes.md) **M-017**。

## 六点九、Plus M6 文本信号 + Walk-forward（EXP-TEXT-001 / EXP-TEXT-WF-001）✅

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[ml,text]"
python -m pytest -v   # 161 passed

# 配置：复制 example → 编辑路径
# cp configs/text_model.server.yaml.example configs/text_model.server.yaml
# cp configs/features.text.server.yaml.example configs/features.text.yaml

# FinBERT（Hub 不可达时用 ModelScope 本地路径，见 mistakes.md M-018）
python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml \
  --text-path data/text/smoke_from_features.jsonl \
  --output-dir /mnt/localDisk3/weizian/models/text/exp_text_001 \
  --signals-output /mnt/localDisk3/weizian/datasets/text/signals_finbert.parquet \
  2>&1 | tee /mnt/localDisk3/weizian/logs/exp_text_001_finbert.log

python scripts/build_features.py \
  --config configs/features.text.yaml \
  --storage-config configs/storage.server.yaml \
  --input /mnt/localDisk3/weizian/datasets/raw/market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet
# fillna(0) on finbert_sentiment if sparse — see text_model_plan.md

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet \
  --experiment-name server_walk_forward_text_001 \
  --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_001

python scripts/compare_experiments.py \
  --storage-config configs/storage.server.yaml \
  --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
  --output-dir /mnt/localDisk3/weizian/reports/research
```

**EXP-TEXT-WF-001 结果**：oos.sharpe **0.563** vs baseline **0.586**（Δ -0.023）；200/6033 text 覆盖 + fillna(0)，exploratory。

**注意**：勿覆盖 `market_data.parquet` 为小样本（见 **M-019**）；应用 `merge_parquet.py` 恢复 6033 行。

记录：**EXP-20260602-020**（pytest 161）；**EXP-TEXT-001**；**EXP-TEXT-WF-001**。

详见 [`docs/text_model_plan.md`](text_model_plan.md)。

## 六点十、Plus M7 RL 模拟（EXP-20260602-021 / EXP-20260602-022）✅

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v   # 预期 180 passed

python scripts/run_rl_baseline.py --help
python scripts/run_rl_baseline.py --config configs/rl.yaml --policy random --dry-run \
  --output-dir /mnt/localDisk3/weizian/reports/rl_baseline_001

# 可选 policies: buy_hold | ml_copy（ml_copy 需 --signals-path）
python scripts/run_rl_baseline.py --config configs/rl.yaml --policy buy_hold --dry-run
```

**说明**：

- **simulation only** — 不接 broker；metrics 为 `simulation.*`，**不得**与 walk-forward `oos.sharpe` **0.586** 混比
- 可选：`pip install -e ".[rl]"` 安装 gymnasium wrapper（核心 pytest 不依赖）
- 记录：**EXP-20260602-021**（本地）；**EXP-20260602-022**（服务器 **180 passed**，10.15s）

详见 [`docs/rl_plan.md`](rl_plan.md)。

## 六点十一、Plus M8 MCP/A2A（EXP-20260602-023 / EXP-20260602-024）✅

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v   # 预期 195 passed

python scripts/export_agent_cards.py --help
python scripts/export_agent_cards.py --config configs/protocols.yaml \
  --output-dir /mnt/localDisk3/weizian/reports/protocols \
  --include-mcp-specs
```

**说明**：

- **内部 adapter only** — 不接外部 MCP server；不启动 network listener
- policy 默认 deny shell/broker/order/secrets
- 记录：**EXP-20260602-023**（本地 195 passed）；**EXP-20260602-024**（服务器 **195 passed**，12.41s）

详见 [`docs/protocols.md`](protocols.md)。

## 六点十二、v3 M9 企业 DB（EXP-025 / EXP-026）📋

### 6.12.1 服务器现状（2026-06-01 探测）

| 项 | 状态 |
|----|------|
| OS | Ubuntu 22.04.5 |
| Docker | 28.1.1 + Compose v2.35.1 已装 |
| 用户 weizian | **不在 docker 组**，无 sudo 免密 → 无法自启容器 |
| 5432 | 未监听（Postgres 未起） |
| Quant-MAS | **`0794bd6`（M8，195 pytest）** — M9 在 **`06a6a5d`** 待 pull |
| infra | `/mnt/localDisk3/weizian/infra/quant-mas-db/`（compose + setup.sh + .env） |
| Python 驱动 | psycopg 3.3.4、neo4j 6.2.0 ✅ |

### 6.12.2 阻塞解除（找管理员，二选一）

**推荐 A — 加入 docker 组（长期）**

```bash
# 管理员执行一次
sudo usermod -aG docker weizian
# weizian 必须退出 SSH 重新登录后生效
groups   # 应含 docker
```

**B — 管理员代启 Postgres（一次性）**

```bash
cd /mnt/localDisk3/weizian/infra/quant-mas-db
sudo docker compose up -d postgres
sudo docker exec quant-mas-postgres psql -U quant_mas -d quant_mas \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

weizian 获得 docker 权限并重新登录后：

```bash
bash /mnt/localDisk3/weizian/infra/quant-mas-db/setup.sh
# 可选 Neo4j：
# cd /mnt/localDisk3/weizian/infra/quant-mas-db && docker compose --profile neo4j up -d neo4j
```

密码仅在 `infra/quant-mas-db/.env` 与 `Quant-MAS/.env`（**勿 commit**）。

### 6.12.3 拉 M9 代码并验收（EXP-026）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git status
git checkout -- docs/experiment_log.md 2>/dev/null || true   # 若有本地文档改动
git fetch origin main
git log -1 --oneline origin/main   # 目标：M10 后含 212 pytest 的 commit
git merge --ff-only origin/main

conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pip install "psycopg[binary]>=3.1" neo4j   # 若未装
python -m pytest -v   # 预期 212 passed（M9+M10）

python -m pytest tests/test_memory_enterprise.py -v   # 12 passed
python -m pytest tests/test_context_engineering.py -v # 17 passed

# 真实 DB smoke（Postgres 已起且 POSTGRES_DSN 在 .env）
python scripts/query_memory.py --backend postgres --best-metric oos.sharpe
python scripts/index_documents.py --vector-store pgvector --dirs docs --embedding-dimensions 64
```

**说明**：

- pytest 默认 mock，**不依赖**真实 Postgres / vLLM；**212** 与 DB 是否启动无关
- 环境变量名：**`POSTGRES_DSN`**；vLLM：**`VLLM_BASE_URL`**
- 记录：**EXP-025** 本地 207；**EXP-027/028** 212；**EXP-026** DB smoke 待 Docker；**EXP-LLM-002** ✅

详见 [`docs/database_setup.md`](database_setup.md) §M9 · [`docs/context_engineering.md`](context_engineering.md) M10。

## 六点十三、v3 M10 LLM（EXP-027 / EXP-028 / EXP-LLM-002）✅

### 6.13.1 pytest（mock，不启 vLLM）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pytest tests/test_context_engineering.py -v   # 17 passed
python -m pytest -v                                     # 212 passed
```

记录：**EXP-20260602-027**（本地 212）；**EXP-20260602-028**（服务器 212，11.39s）。

### 6.13.2 vLLM 环境（独立 conda，勿装进 quant-mas）

```bash
# 一次性：独立环境
conda create -p /mnt/localDisk3/weizian/conda_envs/vllm python=3.11 -y
conda activate /mnt/localDisk3/weizian/conda_envs/vllm
pip install vllm
which vllm   # 必须在 .../conda_envs/vllm/bin/vllm，不是 ~/.local/bin/vllm
```

**模型**（服务器无法直连 huggingface.co 时用镜像下载到本地）：

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download Qwen/Qwen2.5-7B-Instruct \
  --local-dir /mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct \
  --local-dir-use-symlinks False
```

**踩坑**：

| 问题 | 处理 |
|------|------|
| `Network is unreachable`（HF） | 镜像下载 + 本地路径 serve |
| FlashInfer / CUDA 12 编译失败 | `export VLLM_USE_FLASHINFER_SAMPLER=0` |
| `vllm: command not found` | 先 `conda activate .../vllm` |
| GPU OOM（3GB free） | 旧 vLLM 仍占 GPU 0：`pkill -f "vllm serve"` 或 `kill <EngineCore PID>` |
| 误用 `VLLM_USE_FLASHINFER` | v0.22 无效；用 **`VLLM_USE_FLASHINFER_SAMPLER=0`** |

### 6.13.3 启动 vLLM（终端 1，建议 tmux）

```bash
tmux new -s vllm
conda activate /mnt/localDisk3/weizian/conda_envs/vllm

export HF_HUB_OFFLINE=1
export VLLM_USE_FLASHINFER_SAMPLER=0
unset VLLM_BASE_URL VLLM_MODEL VLLM_USE_FLASHINFER

CUDA_VISIBLE_DEVICES=0 vllm serve /mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct \
  --host 127.0.0.1 --port 8000 --dtype auto --max-model-len 8192 \
  --served-model-name Qwen/Qwen2.5-7B-Instruct --enforce-eager
# 等到 Application startup complete；Ctrl+B D detach
```

### 6.13.4 ResearchAgent smoke（终端 2，EXP-LLM-002）

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS

curl -s http://127.0.0.1:8000/v1/models | python -m json.tool

export VLLM_BASE_URL=http://127.0.0.1:8000
export VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct

mkdir -p /mnt/localDisk3/weizian/reports/llm

python scripts/run_research_agent.py \
  --provider local_vllm --use-llm \
  --task "Interpret ONLY the walk-forward OOS baseline EXP-20260602-008 (oos.sharpe ≈ 0.586). Do NOT treat workflow_ml_backtest, single-segment ML sharpe, or pytest milestones as paper metrics. List three research risks." \
  --experiment-name walk-forward \
  --rag-query "OOS baseline EXP-20260602-008 sharpe 0.586" \
  --output-json /mnt/localDisk3/weizian/reports/llm/EXP-LLM-002-constrained.json
```

验收：`llm_provider=local_vllm`；RAG 命中 `experiment_log.md`；**不**将单段 ML sharpe 当论文指标。

记录：**EXP-LLM-002** ✅（2026-06-03，Qwen2.5-7B-Instruct @ GPU 0，vLLM 0.22.0）。

## 七、删除旧部署（如曾在 ~/quant-mas 建过）

```bash
rm -rf ~/quant-mas
# conda 环境可选删除：conda env remove -n quant-mas -y
```

## 八、本地 ↔ 服务器工作流

| 操作 | 本地 Windows | 服务器 |
|------|-------------|--------|
| 写代码 | Codex | — |
| 测试 | `python -m pytest -v` | `conda activate quant-mas && python -m pytest -v` |
| 推送/拉取 | `git push` | `git pull` |

本地推送：

```powershell
cd "D:\scientific reasearch and work\SRTP\Quant MAS"
git add .
git commit -m "your message"
git push origin main
```
