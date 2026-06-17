export type PageId =
  | "overview"
  | "experiments"
  | "backtests"
  | "oos"
  | "risk"
  | "agents"
  | "tools"
  | "memory"
  | "audit"
  | "paper"
  | "database"
  | "observability"
  | "settings"
  | "help";

export interface NavItem {
  id: PageId;
  label: string;
  icon: string;
  group?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { id: "overview", label: "Overview", icon: "◉", group: "Workspace" },
  { id: "experiments", label: "Experiments", icon: "▣", group: "Research" },
  { id: "backtests", label: "Backtests", icon: "▤", group: "Research" },
  { id: "oos", label: "Walk-forward OOS", icon: "◎", group: "Research" },
  { id: "risk", label: "Risk Review", icon: "◈", group: "Research" },
  { id: "agents", label: "Agents", icon: "◆", group: "MAS" },
  { id: "tools", label: "Tools", icon: "⚙", group: "MAS" },
  { id: "memory", label: "Memory / RAG", icon: "⌕", group: "MAS" },
  { id: "audit", label: "Audit Logs", icon: "☰", group: "Compliance" },
  { id: "paper", label: "Paper Artifacts", icon: "▦", group: "Compliance" },
  { id: "database", label: "Database", icon: "⬡", group: "Platform" },
  { id: "observability", label: "Observability", icon: "◐", group: "Platform" },
  { id: "help", label: "Help", icon: "?", group: "Platform" },
  { id: "settings", label: "Settings", icon: "⚙", group: "Platform" }
];

export const PAGE_TITLES: Record<PageId, string> = {
  overview: "Overview",
  experiments: "Experiment Registry",
  backtests: "Backtest Summary",
  oos: "Walk-forward OOS",
  risk: "Risk Review",
  agents: "Agent Console",
  tools: "Controlled Tools",
  memory: "Memory / RAG Search",
  audit: "Audit Logs",
  paper: "Paper Artifacts",
  database: "Database Backends",
  observability: "Observability",
  help: "Help & User Guide",
  settings: "Settings"
};
