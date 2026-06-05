import { Badge } from "./Badge";
import { Card } from "./Card";
import { useLanguage } from "../i18n/LanguageContext";
import type { JobItem } from "../api/jobs";

function statusTone(status: string): "success" | "warning" | "danger" | "info" | "muted" {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  if (status === "running") return "info";
  if (status === "queued") return "warning";
  return "muted";
}

export function JobConsole({
  job,
  events,
  error
}: {
  job: JobItem | null;
  events: Array<{ type: string; message: string; timestamp?: string }>;
  error?: string;
}) {
  const { t } = useLanguage();

  if (!job && !error) {
    return null;
  }

  return (
    <Card title={t("jobs.console")} subtitle={t("jobs.consoleSubtitle")}>
      {error && <p className="job-console__error">{error}</p>}
      {job && (
        <div className="job-console__head">
          <span className="mono">{job.job_id}</span>
          <Badge tone={statusTone(job.status)}>{job.status}</Badge>
          <Badge tone="muted">{job.type}</Badge>
        </div>
      )}
      {job && (
        <>
          <p className="muted">{job.summary}</p>
          <div className="job-progress" aria-label="Job progress">
            <span style={{ width: `${Math.round(job.progress * 100)}%` }} />
          </div>
          {job.error && <p className="job-console__error">{job.error}</p>}
        </>
      )}
      {events.length > 0 && (
        <pre className="console-panel compact">
          {events
            .slice()
            .reverse()
            .map((event) => `[${event.type}] ${event.message}`)
            .join("\n")}
        </pre>
      )}
    </Card>
  );
}
