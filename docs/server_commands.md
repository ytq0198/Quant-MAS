# Quant MAS 服务器操作指令

GitHub 仓库：[https://github.com/ytq0198/Quant-MAS](https://github.com/ytq0198/Quant-MAS)

**推荐服务器路径**：`/mnt/localDisk3/weizian/Quant-MAS`

> **重要**：必须先 `conda activate quant-mas`，再用 `python -m pytest`，不要直接敲 `pytest`（否则会用到系统 Python 3.9）。

## 一、首次部署

```bash
# 1. 创建目录并克隆
mkdir -p /mnt/localDisk3/weizian
cd /mnt/localDisk3/weizian
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS

# 2. 创建数据目录
mkdir -p /mnt/localDisk3/weizian/datasets/{raw,processed,features}
mkdir -p /mnt/localDisk3/weizian/{models,reports,logs}

# 3. 配置服务器路径
cp configs/storage.server.yaml.example configs/storage.server.yaml
# 如需修改路径，编辑 configs/storage.server.yaml

# 4. 安装环境
bash server/setup_server.sh
conda activate quant-mas
pip install -r requirements.txt
pip install -e .

# 5. 验证（必须用 python -m pytest）
python -m pytest -v
# 或
bash server/run_server_tests.sh
```

自检：

```bash
which python      # 应指向 quant-mas 环境
python --version  # 应为 3.11.x
which pytest      # 应在 quant-mas 环境内
```

## 二、日常同步代码

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate quant-mas
pip install -r requirements.txt
pip install -e .
python -m pytest -v
```

## 三、下载真实行情数据

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate quant-mas

python scripts/download_data.py \
  --symbols AAPL MSFT SPY QQQ NVDA \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml
```

## 四、端到端 Pipeline

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate quant-mas

python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml \
  --experiment-name server_ma_cross_001
```

或：`bash server/run_small_pipeline.sh`

## 五、ML 训练

```bash
conda activate quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS

python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.server.yaml \
  --experiment-name server_lgbm_001
```

## 六、ML 回测 / Walk-forward（待实现）

```bash
python scripts/run_ml_backtest.py --config configs/backtest_ml.yaml --storage-config configs/storage.server.yaml
python scripts/run_walk_forward.py --config configs/walk_forward.yaml --storage-config configs/storage.server.yaml
```

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
