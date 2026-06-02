# Quant MAS 问题与解决记录

> 记录各开发阶段遇到的典型问题、根因与解决方法，便于复盘和避免重复踩坑。  
> 与 [`项目指导.md`](项目指导.md) §20 操作手册、`docs/server_commands.md` 配合使用。

**最后更新**：2026-06-02  
**维护方式**：每遇到新问题，在对应 Phase 章节末尾追加一条（含日期、步骤、现象、根因、解法）。

---

## 目录

- [使用说明](#使用说明)
- [问题索引（按编号）](#问题索引按编号)
- [Phase 0：项目初始化与 GitHub 同步](#phase-0项目初始化与-github-同步)
  - [Step 0.1 首次 push 到 GitHub](#step-01-首次-push-到-github)
- [Phase 1：量化核心 MVP](#phase-1量化核心-mvp)
  - [Step 1.1–1.12 本地开发与 pytest（Prompt 1–12）](#step-11112-本地开发与-pytestprompt-112)
  - [Step 1.14 服务器部署与 pytest（Prompt 14）](#step-114-服务器部署与-pytestprompt-14)
  - [Step 1.5 真实数据 pipeline（§20.2，服务器）](#step-15-真实数据-pipeline202-服务器)
- [Phase 2：机器学习实验（进行中）](#phase-2机器学习实验进行中)
  - [Step 2.1 真实数据下载（与 Step 1.5 延续）](#step-21-真实数据下载与-step-15-延续)
- [跨阶段通用规则](#跨阶段通用规则)
- [待验证 / 未完全解决](#待验证--未完全解决)

---

## 使用说明

| 字段 | 含义 |
|------|------|
| **阶段 / 步骤** | 对应 `项目指导.md` §9 Phase 与 §20 分步手册 |
| **现象** | 终端报错或异常行为（原文或摘要） |
| **根因** | 为什么会发生 |
| **解决方法** | 已验证或可操作的修复步骤 |
| **相关提交 / 文件** | 代码或文档改动位置（如有） |

**优先级标记**：P0 = 阻塞开发；P1 = 严重但可绕过；P2 = 环境/体验类。

---

## 问题索引（按编号）

| 编号 | 优先级 | 阶段 / 步骤 | 关键词 |
|------|--------|-------------|--------|
| [M-001](#m-001-git-commit-缺少用户身份) | P1 | Phase 0 / Step 0.1 | git commit 身份 |
| [M-002](#m-002-gitignore-误忽略源码包) | **P0** | Phase 1 / Step 1.14 | ModuleNotFoundError |
| [M-003](#m-003-裸敲-pytest-误用-python-39) | **P0** | Phase 1 / Step 1.14 | pytest、UTC、3.9 |
| [M-004](#m-004-conda-环境为-python-39-非-311) | **P0** | Phase 1 / Step 1.14 | pip、Requires-Python |
| [M-005](#m-005-裸敲-pip-指向用户目录-python-39) | **P0** | Phase 1 / Step 1.14 | python -m pip |
| [M-006](#m-006-yfinance-依赖解析失败) | P1 | Phase 1 / Step 1.14 | requirements、pip 回溯 |
| [M-007](#m-007-yfinance-限流与网络超时) | P1 | Phase 1 Step 1.5 / Phase 2 Step 2.1 | YFRateLimitError |
| [M-008](#m-008-windows-pytest-临时目录权限) | P2 | Phase 1 / 本地 pytest | PermissionError |
| [M-009](#m-009-stooq-需要-api-key) | P1 | Phase 1 Step 1.5 / Phase 2 Step 2.1 | Stooq apikey |

---

## Phase 0：项目初始化与 GitHub 同步

### Step 0.1 首次 push 到 GitHub

#### M-001 Git commit 缺少用户身份

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **现象** | 本地 `git commit` 失败，提示需配置 `user.name` / `user.email` |
| **根因** | Windows 本机未全局配置 Git 用户信息 |
| **解决方法** | 单次提交可内联身份，不修改全局 git config：<br>`git -c user.name="ytq0198" -c user.email="ytq0198@users.noreply.github.com" commit -m "..."` |
| **预防** | 或在系统/用户级一次性配置 Git 身份（按个人习惯） |

---

## Phase 1：量化核心 MVP

### Step 1.1–1.12 本地开发与 pytest（Prompt 1–12）

#### M-008 Windows pytest 临时目录权限

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Phase 1，本地 `python -m pytest -v` |
| **现象** | 测试逻辑通过，但 teardown 阶段报 `PermissionError`（`.pytest_tmp` 相关） |
| **根因** | Windows 本地 pytest 临时目录权限/占用，与业务代码无关 |
| **解决方法** | 1. 测试用例本身无需修改<br>2. 关闭占用该目录的进程后重跑<br>3. 手动删除项目下 `.pytest_tmp` / `.pytest_cache` 后重试<br>4. 以管理员权限或换到 WSL/Linux 跑 pytest |
| **说明** | 服务器 Linux 上 44 passed，无此问题 |

---

### Step 1.14 服务器部署与 pytest（Prompt 14）

> 服务器：`a6000-9961`，路径 `/mnt/localDisk3/weizian/Quant-MAS`，Conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`

#### M-002 `.gitignore` 误忽略源码包

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **现象** | 服务器 `python -m pytest` 收集阶段失败：<br>`ModuleNotFoundError: No module named 'quant_mas.data'`<br>`ModuleNotFoundError: No module named 'quant_mas.models'` |
| **根因** | `.gitignore` 中 `data/`、`models/` 会匹配**任意路径**下同名目录，导致 `src/quant_mas/data/`、`src/quant_mas/models/` 从未被 `git push` |
| **解决方法** | 1. 将规则改为**仅忽略仓库根目录**产物：<br>`/data/`、`/datasets/`、`/outputs/`、`/models/`、`/logs/`、`/reports/`<br>2. 补交缺失源码并 push<br>3. 服务器 `git pull` + `python -m pip install -e .` |
| **相关提交** | `bc5d31c` — Fix gitignore excluding src packages |
| **预防** | 源码包目录不要用与产物同名的裸 glob；可用 `git check-ignore -v src/quant_mas/data/__init__.py` 自检 |

#### M-003 裸敲 `pytest` 误用 Python 3.9

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **现象** | 未激活 conda 或直接敲 `pytest` 时：<br>• Python 3.9（`/opt/anaconda3/bin/python`）<br>• `cannot import name 'UTC' from 'datetime'`<br>• NumPy 1.x / 2.x 与 pandas 冲突 |
| **根因** | 系统默认 Python 3.9 + 用户目录 `~/.local/bin/pytest`，未进入 quant-mas 环境 |
| **解决方法** | ```bash<br>conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas<br>cd /mnt/localDisk3/weizian/Quant-MAS<br>python -m pytest -v   # 不要 bare pytest<br>``` |
| **自检** | `which python` → conda env；`python --version` → 3.11.x |
| **相关文件** | `server/run_server_tests.sh`、`docs/server_commands.md` |

#### M-004 Conda 环境为 Python 3.9 非 3.11

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **现象** | `pip install -e .` 报错：`Python 3.9.13 not in '>=3.11'` |
| **根因** | 初次创建的 `quant-mas` 环境用了 Python 3.9，与 `pyproject.toml` 要求不符 |
| **解决方法** | ```bash<br>conda deactivate<br>rm -rf /mnt/localDisk3/weizian/conda_envs/quant-mas<br>cd /mnt/localDisk3/weizian/Quant-MAS<br>git pull origin main<br>CONDA_ENV_PREFIX=/mnt/localDisk3/weizian/conda_envs/quant-mas bash server/setup_server.sh<br>conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas<br>python --version   # 必须 3.11.x<br>``` |

#### M-005 裸敲 `pip` 指向用户目录 Python 3.9

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **现象** | `python --version` 为 3.11.15，但 `pip --version` 显示：<br>`pip ... from /home/weizian/.local/lib/python3.9/site-packages/pip (python 3.9)` |
| **根因** | `~/.local` 下安装了 Python 3.9 的 pip，PATH 中 `pip` 优先于 conda env |
| **解决方法** | **永远使用** `python -m pip`，不要 bare `pip`：<br>```bash<br>python -m pip install -r requirements.txt<br>python -m pip install -e .<br>python -m pip install -r requirements-data.txt<br>python -m pip install -r requirements-ml.txt<br>``` |
| **相关提交** | setup_server.sh 改为内部调用 `python -m pip` |
| **验收** | `python -m pip --version` 必须显示 `python 3.11` |

#### M-006 yfinance 依赖解析失败

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Step 1.14 安装依赖时 |
| **现象** | `pip install -e ".[data,ml]"` 或含 yfinance 的安装长时间回溯，最终解析失败 |
| **根因** | yfinance 版本与 transitive 依赖（beautifulsoup4 等）在 resolver 下组合爆炸；与 Python 版本无关 |
| **解决方法** | 拆分可选依赖，核心 pytest **不依赖 yfinance**：<br><br>```bash<br># 1. 核心（足够跑 pytest）<br>python -m pip install -r requirements.txt<br>python -m pip install -e .<br>python -m pytest -v<br><br># 2. 需要下载行情时再装<br>python -m pip install -r requirements-data.txt<br><br># 3. 需要 ML 训练时再装<br>python -m pip install -r requirements-ml.txt<br>``` |
| **相关文件** | `requirements.txt`、`requirements-data.txt`（`yfinance==0.2.66`）、`requirements-ml.txt` |
| **验收** | 服务器 **44 passed**（2026-06-02，不装 yfinance 亦可全绿） |

---

### Step 1.5 真实数据 pipeline（§20.2，服务器）

> 目标：yfinance 下载 AAPL / MSFT / SPY → 合并 parquet → `run_pipeline.py --skip-download`

#### M-007 yfinance 限流与网络超时

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02（持续排查中） |
| **阶段** | Phase 1 Step 1.5 / Phase 2 Step 2.1 |
| **现象** | • `YFRateLimitError: Too Many Requests`<br>• `curl: (56) Connection closed abruptly`<br>• 多标的 + 长区间（2018–2025）一次下载更易失败 |
| **根因** | Yahoo Finance 免费 API 对短时间连续请求限流；非 `storage.server.yaml` 配置错误 |
| **解决方法（递进）** | |

**第一层：拉最新代码 + 单标的 + 重试**

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
python -m pip install -e .
python -m pip install -r requirements-data.txt

# 限流后先等 15–30 分钟再试
for sym in AAPL MSFT SPY; do
  python scripts/download_data.py \
    --symbols "$sym" \
    --start 2018-01-01 --end 2025-12-31 \
    --storage-config configs/storage.server.yaml \
    --filename "${sym}.parquet" \
    --retries 8 --retry-backoff 20 --delay 0
  sleep 30   # 仍可能不够，见第二层
done
```

**第二层：Stooq + API Key（推荐，绕过 Yahoo 限流）**

Stooq 已不再允许无 key 下载 CSV，需先申请 API Key：

1. 浏览器打开：https://stooq.com/q/d/?s=aapl.us&get_apikey  
2. 完成 captcha，复制 32 位 `apikey`  
3. 在服务器项目根目录：

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
python -m pip install -e .

cp .env.example .env
# 编辑 .env，设置 STOOQ_API_KEY=你的32位key（不要 commit .env）

# 先验证单条
python scripts/download_data.py \
  --symbols AAPL \
  --start 2018-01-01 --end 2019-01-01 \
  --source stooq \
  --storage-config configs/storage.server.yaml \
  --filename AAPL_2018.parquet

# 全量按年下载 + 合并
SOURCE=stooq SYMBOLS="AAPL" bash server/download_data_resilient.sh
SOURCE=stooq SYMBOLS="AAPL MSFT SPY" bash server/download_data_resilient.sh
```

**第三层：resilient 脚本（Yahoo，需冷却）**

仅当 Yahoo IP 冷却后可试：

```bash
INITIAL_COOLDOWN_SECONDS=1800 SOURCE=yfinance SYMBOLS="AAPL" bash server/download_data_resilient.sh
```

**第四层：仍失败时**

| 手段 | 操作 |
|------|------|
| **改用 Stooq + API Key** | 见 [M-009](#m-009-stooq-需要-api-key) |
| 单条测试 Stooq | `python scripts/download_data.py ... --source stooq`（需 `STOOQ_API_KEY`） |
| 加长间隔 | `SLEEP_SECONDS=120` |
| Yahoo 冷却 | 被限流后 **等待 30–60 分钟**，不要立刻重试；可用 `INITIAL_COOLDOWN_SECONDS=1800` |
| 分 symbol 分三次跑 | 每次只设一个 `SYMBOLS="AAPL"` |
| 备用数据源 | 手动 CSV 放到 `datasets/raw/manual/`（见 `docs/server_commands.md` 方式 C） |
| 代理 | 必要时配置 `http_proxy` / `https_proxy` |

**下载完成后跑 pipeline**

```bash
python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 --end 2025-12-31 \
  --storage-config configs/storage.server.yaml \
  --skip-download \
  --experiment-name server_ma_cross_real_001
```

| **相关提交** | 逐标的重试：`c9b005c` 附近；resilient 脚本：`74ca5fd` |
| **相关文件** | `src/quant_mas/data/fetchers.py`、`scripts/download_data.py`、`server/download_data_resilient.sh`、`scripts/merge_parquet.py` |
| **状态** | 使用 Stooq + API Key 下载（见 M-009）；Yahoo 仍限流 |

#### M-009 Stooq 需要 API Key

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Phase 1 Step 1.5 / Phase 2 Step 2.1 |
| **现象** | Stooq URL 返回约 370 字节文字「Get your apikey: …」，非 CSV；`pd.read_csv` 报 `ParserError` |
| **根因** | Stooq 政策变更：CSV 下载 URL 必须带 `apikey=XXXXXXXX` 参数 |
| **解决方法** | 1. 浏览器打开 https://stooq.com/q/d/?s=aapl.us&get_apikey ，完成 captcha<br>2. 复制 apikey 到服务器 `.env`：`STOOQ_API_KEY=...`<br>3. `git pull` 后 `SOURCE=stooq bash server/download_data_resilient.sh` |
| **相关文件** | `src/quant_mas/data/fetchers.py`（`StooqFetcher`）、`.env.example`、`server/download_data_resilient.sh` |
| **注意** | **不要** commit `.env`；apikey 仅放服务器本地 |

---

## Phase 2：机器学习实验（进行中）

### Step 2.1 真实数据下载（与 Step 1.5 延续）

Step 2.1 与 Phase 1 Step 1.5 为同一服务器操作链（下载 → pipeline）。  
当前阻塞点仍为 **[M-007](#m-007-yfinance-限流与网络超时)**；数据下载成功前，Step 2.2（Prompt 15 ML 训练）不应开始。

| 步骤 | Prompt | 潜在问题 | 说明 |
|------|--------|----------|------|
| 2.2 ML 训练输出 | 15 | LightGBM 未安装 | 先 `python -m pip install -r requirements-ml.txt` |
| 2.2 ML 训练输出 | 15 | 无特征 parquet | 必须先完成 Step 2.1 pipeline 或手动 build_features |
| 2.3 ML 回测 | 16 | 模型路径不对 | 检查 `storage.server.yaml` 中 `models_dir` |

*本节随 Phase 2 推进持续追加。*

---

## 跨阶段通用规则

以下规则来自多次踩坑后的**固定习惯**，适用于所有阶段：

| 规则 | 错误做法 | 正确做法 |
|------|----------|----------|
| 运行测试 | `pytest` | `python -m pytest -v` |
| 安装包 | `pip install ...` | `python -m pip install ...` |
| 激活环境 | 直接 SSH 跑命令 | 先 `conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas` |
| 同步代码 | 只改本地不 push | 本地 pytest → git push → 服务器 git pull |
| 安装顺序 | 一次装全部含 yfinance | 先 `requirements.txt` + `-e .`，再按需 `requirements-data.txt` / `requirements-ml.txt` |
| 下载行情 | 三标的 + 8 年一次请求 | `download_data_resilient.sh`，单 symbol、按年、长 sleep |
| 源码 vs 产物 | `.gitignore` 写 `data/` | 写 `/data/`、`/models/` 等根目录规则 |
| 实验记录 | 口头说「跑过了」 | 写入 `docs/experiment_log.md`（含 metrics 路径） |

**环境自检清单（服务器每次会话建议执行一次）：**

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
which python && python --version          # 3.11.x
python -m pip --version                   # python 3.11
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
python -m pip install -e .
```

---

## 待验证 / 未完全解决

| 编号 | 阶段 | 问题 | 当前状态 |
|------|------|------|----------|
| M-007 | Step 1.5 / 2.1 | yfinance 真实数据全量下载 | 已提供 resilient 脚本；**待服务器跑通并记入 experiment_log** |
| — | Step 2.2 | LightGBM 真实训练 | 未开始 |
| — | Step 2.3–2.4 | ML 回测 / Walk-forward | 未开始 |

---

## 追加记录模板

复制以下模板追加到对应 Phase 章节：

```markdown
#### M-0XX 简短标题

| 项 | 内容 |
|----|------|
| **日期** | YYYY-MM-DD |
| **阶段** | Phase X / Step X.X（Prompt N） |
| **现象** | … |
| **根因** | … |
| **解决方法** | … |
| **相关提交 / 文件** | … |
```
