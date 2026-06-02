# Quant MAS 服务器操作指令

GitHub 仓库：[https://github.com/ytq0198/Quant-MAS](https://github.com/ytq0198/Quant-MAS)

## 一、首次部署（Prompt 14）

```bash
# 1. 创建目录并克隆
mkdir -p ~/quant-mas
cd ~/quant-mas
git clone https://github.com/ytq0198/Quant-MAS.git repo
cd repo

# 2. 创建数据目录
mkdir -p ~/quant-mas/datasets/{raw,processed,features}
mkdir -p ~/quant-mas/{models,reports,logs}

# 3. 配置服务器路径（把 <USER> 换成你的用户名）
cp configs/storage.server.yaml.example configs/storage.server.yaml
# 编辑 configs/storage.server.yaml

# 4. 安装环境
bash server/setup_server.sh
conda activate quant-mas

# 5. 验证
bash server/run_server_tests.sh
```

## 二、日常同步代码

```bash
cd ~/quant-mas/repo
git pull origin main
conda activate quant-mas
pip install -r requirements.txt
pip install -e .
pytest
```

## 三、下载真实行情数据

```bash
cd ~/quant-mas/repo
conda activate quant-mas

python scripts/download_data.py \
  --symbols AAPL MSFT SPY QQQ NVDA \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml
```

数据保存到 `~/quant-mas/datasets/raw/market_data.parquet`（由 storage 配置决定）。

## 四、端到端 Pipeline（Prompt 11，真实数据）

```bash
cd ~/quant-mas/repo
conda activate quant-mas

python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml \
  --experiment-name server_ma_cross_001
```

或使用快捷脚本：

```bash
bash server/run_small_pipeline.sh
```

## 五、分步运行（调试用）

```bash
conda activate quant-mas
cd ~/quant-mas/repo
STORAGE=configs/storage.server.yaml

# 特征
python scripts/build_features.py \
  --storage-config $STORAGE

# 回测
python scripts/run_backtest.py \
  --config configs/backtest.yaml \
  --storage-config $STORAGE

# 报告
python scripts/generate_report.py --latest \
  --storage-config $STORAGE
```

## 六、ML 训练（Prompt 15）

```bash
conda activate quant-mas
cd ~/quant-mas/repo

python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.server.yaml \
  --experiment-name server_lgbm_001
```

产物：`~/quant-mas/models/` 下的 metrics.json、feature_importance.csv、model 文件。

## 七、ML 信号回测（Prompt 16，待实现）

```bash
python scripts/run_ml_backtest.py \
  --config configs/backtest_ml.yaml \
  --storage-config configs/storage.server.yaml
```

## 八、Walk-forward 样本外评估（Prompt 17，待实现）

```bash
python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml
```

## 九、查看实验结果

```bash
# 报告目录
ls ~/quant-mas/reports/

# 实验记忆
cat ~/quant-mas/reports/experiments.json

# 训练日志
tail -f ~/quant-mas/logs/server_pytest.log
```

## 十、本地 ↔ 服务器工作流

| 操作 | 本地 Windows | 服务器 Linux |
|------|-------------|--------------|
| 写代码 | Codex | — |
| 单元测试 | `pytest` | `bash server/run_server_tests.sh` |
| 推送代码 | `git push` | — |
| 拉取代码 | — | `git pull` |
| 真实训练/回测 | 小数据可选 | **推荐** |

本地推送：

```powershell
cd "D:\scientific reasearch and work\SRTP\Quant MAS"
git add .
git commit -m "your message"
git push origin main
```
