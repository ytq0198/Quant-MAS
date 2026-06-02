# Quant MAS 服务器操作指令

GitHub 仓库：[https://github.com/ytq0198/Quant-MAS](https://github.com/ytq0198/Quant-MAS)

**推荐服务器路径**：`/mnt/localDisk3/weizian/Quant-MAS`

> **重要**：必须先 `conda activate quant-mas`，再用 `python -m pytest` 和 `python -m pip`，不要裸敲 `pytest` / `pip`。

## 验证记录

| 日期 | 项目 | 结果 | 备注 |
|------|------|------|------|
| 2026-06-01 | pytest（Prompt 19 后，服务器） | **87 passed**（1.90s） | EXP-20260601-012 |
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
python -m pytest -v   # 预期 98 passed

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --experiment-name server_walk_forward_001
```

产物：`metrics.json`（含 train/val/test/oos）、`windows.csv`、`oos_equity_curve.csv`、`oos_trades.csv`、`summary.md`。

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
