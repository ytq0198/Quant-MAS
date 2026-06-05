import { readJson } from "./client";

export interface BacktestSummary {
  id: string;
  title: string;
  metric_family: string;
  is_oos: boolean;
  research_only: boolean;
  strategy: string;
  chart: Array<{ label: string; equity: number }>;
  notes: string[];
  disclaimer: string;
}

export interface OosSummary {
  id: string;
  title: string;
  metric_family: string;
  is_oos: boolean;
  paper_grade: boolean;
  sharpe: number;
  window_count: number;
  windows: Array<{ window: string; status: string }>;
  notes: string[];
}

export interface RiskSummary {
  id: string;
  status: string;
  live_trading_enabled: boolean;
  human_confirmation_required: boolean;
  checks: Array<{ name: string; status: string }>;
  required_gates: string[];
  decision: string;
}

export const fallbackBacktest: BacktestSummary = {
  id: "demo-backtest",
  title: "Demo deterministic backtest summary",
  metric_family: "backtest.summary",
  is_oos: false,
  research_only: true,
  strategy: "MLSignalStrategy candidate",
  chart: [
    { label: "start", equity: 1.0 },
    { label: "mid", equity: 1.03 },
    { label: "end", equity: 1.01 }
  ],
  notes: [
    "Backtest summaries are not paper-grade OOS conclusions.",
    "Use walk-forward OOS for paper-grade baseline comparison."
  ],
  disclaimer: "Research only; not financial advice; not a live-trading signal."
};

export const fallbackOos: OosSummary = {
  id: "EXP-20260602-008",
  title: "Walk-forward OOS baseline",
  metric_family: "oos",
  is_oos: true,
  paper_grade: true,
  sharpe: 0.586,
  window_count: 19,
  windows: [
    { window: "W01", status: "audited" },
    { window: "W02", status: "audited" },
    { window: "W03-W19", status: "audited aggregate" }
  ],
  notes: [
    "Only audited walk-forward OOS metrics can support paper-grade conclusions.",
    "Do not mix oos.* with simulation.*, training.*, population.*, or audit.* metrics."
  ]
};

export const fallbackRisk: RiskSummary = {
  id: "demo-risk",
  status: "review_required",
  live_trading_enabled: false,
  human_confirmation_required: true,
  checks: [
    { name: "Backtest completed", status: "required" },
    { name: "Risk limits checked", status: "required" },
    { name: "Audit log written", status: "required" },
    { name: "Human confirmation", status: "required" }
  ],
  required_gates: ["backtest", "risk check", "audit log", "human confirmation"],
  decision: "No candidate can move to live trading from this UI."
};

export function fetchBacktestSummary(): Promise<BacktestSummary> {
  return readJson<BacktestSummary>("/api/backtests/demo-backtest");
}

export function fetchOosSummary(): Promise<OosSummary> {
  return readJson<OosSummary>("/api/oos/EXP-20260602-008");
}

export function fetchRiskSummary(): Promise<RiskSummary> {
  return readJson<RiskSummary>("/api/risk/demo-risk");
}
