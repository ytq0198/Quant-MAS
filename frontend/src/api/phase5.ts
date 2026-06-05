import { readJson } from "./client";

export interface ExperimentRecord {
  experiment_id: string;
  name: string;
  status: string;
  metrics: Record<string, unknown>;
  metric_family_summary: Record<string, boolean>;
  artifacts: Record<string, string>;
  notes: string;
}

export interface ExperimentsPayload {
  source: string;
  path: string;
  experiments: ExperimentRecord[];
}

export interface PaperArtifact {
  name: string;
  path: string;
  suffix: string;
  size_bytes: number;
}

export interface PaperArtifactsPayload {
  source: string;
  path: string;
  artifacts: PaperArtifact[];
}

export interface AuditLogsPayload {
  source: string;
  path: string;
  events: Array<Record<string, unknown>>;
}

export const fallbackExperiments: ExperimentsPayload = {
  source: "fallback_baseline",
  path: "outputs/reports/experiments.json",
  experiments: [
    {
      experiment_id: "EXP-20260602-008",
      name: "Walk-forward OOS baseline",
      status: "documented",
      metrics: { oos: { sharpe: 0.586, window_count: 19 } },
      metric_family_summary: {
        oos: true,
        simulation: false,
        training: false,
        population: false,
        audit: false
      },
      artifacts: {},
      notes: "Fallback baseline from documented project context."
    }
  ]
};

export const fallbackPaperArtifacts: PaperArtifactsPayload = {
  source: "fallback_empty",
  path: "outputs/paper",
  artifacts: []
};

export const fallbackAuditLogs: AuditLogsPayload = {
  source: "fallback_empty",
  path: "outputs/pipelines",
  events: []
};

export function fetchExperiments(): Promise<ExperimentsPayload> {
  return readJson<ExperimentsPayload>("/api/experiments");
}

export function fetchPaperArtifacts(): Promise<PaperArtifactsPayload> {
  return readJson<PaperArtifactsPayload>("/api/artifacts/paper");
}

export function fetchAuditLogs(): Promise<AuditLogsPayload> {
  return readJson<AuditLogsPayload>("/api/audit/logs");
}
