import { useState, type FormEvent } from "react";

import type { JobType } from "../api/jobs";
import { useLanguage } from "../i18n/LanguageContext";
import { useJobRunner } from "../hooks/useJobRunner";
import { JobConsole } from "./JobConsole";

export function ResearchJobPanel({
  jobType,
  onComplete
}: {
  jobType: JobType;
  onComplete?: () => void;
}) {
  const { t } = useLanguage();
  const { activeJob, events, submitting, error, submitJob } = useJobRunner(onComplete);
  const [experimentName, setExperimentName] = useState(
    jobType === "backtest" ? "ui_moving_average_backtest" : "ui_walk_forward_oos"
  );
  const [fastWindow, setFastWindow] = useState("5");
  const [slowWindow, setSlowWindow] = useState("20");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const params: Record<string, unknown> = { experiment_name: experimentName.trim() };
    if (jobType === "backtest") {
      params.fast_window = Number(fastWindow);
      params.slow_window = Number(slowWindow);
    }
    await submitJob({
      type: jobType,
      params,
      summary: t(`jobs.submitSummary.${jobType}`)
    });
  }

  return (
    <section className="research-job-panel">
      <form className="research-job-form" onSubmit={(e) => void handleSubmit(e)}>
        <h3 className="section-title">{t(`jobs.formTitle.${jobType}`)}</h3>
        <p className="muted">{t("jobs.researchOnlyNote")}</p>
        <label className="form-field">
          <span>{t("jobs.experimentName")}</span>
          <input value={experimentName} onChange={(e) => setExperimentName(e.target.value)} required />
        </label>
        {jobType === "backtest" && (
          <div className="form-row">
            <label className="form-field">
              <span>{t("jobs.fastWindow")}</span>
              <input value={fastWindow} onChange={(e) => setFastWindow(e.target.value)} type="number" min={2} />
            </label>
            <label className="form-field">
              <span>{t("jobs.slowWindow")}</span>
              <input value={slowWindow} onChange={(e) => setSlowWindow(e.target.value)} type="number" min={3} />
            </label>
          </div>
        )}
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? t("jobs.submitting") : t(`jobs.submit.${jobType}`)}
        </button>
      </form>
      <JobConsole job={activeJob} events={events} error={error} />
    </section>
  );
}

export function PaperExportPanel({ onComplete }: { onComplete?: () => void }) {
  const { t } = useLanguage();
  const { activeJob, events, submitting, error, submitPaperExport } = useJobRunner(onComplete);

  return (
    <section className="research-job-panel">
      <div className="research-job-form">
        <h3 className="section-title">{t("jobs.formTitle.paper_export")}</h3>
        <p className="muted">{t("jobs.paperExportNote")}</p>
        <button type="button" className="btn btn--primary" disabled={submitting} onClick={() => void submitPaperExport()}>
          {submitting ? t("jobs.submitting") : t("jobs.submit.paper_export")}
        </button>
      </div>
      <JobConsole job={activeJob} events={events} error={error} />
    </section>
  );
}
