# Quant MAS 问题与解决记录

> 记录各开发阶段遇到的典型问题、根因与解决方法，便于复盘和避免重复踩坑。  
> 与 [`项目指导.md`](项目指导.md) §20 操作手册、`docs/server_commands.md` 配合使用。

**最后更新**：2026-06-03（Plus M4 EXP-20260602-016）  
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
  - [Step 1.5 真实数据 pipeline（§20.2，✅ 已完成）](#step-15-真实数据-pipeline202-已完成-2026-06-01)
- [Phase 2：机器学习实验（进行中）](#phase-2机器学习实验进行中)
  - [Step 2.2b GPU 训练 ✅](#step-22b-gpu-训练--已完成2026-06-02)
- [Plus M2：多数据源扩展（EXP-DATA-001）](#plus-m2多数据源扩展exp-data-001)
- [Plus M4：LangGraph 编排（EXP-20260602-016）](#plus-m4langgraph-编排exp-20260602-016)
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
| [M-010](#m-010-lightgbm-pypi-wheel-为-cpu-only) | **P0** | Phase 2 / Step 2.2b | LightGBM CUDA build |
| [M-011](#m-011-alpha-vantage-历史区间返回-0-行) | P1 | Plus M2 / EXP-DATA-001 | Alpha Vantage compact |
| [M-012](#m-012-alpha-vantage-outputsizefull-免费-tier-失败) | P1 | Plus M2 / EXP-DATA-001 | outputsize=full |
| [M-013](#m-013-finnhub-免费-tier-无-candle-权限) | P1 | Plus M2 / EXP-DATA-001 | Finnhub 403 |
| [M-014](#m-014-把-api-key-写入-envexample-或-commit) | **P0** | Plus M2 / 安全 | .env vs .env.example |
| [M-015](#m-015-sec-edgar-需真实-user-agent) | P1 | Plus M2 / EXP-DATA-001 | SEC User-Agent |
| [M-016](#m-016-langgraph-建边-zipstrict-长度不匹配) | **P0** | Plus M4 / langgraph backend | zip() strict |
| [M-017](#m-017-服务器-env-导致-pytest-llm-用例失败) | P1 | Plus M5 / 服务器 pytest | load_repo_dotenv |

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

### Step 1.5 真实数据 pipeline（§20.2，✅ 已完成 2026-06-01）

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

Stooq 已不再允许无 key 下载 CSV。Key 的获取方式在 2026 年又变过一次——**不会直接显示 32 位 key**，详见 [M-009](#m-009-stooq-需要-api-key) 完整流程。

简要步骤：

1. 浏览器打开：https://stooq.com/q/d/?s=aapl.us&get_apikey  
2. 按 M-009 流程完成 Authorization → Refresh → 从底部 **CSV Download Link** 提取 `apikey=`  
3. 写入服务器 `.env`：`STOOQ_API_KEY=...`  
4. `SOURCE=stooq bash server/download_data_resilient.sh`

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
| **状态** | ✅ 2026-06-01 服务器验证：Stooq 6033 rows + `server_ma_cross_real_001` pipeline 成功 |

#### M-009 Stooq 需要 API Key

> **2026 年规则更新**：Key **不会直接显示**；需 Authorization → Refresh → 从 CSV Download Link 提取 `apikey=`。

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02（流程更新） |
| **阶段** | Phase 1 Step 1.5 / Phase 2 Step 2.1 |
| **现象 A** | 无 key 请求 Stooq 时，返回约 370 字节文字「Get your apikey: …」，非 CSV；`pd.read_csv` 报 `ParserError` |
| **现象 B** | 打开 get_apikey 页面后**根本没有出现验证码**，无法进入授权流程 |
| **根因** | Stooq 政策多次变更：① CSV 下载 URL 必须带 `apikey=XXXXXXXX`；② **2026 年起 key 不再直接展示**，需从授权后的 CSV 下载链接中提取 |

##### 2026 年正确获取 API Key 流程（已验证用户路径）

> **注意**：不是「打开页面 → captcha → 直接复制 Key」。当前成功用户的实际流程如下：

```
打开 get_apikey 页面
    ↓
出现验证码（Captcha）
    ↓
点击 Approve
    ↓
页面显示 Authorization successful
    ↓
Refresh page（刷新页面）
    ↓
页面底部出现 CSV Download Link
    ↓
从链接 URL 中提取 apikey= 后面的 32 位字符串
```

**get_apikey 页面地址：**

https://stooq.com/q/d/?s=aapl.us&get_apikey

**从 CSV Download Link 提取 key 示例：**

链接形如：

```text
https://stooq.com/q/d/l/?s=aapl.us&d1=20180101&d2=20181231&i=d&apikey=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

其中 `apikey=` 后面即为 32 位 key（复制到 `.env`，不要 commit）。

**写入服务器：**

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
cp .env.example .env
nano .env   # STOOQ_API_KEY=上面提取的32位key
```

**验证下载：**

```bash
python scripts/download_data.py \
  --symbols AAPL \
  --start 2018-01-01 --end 2019-01-01 \
  --source stooq \
  --storage-config configs/storage.server.yaml \
  --filename AAPL_2018.parquet
```

##### 卡点：页面不出现验证码

若打开 get_apikey 后**连验证码都没有**，则卡在流程第一步，常见原因与尝试：

| 可能原因 | 建议操作 |
|----------|----------|
| 浏览器/网络环境被 Stooq 限制 | 换浏览器（Chrome / Firefox）、开无痕模式、换网络（手机热点 / VPN） |
| 页面未完全加载或缓存异常 | 硬刷新（Ctrl+F5）、清 cookie 后重开 |
| 服务器 IP 与浏览器环境不同 | **必须在有图形界面的浏览器中操作**；SSH 服务器无法完成 captcha |
| Stooq 区域性/时段限制 | 隔几小时再试，或换时间段访问 |
| 已授权但未刷新 | 若曾成功授权，直接 **Refresh** 看底部是否已有 CSV Download Link |

若长期无法出现验证码，可暂用 [M-007 第四层](#第四层仍失败时) 的 **手动 CSV** 或等 Yahoo 冷却后再试 yfinance。

| **相关提交** | `867ac14` — StooqFetcher + `STOOQ_API_KEY` |
| **相关文件** | `src/quant_mas/data/fetchers.py`、`.env.example`、`server/download_data_resilient.sh` |
| **注意** | **不要** commit `.env`；apikey 仅放服务器/本机本地 |
| **验证记录** | EXP-20260601-004：AAPL+MSFT+SPY 2018–2025，pipeline ma_cross 通过 |

---

## Phase 2：机器学习实验（进行中）

### Step 2.1 真实数据下载 ✅ 已完成（2026-06-01）

服务器已用 **Stooq + `.env`** 完成 AAPL / MSFT / SPY 下载与 `run_pipeline.py --skip-download`。  
实验记录：**EXP-20260601-004**（`docs/experiment_log.md`）。

| 步骤 | Prompt | 潜在问题 | 说明 |
|------|--------|----------|------|
| 2.2 ML 训练输出 | **15** | LightGBM 未安装 | 先 `python -m pip install -r requirements-ml.txt` |
| 2.2b GPU 训练 | **15b** | CUDA Tree Learner not enabled | 见 [M-010](#m-010-lightgbm-pypi-wheel-为-cpu-only)，编译 CUDA 版 LightGBM |
| 2.4 Walk-forward | 17 | 窗口无数据 / 路径 | 检查 features.parquet 与 `walk_forward.yaml` |

### Step 2.2b GPU 训练 ✅ 已完成（2026-06-02）

服务器 **4× RTX A6000** 上 `--device cuda` 训练与 ML 回测均已通过。  
实验记录：**EXP-20260602-004**（GPU 训练）、**EXP-20260602-005**（ML 回测）。

#### M-010 LightGBM PyPI wheel 为 CPU-only

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Phase 2 / Step 2.2b（Prompt 15b） |
| **现象** | `train_model.py --device cuda` 在 `fit()` 时报错：`[LightGBM] [Fatal] CUDA Tree Learner was not enabled in this build.`；metadata 中 `device_resolved=cuda`、`device_fallback=false` |
| **根因** | 1) `pip install lightgbm` 默认 wheel 常为 CPU-only；2) `resolve_training_device()` 仅检测 `nvidia-smi`，**未**检测 LightGBM 是否带 CUDA 编译 |
| **解决方法** | 服务器上从源码编译 CUDA 版（约 5 分钟）：<br>`python -m pip uninstall -y lightgbm`<br>`python -m pip install --no-binary lightgbm --config-settings=cmake.define.USE_CUDA=ON 'lightgbm==4.6.0'`<br>冒烟：`python -c "from lightgbm import LGBMClassifier; LGBMClassifier(device='cuda').fit([[0],[1]], [0,1])"` |
| **相关文件** | `docs/server_commands.md` §五、`requirements-ml.txt`、`src/quant_mas/utils/device.py` |
| **验证记录** | EXP-20260602-004：`server_lgbm_gpu_001`，device=cuda，test AUC 0.479 |
| **后续改进** | 可在 `device.py` 增加 LightGBM CUDA 编译检测，避免 `fit()` 才 Fatal |

*本节随 Phase 2 推进持续追加。*

---

## Plus M2：多数据源扩展（EXP-DATA-001）

> 阶段：Plus v2 **M2**（`tests/test_data_sources.py` mock 测试 + 服务器 API smoke）  
> 实验：**EXP-20260602-011/012**、**EXP-DATA-001**（2026-06-02）  
> 文档：[`docs/data_sources.md`](docs/data_sources.md)、[`docs/server_commands.md`](docs/server_commands.md) §六点五

### Step M2.1 服务器 API smoke

#### M-011 Alpha Vantage 历史区间返回 0 行

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Plus M2 / EXP-DATA-001 |
| **现象** | `python scripts/download_data.py --source alpha_vantage --symbols AAPL --start 2024-01-01 --end 2024-06-01` 报错：<br>`[download] ERROR: Alpha Vantage returned no rows for AAPL` |
| **根因** | Alpha Vantage **免费 tier** 的 `compact` 模式只返回**最近约 100 个交易日**；服务器日期为 2026 年时，返回窗口约为 2025 年底～2026 年，**过滤 2024 区间后行数为 0**。不是 API key 失效，也不是代码未拉取到数据 |
| **解决方法** | 1. **历史 OHLCV** → 用 **Stooq**（见 [M-009](#m-009-stooq-需要-api-key)）<br>2. **Alpha Vantage smoke** → 用**近期 3 个月**，例如：<br>```bash<br>python scripts/download_data.py --source alpha_vantage \<br>  --symbols AAPL --start 2026-01-01 --end 2026-06-01 \<br>  --storage-config configs/storage.server.yaml<br>```<br>3. fetcher 已支持 `outputsize=auto` 并在空结果时提示可用日期范围（commit `7514cdc`） |
| **验证记录** | EXP-20260602-012：AV **100 rows**（2026 H1）；Stooq **105 rows**（2024 H1） |
| **相关文件** | `src/quant_mas/data/fetchers/alpha_vantage_fetcher.py`、`docs/data_sources.md` |

#### M-012 Alpha Vantage `outputsize=full` 免费 tier 失败

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Plus M2 / EXP-DATA-001（首次 smoke） |
| **现象** | 使用 `outputsize=full` 时 API 无完整历史或报错；改用 `compact` + `IBM` 可拿到约 100 日 |
| **根因** | 免费 tier 对 `full` 历史数据支持有限/不稳定；`compact` 才是免费 tier 默认可用模式 |
| **解决方法** | 1. fetcher 默认 **`outputsize=auto`**：先尝试 `full`，失败再 `compact`<br>2. 不要指望 AV 免费 tier 替代 Stooq 做 2018–2025 长历史<br>3. 限速约 **5 次/分钟**，多 symbol 时加 `--delay 12` 或更高 |
| **相关提交** | `70007ce`、`7514cdc` |

#### M-013 Finnhub 免费 tier 无 candle 权限

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Plus M2 / EXP-DATA-001 |
| **现象** | HTTP **403**，响应：<br>`{"error":"You don't have access to this resource."}` |
| **根因** | Finnhub **免费账户无权调用** `/stock/candle` OHLCV 接口；需付费计划。**不是代码 bug** |
| **解决方法** | 1. OHLCV 继续用 **Stooq**（历史）+ **Alpha Vantage**（近期 smoke）<br>2. `configs/data_sources.yaml` 中 finnhub 标 `blocked_free_tier`<br>3. 若未来升级 Finnhub 付费，再复测 `--source finnhub` |
| **验证记录** | EXP-DATA-001：Finnhub ❌（预期）；FRED + Stooq + AV ✅ |

#### M-014 把 API Key 写入 `.env.example` 或 commit

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Plus M2 配置 |
| **现象** | 真实 `ALPHAVANTAGE_API_KEY`、`FRED_API_KEY` 等被粘贴进 `.env.example` 或聊天/文档，存在泄露风险 |
| **根因** | `.env.example` 会 **commit 到 GitHub**；只有 `.env` 在 `.gitignore` 中 |
| **解决方法** | 1. **真实 key 只放** 项目根 `.env`（本地 / 服务器各一份）<br>2. `.env.example` **只保留空占位符**，例如 `ALPHAVANTAGE_API_KEY=`<br>3. 若 key 已暴露 → 到各平台**轮换 key**<br>4. `git status` 确认 `.env` 未被 staged |
| **预防** | `download_data.py` 通过 `load_repo_dotenv()` 读 `.env`；文档与 smoke 命令中不写真实 key |
| **相关文件** | `.env.example`、`.gitignore`、`docs/server_commands.md` §六点五 |

#### M-015 SEC EDGAR 需真实 User-Agent

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-02 |
| **阶段** | Plus M2 / EXP-DATA-001（未测） |
| **现象** | 使用占位符 `SEC_EDGAR_USER_AGENT=YourName your@email.com` 时，SEC 可能拒绝或限流 |
| **根因** | SEC **强制要求**可识别的 User-Agent（真实姓名 + 联系邮箱），用于合规与联系 |
| **解决方法** | 在服务器 `.env` 写入真实信息，例如：<br>`SEC_EDGAR_USER_AGENT=Zian Wei zian@example.edu`<br>然后：<br>```bash<br>python scripts/download_data.py --source sec_edgar --cik 0000320193 \<br>  --storage-config configs/storage.server.yaml<br>``` |
| **状态** | EXP-DATA-001 中 **SEC 未测**；FRED / Stooq / AV 已通过 |

---

## Plus M4：LangGraph 编排（EXP-20260602-016）

> 阶段：Plus v2 **M4**（`src/quant_mas/orchestration/langgraph_workflow.py`）  
> 实验：**EXP-20260602-015**（本地）、**EXP-20260602-016**（服务器 langgraph backend）  
> 文档：[`docs/langgraph_workflow.md`](docs/langgraph_workflow.md)

### Step M4.1 服务器 `--backend langgraph`

#### M-016 LangGraph 建边 `zip(..., strict=True)` 长度不匹配

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-03 |
| **阶段** | Plus M4 / 服务器 smoke（`pip install -e ".[orchestration]"` 后） |
| **现象** | `python scripts/run_langgraph_workflow.py --dry-run --backend langgraph` 报错：<br>`[workflow] ERROR: zip() argument 2 is shorter than argument 1`<br>sequential backend 正常；pytest 中 langgraph 用例在无 langgraph 时被 skip |
| **根因** | `langgraph_workflow.py` 建边时使用 `zip(NODE_ORDER, NODE_ORDER[1:], strict=True)`。`NODE_ORDER` 有 **6** 个节点，而 `NODE_ORDER[1:]` 只有 **5** 个；`strict=True` 要求两 iterable **等长**，配对相邻边应使用 `NODE_ORDER[:-1]` 与 `NODE_ORDER[1:]` |
| **解决方法** | 1. 拉取修复 commit **`c0fa5e3`** 及以上<br>2. 建边改为 `zip(NODE_ORDER[:-1], NODE_ORDER[1:], strict=True)`（或 `_node_edges()` 辅助函数）<br>3. 复测：<br>```bash<br>python -m pytest tests/test_langgraph_workflow.py::test_langgraph_build_and_dry_run_when_available -v<br>python scripts/run_langgraph_workflow.py --dry-run --backend langgraph<br>``` |
| **相关提交** | `c0fa5e3` — Fix LangGraph backend zip strict mismatch on node edges |
| **相关文件** | `src/quant_mas/orchestration/langgraph_workflow.py`、`tests/test_langgraph_workflow.py` |
| **验证记录** | EXP-20260602-016：a6000-9961 @ `c0fa5e3`，langgraph invoke 测试通过；dry-run 6 节点、`errors: []` |
| **预防** | 用 `strict=True` 配对「相邻元素」时，左边取 `seq[:-1]`、右边取 `seq[1:]`，不要对全长 `seq` 与 `seq[1:]` 做 strict zip |

#### M-017 服务器 `.env` 导致 pytest LLM 用例失败

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-03 |
| **阶段** | Plus M5 / 服务器（已配置 DeepSeek `.env`） |
| **现象** | 配置 `LLM_API_KEY` 后 `python -m pytest -v` 失败：<br>`test_resolve_llm_client_defaults_to_mock` 期望无 key 时回退 Mock，实际得到 `OpenAICompatibleLLMClient` |
| **根因** | `resolve_llm_client()` 内调用 `load_repo_dotenv()`，会从项目根 `.env` **重新写入** `LLM_API_KEY`；测试里 `monkeypatch.delenv("LLM_API_KEY")` 之后仍被 `.env` 覆盖 |
| **解决方法** | 1. 拉取修复：`tests/test_context_engineering.py` 对该用例 `monkeypatch` 禁用 `load_repo_dotenv`<br>2. **CLI smoke** 与 **pytest** 分离：有 `.env` 时 CLI 可走 DeepSeek；pytest 仍 mock 隔离<br>3. 配置 `.env` 后若 `--use-llm` 仍显示 `"llm_provider": "mock"` → 检查 `.env` 是否在仓库根、变量名是否为 `LLM_API_KEY` |
| **相关提交** | （test 修复 commit 待 push） |
| **DeepSeek smoke 正确命令** | 见 [context_engineering.md](docs/context_engineering.md) 服务器节 |

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
| 下载行情 | 三标的 + 8 年一次请求 | Stooq + `download_data_resilient.sh`，或 `--source stooq` |
| Stooq key | 单独跑 download 忘记 export | 项目根 `.env` 含 `STOOQ_API_KEY`；`download_data.py` 启动时自动加载 |
| M2 API key | 把 key 写进 `.env.example` 或 commit | 真实 key **仅** `.env`；example 只留占位符（见 [M-014](#m-014-把-api-key-写入-envexample-或-commit)） |
| M2 OHLCV 历史 | Alpha Vantage + 2024 区间 | **Stooq** 做历史；AV 仅近期 ~100 日 smoke（见 [M-011](#m-011-alpha-vantage-历史区间返回-0-行)） |
| M2 Finnhub | 以为 403 是代码 bug | 免费 tier 无 candle；标 blocked，换 Stooq/AV（见 [M-013](#m-013-finnhub-免费-tier-无-candle-权限)） |
| M4 LangGraph 建边 | `zip(NODE_ORDER, NODE_ORDER[1:], strict=True)` | 用 `NODE_ORDER[:-1]` 与 `NODE_ORDER[1:]`（见 [M-016](#m-016-langgraph-建边-zipstrict-长度不匹配)） |
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
| M-007 | Step 2.1 | yfinance 真实数据全量下载 | Yahoo 限流；已改用 Stooq 完成（EXP-20260601-004） |
| M-009 | Step 2.1 | Stooq API Key | ✅ 已解决，流程见 M-009 |
| — | Step 2.2 | LightGBM 真实训练 | ✅ EXP-20260601-006 |
| — | Step 2.2b | GPU/CUDA 训练 | ✅ EXP-20260602-004（见 M-010） |
| 2.4 Walk-forward | 17 | 见 M-010 若用 GPU | ✅ EXP-20260602-008 |
| — | Plus M2 | 多数据源 API smoke | ✅ EXP-DATA-001（Finnhub 免费 blocked；SEC 待测，见 M-015） |
| — | Plus M3 | Memory/RAG v2 SQLite | ✅ EXP-20260602-013/014 |
| — | Plus M4 | LangGraph workflow | ✅ EXP-20260602-015/016（含 langgraph backend 修复 M-016） |
| — | Plus M5 | 上下文/LLM | ✅ EXP-017/018 本地+服务器；DeepSeek EXP-LLM-001（M-017 已修复） |

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
