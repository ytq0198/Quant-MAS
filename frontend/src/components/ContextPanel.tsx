import type { StatusPayload } from "../api/status";
import { useLanguage } from "../i18n/LanguageContext";
import { Badge, MetricFamilyBadge } from "./Badge";

export function ContextPanel({
  status,
  selectedExperimentId
}: {
  status: StatusPayload;
  selectedExperimentId: string;
}) {
  const { t } = useLanguage();

  return (
    <aside className="context-panel">
      <section>
        <h3>{t("context.safetyBoundary")}</h3>
        <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
        <p className="context-panel__text">{t("context.noLiveOrders")}</p>
      </section>
      <section>
        <h3>{t("context.currentExperiment")}</h3>
        <p className="context-panel__mono">{selectedExperimentId}</p>
        <MetricFamilyBadge family="oos" />
      </section>
      <section>
        <h3>{t("context.metricReminder")}</h3>
        <div className="context-panel__badges">
          <MetricFamilyBadge family="oos" />
          <MetricFamilyBadge family="simulation" />
          <MetricFamilyBadge family="population" />
        </div>
        <p className="context-panel__text">{t("context.metricReminderText")}</p>
      </section>
      <section>
        <h3>{t("context.baseline")}</h3>
        <p className="context-panel__text">
          OOS Sharpe {status.baselines.oos_sharpe.toFixed(3)} · {status.baselines.tests}
        </p>
      </section>
    </aside>
  );
}
