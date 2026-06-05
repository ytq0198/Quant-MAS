import { readJson } from "./client";
import type { EffectiveConfigPayload } from "./phase9";

export function normalizeEffectiveConfig(raw: Record<string, unknown>): EffectiveConfigPayload {
  const env =
    (raw.env as Record<string, string> | undefined) ??
    (raw.values as Record<string, string> | undefined) ??
    {};

  return {
    source: String(raw.source ?? "server_config"),
    auth_mode: String(raw.auth_mode ?? "open"),
    storage_mode: String(raw.storage_mode ?? "local_files"),
    vector_store: String(raw.vector_store ?? "in_memory"),
    live_trading_enabled: Boolean(raw.live_trading_enabled),
    env
  };
}

export function fetchEffectiveConfig(): Promise<EffectiveConfigPayload> {
  return readJson<Record<string, unknown>>("/api/config/effective").then(normalizeEffectiveConfig);
}
