import type { ReactNode } from "react";

type BadgeTone = "default" | "success" | "warning" | "danger" | "info" | "muted" | "purple";

const TONE_CLASS: Record<BadgeTone, string> = {
  default: "badge--default",
  success: "badge--success",
  warning: "badge--warning",
  danger: "badge--danger",
  info: "badge--info",
  muted: "badge--muted",
  purple: "badge--purple"
};

export function Badge({
  children,
  tone = "default"
}: {
  children: ReactNode;
  tone?: BadgeTone;
}) {
  return <span className={`badge ${TONE_CLASS[tone]}`}>{children}</span>;
}

export type MetricFamily =
  | "oos"
  | "simulation"
  | "training"
  | "population"
  | "audit"
  | "research";

const METRIC_TONE: Record<MetricFamily, BadgeTone> = {
  oos: "info",
  simulation: "purple",
  training: "muted",
  population: "warning",
  audit: "success",
  research: "muted"
};

export function MetricFamilyBadge({ family }: { family: MetricFamily | string }) {
  const key = family.replace(/\.\*$/, "").replace(/\./g, "") as MetricFamily;
  const tone = METRIC_TONE[key] ?? "muted";
  const label = family.includes(".") ? `${family}` : `${family}.*`;
  return <Badge tone={tone}>{label}</Badge>;
}
