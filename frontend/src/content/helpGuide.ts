import type { Locale } from "../i18n/translations";
import type { PageId } from "../types/navigation";

export interface HelpSection {
  id: string;
  title: string;
  intro?: string;
  steps?: string[];
  bullets?: string[];
  notes?: string[];
  commands?: string[];
  table?: { headers: string[]; rows: string[][] };
  pageId?: PageId;
}

export interface HelpGuide {
  lead: string;
  updated: string;
  tocTitle: string;
  goToPage: string;
  stepsLabel: string;
  notesLabel: string;
  commandsLabel: string;
  sections: HelpSection[];
}

const en: HelpGuide = {
  lead: "Research-only enterprise console for experiments, backtests, OOS, audit, and paper artifacts. Not a live-trading system.",
  updated: "Last updated: 2026-06 · v5 Enterprise Research Console",
  tocTitle: "Contents",
  goToPage: "Open page",
  stepsLabel: "Steps",
  notesLabel: "Notes",
  commandsLabel: "Commands (server or local shell)",
  sections: [
    {
      id: "principles",
      title: "Platform principles",
      intro: "Read these before running any job.",
      bullets: [
        "Live trading is disabled — the platform cannot place real orders.",
        "LLM agents do not place live orders; they orchestrate research tools only.",
        "Backtest metrics (simulation.*) are research-only and not paper-grade.",
        "Paper-grade conclusions require audited walk-forward OOS metrics (oos.*) only.",
        "Candidate strategies require human review before any promotion."
      ]
    },
    {
      id: "architecture",
      title: "Architecture & connection",
      intro: "Typical setup: frontend on local Windows, backend on remote GPU server via SSH tunnel.",
      bullets: [
        "Browser → http://localhost:5173 (Vite dev server)",
        "Vite proxies /api → http://127.0.0.1:8000 on your PC",
        "SSH tunnel forwards local 8000 → server 127.0.0.1:8000",
        "Backend runs Quant Engine and reads artifacts under outputs/"
      ],
      commands: [
        "# Local SSH tunnel (PowerShell, keep open)",
        "ssh -p 9961 -L 8000:127.0.0.1:8000 weizian@10.98.36.128",
        "",
        "# Local frontend",
        "cd frontend && npm run dev",
        "",
        "# Server backend",
        "cd /mnt/localDisk3/weizian/Quant-MAS",
        "export QUANT_MAS_ARTIFACT_ROOT=/mnt/localDisk3/weizian/Quant-MAS",
        "export QUANT_MAS_AUTH_MODE=open",
        "PYTHONPATH=src python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000"
      ],
      notes: [
        "Header badge Server connected = API reachable. Local fallback = fixture data only.",
        "After tunnel or backend changes, click Refresh in the header."
      ]
    },
    {
      id: "layout",
      title: "Layout & navigation",
      intro: "Three-column workbench: sidebar, main content, context panel.",
      bullets: [
        "Sidebar — switch pages; collapse with « at the bottom.",
        "Header — connection status, auth mode, role, Refresh.",
        "Main area — current page tools and data.",
        "Context panel (right) — safety boundary, baseline, metric reminders.",
        "Settings and Help pages use full width (no context panel).",
        "Language toggle — header, page toolbar, or sidebar footer (中文 ↔ English)."
      ],
      pageId: "overview"
    },
    {
      id: "overview",
      title: "Overview",
      intro: "Dashboard entry point with KPIs, workflow, and module shortcuts.",
      steps: [
        "Check header badges: prefer Server connected and Live trading disabled.",
        "Review OOS baseline KPIs and test pass count.",
        "Use the workflow stepper to understand the research pipeline.",
        "Click shortcut cards to jump to Experiments, Backtests, OOS, etc.",
        "Click Refresh after any completed job to reload summaries."
      ],
      pageId: "overview"
    },
    {
      id: "experiments",
      title: "Experiments",
      intro: "Experiment registry backed by outputs/reports/experiments.json on the server.",
      steps: [
        "Open Experiments from the sidebar.",
        "Browse the table: experiment_id, metric_family, oos_available, status.",
        "Select a row to inspect metadata in the context panel.",
        "Scroll to Run Backtest Job — enter an experiment name (e.g. ui_ma_backtest_001).",
        "Optionally set Fast window / Slow window (default 5 / 20).",
        "Click Run backtest and watch Job Console until status is completed.",
        "Click Refresh — new experiment should appear in the registry."
      ],
      notes: [
        "If the registry is empty, run at least one successful backtest job or CLI run_backtest.py.",
        "Set QUANT_MAS_EXPERIMENT_MEMORY_PATH on the server to point at experiments.json."
      ],
      pageId: "experiments"
    },
    {
      id: "backtests",
      title: "Backtests",
      intro: "Deterministic backtest summary and job submission. Metrics are non-OOS (research only).",
      steps: [
        "Open Backtests — review the equity chart and metric_family backtest.summary.",
        "Read the disclaimer: not paper-grade OOS.",
        "In Run Backtest Job, set experiment name and optional MA windows.",
        "Submit the job; Job Console shows queued → started → progress → completed/failed.",
        "On completed, Refresh to load artifacts from outputs/reports/backtest_latest/."
      ],
      notes: [
        "Requires data/raw/market_data.parquet on the server.",
        "Job failed with missing parquet → run download_data.py on the server (see Data preparation).",
        "Equity chart shows normalized curve samples from equity_curve.csv."
      ],
      pageId: "backtests"
    },
    {
      id: "oos",
      title: "Walk-forward OOS",
      intro: "Paper-grade out-of-sample metrics (oos.*). Use these for baseline comparison and papers.",
      steps: [
        "Open Walk-forward OOS.",
        "Review current OOS Sharpe and window count if artifacts exist.",
        "Enter experiment name in Run walk-forward OOS.",
        "Submit job and wait for Job Console completion.",
        "Refresh to see updated oos.* metrics."
      ],
      notes: [
        "Requires data/features/features.parquet — run build_features.py after market data download.",
        "Artifacts: outputs/reports/walk_forward_latest/",
        "Do not mix oos.* with simulation.* or training.* in paper conclusions."
      ],
      pageId: "oos"
    },
    {
      id: "risk",
      title: "Risk Review",
      intro: "Human-in-the-loop gate for candidate strategies.",
      steps: [
        "Open Risk Review.",
        "Inspect risk summary and policy badges.",
        "In Review Queue, find items with status pending.",
        "Read each item's context, then click Approve or Reject.",
        "Refresh to update queue state."
      ],
      notes: [
        "In api_key mode, approve/reject requires reviewer role key in Settings.",
        "All candidates should pass backtest → risk → audit → human review."
      ],
      pageId: "risk"
    },
    {
      id: "agents",
      title: "Agents",
      intro: "Multi-agent console — inspect agent cards and run mock orchestration.",
      steps: [
        "Open Agents — view registered agent roles and descriptions.",
        "Use Mock run to test API connectivity (returns explanatory text, not full pipeline).",
        "Review which tools each agent may call under ToolPolicy."
      ],
      notes: [
        "Full agent pipelines are also available via CLI: scripts/run_agent.py.",
        "Agents never place live orders."
      ],
      pageId: "agents"
    },
    {
      id: "tools",
      title: "Controlled Tools",
      intro: "Allowlisted Quant Engine tools exposed to agents and the backend.",
      steps: [
        "Open Tools — list shows tool name, category, and allowed/denied status.",
        "Verify run_backtest, read_report, risk_check, query_memory are allowed.",
        "Denied tools cannot be invoked by agents or jobs."
      ],
      pageId: "tools"
    },
    {
      id: "memory",
      title: "Memory / RAG",
      intro: "Search experiment memory and browse RAG document metadata.",
      steps: [
        "Open Memory / RAG.",
        "Enter a query (e.g. OOS baseline, strategy name) and click Search.",
        "Review hit snippets and scores.",
        "Check RAG documents table for indexed sources."
      ],
      notes: [
        "Results depend on server vector store and experiment memory path.",
        "Empty results — verify QUANT_MAS_EXPERIMENT_MEMORY_PATH and backend connection."
      ],
      pageId: "memory"
    },
    {
      id: "audit",
      title: "Audit Logs",
      intro: "Immutable-style audit trail for research actions.",
      steps: [
        "Open Audit Logs.",
        "Filter by scanning the table: timestamp, actor, action, resource, status.",
        "Use for compliance review alongside Risk Review decisions."
      ],
      notes: [
        "Configure QUANT_MAS_AUDIT_DIR on server to load JSONL audit events.",
        "Reviewer role may be required in api_key mode."
      ],
      pageId: "audit"
    },
    {
      id: "paper",
      title: "Paper Artifacts",
      intro: "Export tables, charts, and markdown for paper writing.",
      steps: [
        "Open Paper Artifacts — browse existing files under outputs/paper/.",
        "Click Export paper artifacts to enqueue a paper_export job.",
        "Wait for Job Console completion, then Refresh.",
        "Download or copy paths listed in the artifacts table."
      ],
      notes: [
        "Requires experiments.json with at least one recorded experiment.",
        "Set QUANT_MAS_PAPER_DIR on the server."
      ],
      pageId: "paper"
    },
    {
      id: "database",
      title: "Database",
      intro: "Status of SQL, vector, and graph backends (metadata only).",
      steps: [
        "Open Database — check backend mode and vector store type.",
        "Review tables list and graph relationships if configured.",
        "Use Deployment section for environment hints."
      ],
      pageId: "database"
    },
    {
      id: "observability",
      title: "Observability",
      intro: "System health, jobs, metrics, logs, and effective config.",
      steps: [
        "Open Observability.",
        "Check System Health and deep health indicators.",
        "Review Jobs list for recent backtest/OOS/export tasks.",
        "Read Metrics summary and Server logs (if QUANT_MAS_LOG_ROOT set).",
        "Inspect Effective Config for auth, storage, and live_trading flags."
      ],
      notes: [
        "If page appears blank, hard-refresh (Ctrl+F5) and ensure latest backend is deployed.",
        "curl http://127.0.0.1:8000/api/config/effective should return env or values object."
      ],
      pageId: "observability"
    },
    {
      id: "settings",
      title: "Settings & API Key",
      intro: "Configure authentication — API Key is only stored here, not on Overview.",
      steps: [
        "Open Settings.",
        "Under API Access, paste your X-Quant-MAS-Key value.",
        "Click Save, then header Refresh.",
        "Verify Auth and Role badges match your key role."
      ],
      table: {
        headers: ["Action", "Minimum role (api_key mode)"],
        rows: [
          ["Browse dashboard", "viewer"],
          ["Submit jobs / export paper", "researcher"],
          ["Approve review / read audit", "reviewer"],
          ["Full admin", "admin"]
        ]
      },
      notes: [
        "open mode — no key required for development.",
        "Keys live in browser localStorage only; never commit them to Git."
      ],
      pageId: "settings"
    },
    {
      id: "jobs",
      title: "Job workflow (general)",
      intro: "All executable research tasks use the same Job Console pattern.",
      steps: [
        "Fill the form on Backtests, Experiments, OOS, or Paper page.",
        "Submit — job gets an id like job-YYYYMMDD-xxxxxx.",
        "Job Console streams events: queued, started, progress, completed/failed.",
        "On failed — read the error message (missing data, import error, 403, etc.).",
        "On completed — click Refresh to pull new artifacts into the UI."
      ],
      bullets: [
        "backtest — moving-average cross, outputs/reports/backtest_latest/",
        "walk_forward_oos — paper-grade OOS, outputs/reports/walk_forward_latest/",
        "paper_export — CSV/MD/JSON under outputs/paper/"
      ]
    },
    {
      id: "data-prep",
      title: "Data preparation (first run)",
      intro: "Run on the server before submitting UI jobs.",
      commands: [
        "cd /mnt/localDisk3/weizian/Quant-MAS",
        "mkdir -p data/raw",
        "",
        "# Download OHLCV (symbols required)",
        "PYTHONPATH=src python scripts/download_data.py \\",
        "  --symbols AAPL MSFT SPY --start 2018-01-01 --end 2025-12-31 --source auto",
        "",
        "# Features for OOS",
        "PYTHONPATH=src python scripts/build_features.py",
        "",
        "ls -lh data/raw/market_data.parquet",
        "ls -lh data/features/features.parquet"
      ],
      notes: [
        "If Yahoo rate-limits, use --source stooq with STOOQ_API_KEY in .env.",
        "Or symlink existing data: ln -sf /path/to/market_data.parquet data/raw/"
      ]
    },
    {
      id: "troubleshooting",
      title: "Troubleshooting",
      table: {
        headers: ["Symptom", "What to do"],
        rows: [
          ["Local fallback in header", "Start SSH tunnel and server uvicorn; curl /api/status"],
          ["405 on Run backtest", "git pull latest backend with POST /api/jobs"],
          ["Job failed: parquet missing", "Run download_data.py on server"],
          ["Job failed: features missing", "Run build_features.py"],
          ["POST 403", "Use researcher/reviewer key or QUANT_MAS_AUTH_MODE=open"],
          ["Observability blank", "Update code, restart uvicorn, Ctrl+F5 browser"],
          ["Huge green chart bars", "Update frontend — equity chart normalization fix"]
        ]
      }
    },
    {
      id: "cli",
      title: "CLI alternative",
      intro: "UI and CLI share the same Quant Engine.",
      commands: [
        "python scripts/run_backtest.py --config configs/backtest.yaml",
        "python scripts/run_walk_forward.py --config configs/walk_forward.yaml",
        "python scripts/export_paper_artifacts.py \\",
        "  --memory-path outputs/reports/experiments.json \\",
        "  --output-dir outputs/paper"
      ],
      notes: ["Recommended: run long jobs on server via CLI; use UI to review, audit, and present."]
    }
  ]
};

const zh: HelpGuide = {
  lead: "面向实验、回测、OOS、审计与论文产物的科研专用企业控制台。非实盘交易系统。",
  updated: "最后更新：2026-06 · v5 企业级研究控制台",
  tocTitle: "目录",
  goToPage: "打开页面",
  stepsLabel: "操作步骤",
  notesLabel: "说明",
  commandsLabel: "命令（服务器或本地终端）",
  sections: [
    {
      id: "principles",
      title: "平台原则",
      intro: "运行任何 Job 前请先阅读。",
      bullets: [
        "实盘交易已禁用 — 平台无法下真实订单。",
        "LLM 智能体不下实盘订单，仅编排研究工具。",
        "回测指标（simulation.*）仅供科研参考，非论文级。",
        "论文级结论只能使用经审计的 Walk-forward OOS 指标（oos.*）。",
        "候选策略推进前须人工审查。"
      ]
    },
    {
      id: "architecture",
      title: "架构与连接",
      intro: "典型方式：本地 Windows 跑前端，远程 GPU 服务器跑后端，经 SSH 隧道连接。",
      bullets: [
        "浏览器 → http://localhost:5173（Vite 开发服务器）",
        "Vite 将 /api 代理到本机 http://127.0.0.1:8000",
        "SSH 隧道将本地 8000 转发到服务器 127.0.0.1:8000",
        "后端运行 Quant Engine，读取 outputs/ 下的产物"
      ],
      commands: [
        "# 本地 SSH 隧道（PowerShell，保持连接）",
        "ssh -p 9961 -L 8000:127.0.0.1:8000 weizian@10.98.36.128",
        "",
        "# 本地前端",
        "cd frontend && npm run dev",
        "",
        "# 服务器后端",
        "cd /mnt/localDisk3/weizian/Quant-MAS",
        "export QUANT_MAS_ARTIFACT_ROOT=/mnt/localDisk3/weizian/Quant-MAS",
        "export QUANT_MAS_AUTH_MODE=open",
        "PYTHONPATH=src python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000"
      ],
      notes: [
        "顶栏 Server connected = API 可达；Local fallback = 仅本地夹具数据。",
        "隧道或后端变更后，请点击顶栏 Refresh。"
      ]
    },
    {
      id: "layout",
      title: "布局与导航",
      intro: "三栏研究工作台：侧边栏、主内容区、上下文面板。",
      bullets: [
        "侧边栏 — 切换页面；底部 « 可折叠。",
        "顶栏 — 连接状态、认证模式、角色、Refresh。",
        "主内容区 — 当前页面工具与数据。",
        "右侧 Context Panel — 安全边界、基线、指标提醒。",
        "Settings 与 Help 页全宽显示（无右侧面板）。",
        "语言切换 — 顶栏、页面工具栏或侧边栏底部（中文 ↔ English）。"
      ],
      pageId: "overview"
    },
    {
      id: "overview",
      title: "总览（Overview）",
      intro: "入口仪表盘：KPI、工作流与模块快捷入口。",
      steps: [
        "查看顶栏徽章：优先 Server connected 与 Live trading disabled。",
        "查看 OOS 基线 KPI 与测试通过数。",
        "通过工作流步骤了解研究流水线。",
        "点击快捷卡片跳转到 Experiments、Backtests、OOS 等页面。",
        "Job 完成后点击 Refresh 重新加载摘要。"
      ],
      pageId: "overview"
    },
    {
      id: "experiments",
      title: "实验（Experiments）",
      intro: "实验注册表，数据来自服务器 outputs/reports/experiments.json。",
      steps: [
        "从侧边栏进入 Experiments。",
        "浏览表格：experiment_id、metric_family、oos_available、status。",
        "点击行可在右侧 Context Panel 查看摘要。",
        "滚动到 Run Backtest Job — 填写实验名（如 ui_ma_backtest_001）。",
        "可选调整 Fast window / Slow window（默认 5 / 20）。",
        "点击运行回测，在 Job Console 等待 completed。",
        "点击 Refresh — 注册表应出现新实验。"
      ],
      notes: [
        "注册表为空时，需至少成功运行一次回测 Job 或 CLI run_backtest.py。",
        "服务器设置 QUANT_MAS_EXPERIMENT_MEMORY_PATH 指向 experiments.json。"
      ],
      pageId: "experiments"
    },
    {
      id: "backtests",
      title: "回测（Backtests）",
      intro: "确定性回测摘要与 Job 提交。指标为非 OOS（仅供科研）。",
      steps: [
        "进入 Backtests — 查看权益曲线与 metric_family backtest.summary。",
        "阅读免责声明：非论文级 OOS。",
        "在 Run Backtest Job 中设置实验名与可选 MA 窗口。",
        "提交 Job；Job Console 显示 queued → started → progress → completed/failed。",
        "completed 后 Refresh，从 outputs/reports/backtest_latest/ 加载产物。"
      ],
      notes: [
        "需要服务器上存在 data/raw/market_data.parquet。",
        "Job 报 parquet 缺失 → 在服务器运行 download_data.py（见数据准备）。",
        "权益曲线来自 equity_curve.csv 的归一化采样。"
      ],
      pageId: "backtests"
    },
    {
      id: "oos",
      title: "Walk-forward OOS",
      intro: "论文级样本外指标（oos.*），用于基线对比与论文写作。",
      steps: [
        "进入 Walk-forward OOS。",
        "若有产物，查看当前 OOS Sharpe 与窗口数。",
        "在 Run walk-forward OOS 中填写实验名。",
        "提交 Job 并等待 Job Console 完成。",
        "Refresh 查看更新后的 oos.* 指标。"
      ],
      notes: [
        "需要 data/features/features.parquet — 下载行情后运行 build_features.py。",
        "产物路径：outputs/reports/walk_forward_latest/",
        "论文中勿将 oos.* 与 simulation.* / training.* 混用。"
      ],
      pageId: "oos"
    },
    {
      id: "risk",
      title: "风险审查（Risk Review）",
      intro: "候选策略的人工审查关卡。",
      steps: [
        "进入 Risk Review。",
        "查看风险摘要与策略徽章。",
        "在 Review Queue 中找到 status 为 pending 的项。",
        "阅读上下文后点击 Approve 或 Reject。",
        "Refresh 更新队列状态。"
      ],
      notes: [
        "api_key 模式下，批准/拒绝需在 Settings 配置 reviewer 角色 Key。",
        "候选策略应经过：回测 → 风控 → 审计 → 人工审查。"
      ],
      pageId: "risk"
    },
    {
      id: "agents",
      title: "智能体（Agents）",
      intro: "多智能体控制台 — 查看 Agent 卡片与 Mock 编排。",
      steps: [
        "进入 Agents — 查看已注册 Agent 角色与描述。",
        "使用 Mock run 测试 API 连通性（返回说明文本，非完整流水线）。",
        "查看各 Agent 在 ToolPolicy 下可调用的工具。"
      ],
      notes: [
        "完整 Agent 流水线亦可通过 CLI：scripts/run_agent.py。",
        "Agent 不会下实盘订单。"
      ],
      pageId: "agents"
    },
    {
      id: "tools",
      title: "受控工具（Tools）",
      intro: "暴露给 Agent 与后端的 Quant Engine 工具白名单。",
      steps: [
        "进入 Tools — 列表显示工具名、类别、允许/拒绝状态。",
        "确认 run_backtest、read_report、risk_check、query_memory 为 Allowed。",
        "Denied 工具无法被 Agent 或 Job 调用。"
      ],
      pageId: "tools"
    },
    {
      id: "memory",
      title: "记忆 / RAG（Memory）",
      intro: "搜索实验记忆并浏览 RAG 文档元数据。",
      steps: [
        "进入 Memory / RAG。",
        "输入查询（如 OOS baseline、策略名）并点击 Search。",
        "查看命中片段与分数。",
        "查看 RAG 文档表中的索引来源。"
      ],
      notes: [
        "结果依赖服务器向量库与实验记忆路径。",
        "无结果 — 检查 QUANT_MAS_EXPERIMENT_MEMORY_PATH 与后端连接。"
      ],
      pageId: "memory"
    },
    {
      id: "audit",
      title: "审计日志（Audit Logs）",
      intro: "研究操作审计轨迹。",
      steps: [
        "进入 Audit Logs。",
        "浏览表格：timestamp、actor、action、resource、status。",
        "与 Risk Review 决策一并用于合规审查。"
      ],
      notes: [
        "服务器配置 QUANT_MAS_AUDIT_DIR 以加载 JSONL 审计事件。",
        "api_key 模式下可能需要 reviewer 角色。"
      ],
      pageId: "audit"
    },
    {
      id: "paper",
      title: "论文产物（Paper Artifacts）",
      intro: "导出表格、图表与 Markdown 供论文使用。",
      steps: [
        "进入 Paper Artifacts — 浏览 outputs/paper/ 下已有文件。",
        "点击 Export paper artifacts 提交 paper_export Job。",
        "等待 Job Console 完成后再 Refresh。",
        "在产物表中查看或复制文件路径。"
      ],
      notes: [
        "需要 experiments.json 中至少有一条实验记录。",
        "服务器设置 QUANT_MAS_PAPER_DIR。"
      ],
      pageId: "paper"
    },
    {
      id: "database",
      title: "数据库（Database）",
      intro: "SQL、向量库与图数据库状态（元数据）。",
      steps: [
        "进入 Database — 查看 backend mode 与 vector store 类型。",
        "若已配置，查看数据表列表与图关系。",
        "Deployment 区域提供环境提示。"
      ],
      pageId: "database"
    },
    {
      id: "observability",
      title: "可观测性（Observability）",
      intro: "系统健康、Job、指标、日志与生效配置。",
      steps: [
        "进入 Observability。",
        "查看 System Health 与深度健康指标。",
        "在 Jobs 列表查看近期 backtest/OOS/export 任务。",
        "阅读 Metrics 与 Server logs（若已设 QUANT_MAS_LOG_ROOT）。",
        "查看 Effective Config 中的 auth、storage、live_trading 等。"
      ],
      notes: [
        "页面空白时，强刷（Ctrl+F5）并确保后端为最新版本。",
        "curl http://127.0.0.1:8000/api/config/effective 应返回 env 或 values 对象。"
      ],
      pageId: "observability"
    },
    {
      id: "settings",
      title: "设置与 API Key（Settings）",
      intro: "配置认证 — API Key 仅在此页配置，不在总览页。",
      steps: [
        "进入 Settings。",
        "在 API Access 中粘贴 X-Quant-MAS-Key。",
        "点击 Save，再点顶栏 Refresh。",
        "确认 Auth 与 Role 徽章与 Key 角色一致。"
      ],
      table: {
        headers: ["操作", "最低角色（api_key 模式）"],
        rows: [
          ["浏览 Dashboard", "viewer"],
          ["提交 Job / 导出论文", "researcher"],
          ["批准审查 / 读审计", "reviewer"],
          ["完整管理", "admin"]
        ]
      },
      notes: [
        "open 模式 — 开发环境无需 Key。",
        "Key 仅存于浏览器 localStorage，切勿提交到 Git。"
      ],
      pageId: "settings"
    },
    {
      id: "jobs",
      title: "Job 工作流（通用）",
      intro: "所有可执行研究任务共用 Job Console 模式。",
      steps: [
        "在 Backtests、Experiments、OOS 或 Paper 页填写表单。",
        "提交 — Job 获得 id，如 job-YYYYMMDD-xxxxxx。",
        "Job Console 推送事件：queued、started、progress、completed/failed。",
        "failed — 阅读错误信息（缺数据、导入错误、403 等）。",
        "completed — 点击 Refresh 将新产物载入 UI。"
      ],
      bullets: [
        "backtest — 均线交叉，产物 outputs/reports/backtest_latest/",
        "walk_forward_oos — 论文级 OOS，产物 outputs/reports/walk_forward_latest/",
        "paper_export — CSV/MD/JSON 于 outputs/paper/"
      ]
    },
    {
      id: "data-prep",
      title: "数据准备（首次运行）",
      intro: "在服务器上、提交 UI Job 之前执行。",
      commands: [
        "cd /mnt/localDisk3/weizian/Quant-MAS",
        "mkdir -p data/raw",
        "",
        "# 下载 OHLCV（必须指定 --symbols）",
        "PYTHONPATH=src python scripts/download_data.py \\",
        "  --symbols AAPL MSFT SPY --start 2018-01-01 --end 2025-12-31 --source auto",
        "",
        "# OOS 所需特征",
        "PYTHONPATH=src python scripts/build_features.py",
        "",
        "ls -lh data/raw/market_data.parquet",
        "ls -lh data/features/features.parquet"
      ],
      notes: [
        "Yahoo 限流时可 --source stooq 并在 .env 配置 STOOQ_API_KEY。",
        "或链接已有数据：ln -sf /path/to/market_data.parquet data/raw/"
      ]
    },
    {
      id: "troubleshooting",
      title: "故障排查",
      table: {
        headers: ["现象", "处理"],
        rows: [
          ["顶栏 Local fallback", "启动 SSH 隧道与 uvicorn；curl /api/status"],
          ["Run backtest 返回 405", "git pull 含 POST /api/jobs 的最新后端"],
          ["Job failed: parquet 缺失", "在服务器运行 download_data.py"],
          ["Job failed: features 缺失", "运行 build_features.py"],
          ["POST 403", "使用 researcher/reviewer Key 或 QUANT_MAS_AUTH_MODE=open"],
          ["Observability 空白", "更新代码、重启 uvicorn、Ctrl+F5"],
          ["回测页满屏绿色竖条", "更新前端 — 权益曲线归一化修复"]
        ]
      }
    },
    {
      id: "cli",
      title: "命令行替代（CLI）",
      intro: "UI 与 CLI 共用同一 Quant Engine。",
      commands: [
        "python scripts/run_backtest.py --config configs/backtest.yaml",
        "python scripts/run_walk_forward.py --config configs/walk_forward.yaml",
        "python scripts/export_paper_artifacts.py \\",
        "  --memory-path outputs/reports/experiments.json \\",
        "  --output-dir outputs/paper"
      ],
      notes: ["建议：长任务在服务器用 CLI 跑；UI 用于查看、审查与展示。"]
    }
  ]
};

export const helpGuides: Record<Locale, HelpGuide> = { en, zh };

export function getHelpGuide(locale: Locale): HelpGuide {
  return helpGuides[locale] ?? helpGuides.en;
}
