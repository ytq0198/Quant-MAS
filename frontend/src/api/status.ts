import { readJson } from "./client";

export interface StatusPayload {
  project: string;
  version: string;
  description: string;
  baselines: {
    tests: string;
    oos_experiment: string;
    oos_sharpe: number;
  };
  safety: {
    live_trading: boolean;
    principles: string[];
  };
  ui_modules: string[];
}

export const fallbackStatus: StatusPayload = {
  project: "Quant MAS",
  version: "v5",
  description:
    "Full-stack multi-agent quantitative research platform with deterministic quant pipelines, audited OOS evaluation, and human-reviewed workflows.",
  baselines: {
    tests: "361 passed",
    oos_experiment: "EXP-20260602-008",
    oos_sharpe: 0.586
  },
  safety: {
    live_trading: false,
    principles: [
      "LLM agents do not place live orders.",
      "All trading candidates require backtesting, risk checks, audit logs, and human confirmation.",
      "Only audited walk-forward OOS metrics can support paper-grade conclusions.",
      "simulation.*, training.*, population.*, and audit.* metrics must not be mixed with oos.* metrics."
    ]
  },
  ui_modules: [
    "Dashboard",
    "Agent Console",
    "Tool Console",
    "Memory/RAG Search",
    "Backtest View",
    "Walk-forward OOS View",
    "Audit / Human Review",
    "Paper Export",
    "API Access",
    "Human Review Queue",
    "Job Status",
    "Optional RAG / Database / Graph",
    "Observability"
  ]
};

export function fetchStatus(): Promise<StatusPayload> {
  return readJson<StatusPayload>("/api/status");
}
