import { readJson } from "./client";

export interface HealthComponent {
  name: string;
  status: string;
  detail: string;
}

export interface DeepHealthPayload {
  status: string;
  service: string;
  research_only: boolean;
  live_trading_enabled: boolean;
  components: HealthComponent[];
}

export interface MetricsSummaryPayload {
  source: string;
  research_only: boolean;
  live_trading_enabled: boolean;
  counters: Record<string, number>;
  gauges: Record<string, number>;
  notes: string[];
}

export interface RecentLogsPayload {
  source: string;
  log_root: string;
  events: Array<Record<string, unknown>>;
}

export interface EffectiveConfigPayload {
  source: string;
  auth_mode: string;
  storage_mode: string;
  vector_store: string;
  live_trading_enabled: boolean;
  env: Record<string, string>;
}

export const fallbackDeepHealth: DeepHealthPayload = {
  status: "ok",
  service: "quant-mas-backend",
  research_only: true,
  live_trading_enabled: false,
  components: [
    { name: "backend", status: "ok", detail: "FastAPI boundary available." },
    { name: "artifact_root", status: "fallback", detail: "Using local fallback artifacts." },
    { name: "database_optional", status: "optional", detail: "Postgres and Neo4j are not required locally." }
  ]
};

export const fallbackMetricsSummary: MetricsSummaryPayload = {
  source: "fallback_metrics",
  research_only: true,
  live_trading_enabled: false,
  counters: {
    api_groups: 9,
    protected_routes: 4,
    fallback_safe_services: 9
  },
  gauges: {
    oos_sharpe_baseline: 0.586,
    oos_window_count: 19
  },
  notes: ["Metrics summarize system readiness only; they are not trading performance promises."]
};

export const fallbackRecentLogs: RecentLogsPayload = {
  source: "fallback_logs",
  log_root: "logs",
  events: []
};

export const fallbackEffectiveConfig: EffectiveConfigPayload = {
  source: "fallback_config",
  auth_mode: "open",
  storage_mode: "local_files",
  vector_store: "in_memory",
  live_trading_enabled: false,
  env: {
    QUANT_MAS_AUTH_MODE: "open",
    QUANT_MAS_STORAGE_MODE: "local_files",
    VECTOR_STORE: "in_memory"
  }
};

export function fetchDeepHealth(): Promise<DeepHealthPayload> {
  return readJson<DeepHealthPayload>("/api/health/deep");
}

export function fetchMetricsSummary(): Promise<MetricsSummaryPayload> {
  return readJson<MetricsSummaryPayload>("/api/metrics/summary");
}

export function fetchRecentLogs(): Promise<RecentLogsPayload> {
  return readJson<RecentLogsPayload>("/api/logs/recent");
}

export { fetchEffectiveConfig } from "./config";
