import { Badge } from "../components/Badge";
import { Card, StatCard } from "../components/Card";
import { SafetyBoundary, WorkflowStepper } from "../components/SafetyBoundary";
import { useLanguage } from "../i18n/LanguageContext";
import type { TranslationKey } from "../i18n/translations";
import type { DashboardData } from "../hooks/useDashboardData";
import type { PageId } from "../types/navigation";

const SHORTCUT_IDS: Array<{
  id: PageId;
  titleKey: TranslationKey;
  descKey: TranslationKey;
  badgeKey: TranslationKey;
  icon: string;
}> = [
  {
    id: "experiments",
    titleKey: "shortcut.experiments.title",
    descKey: "shortcut.experiments.desc",
    badgeKey: "shortcut.experiments.badge",
    icon: "▣"
  },
  {
    id: "backtests",
    titleKey: "shortcut.backtests.title",
    descKey: "shortcut.backtests.desc",
    badgeKey: "shortcut.backtests.badge",
    icon: "▤"
  },
  {
    id: "oos",
    titleKey: "shortcut.oos.title",
    descKey: "shortcut.oos.desc",
    badgeKey: "shortcut.oos.badge",
    icon: "◎"
  },
  {
    id: "risk",
    titleKey: "shortcut.risk.title",
    descKey: "shortcut.risk.desc",
    badgeKey: "shortcut.risk.badge",
    icon: "◈"
  },
  {
    id: "agents",
    titleKey: "shortcut.agents.title",
    descKey: "shortcut.agents.desc",
    badgeKey: "shortcut.agents.badge",
    icon: "◆"
  },
  {
    id: "memory",
    titleKey: "shortcut.memory.title",
    descKey: "shortcut.memory.desc",
    badgeKey: "shortcut.memory.badge",
    icon: "⌕"
  },
  {
    id: "audit",
    titleKey: "shortcut.audit.title",
    descKey: "shortcut.audit.desc",
    badgeKey: "shortcut.audit.badge",
    icon: "☰"
  },
  {
    id: "paper",
    titleKey: "shortcut.paper.title",
    descKey: "shortcut.paper.desc",
    badgeKey: "shortcut.paper.badge",
    icon: "▦"
  },
  {
    id: "help",
    titleKey: "shortcut.help.title",
    descKey: "shortcut.help.desc",
    badgeKey: "shortcut.help.badge",
    icon: "?"
  }
];

export function Overview({
  data,
  onNavigate
}: {
  data: DashboardData;
  onNavigate: (page: PageId) => void;
}) {
  const { status, source } = data;
  const { t } = useLanguage();

  return (
    <div className="page page--overview">
      <section className="hero-summary">
        <div className="hero-summary__copy">
          <h2 className="page-heading">Quant MAS</h2>
          <p className="page-lead">{t("overview.lead")}</p>
          <p className="muted">{t("overview.tagline")}</p>
        </div>
        <div className="hero-summary__status">
          <Badge tone={source === "api" ? "success" : "warning"}>
            {source === "api" ? t("header.backendOk") : t("header.backendFallback")}
          </Badge>
          <Badge tone="info">{status.baselines.tests}</Badge>
          <Badge tone="info">OOS {status.baselines.oos_sharpe.toFixed(3)}</Badge>
          <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
        </div>
      </section>

      <section className="kpi-row">
        <StatCard
          label={t("overview.kpiTests")}
          value={status.baselines.tests.split(" ")[0]}
          hint={status.baselines.tests}
        />
        <StatCard
          label={t("overview.kpiOosBaseline")}
          value={status.baselines.oos_sharpe.toFixed(3)}
          hint={t("safety.paperGrade")}
        />
        <StatCard
          label={t("overview.kpiOosExperiment")}
          value={status.baselines.oos_experiment}
          hint={t("overview.selectedBaseline")}
        />
        <StatCard
          label={t("overview.kpiSafety")}
          value={t("safety.disabled")}
          hint={t("safety.liveTradingDisabled")}
          tone="danger"
        />
      </section>

      <Card title={t("workflow.title")} subtitle={t("workflow.subtitle")}>
        <WorkflowStepper />
      </Card>

      <Card title={t("overview.safetyBoundary")} accent="safety">
        <SafetyBoundary status={status} />
      </Card>

      <section>
        <h3 className="section-title">{t("overview.moduleShortcuts")}</h3>
        <div className="shortcut-grid">
          {SHORTCUT_IDS.map((item) => (
            <button
              type="button"
              key={item.id}
              className="shortcut-card"
              onClick={() => onNavigate(item.id)}
            >
              <span className="shortcut-card__icon">{item.icon}</span>
              <strong>{t(item.titleKey)}</strong>
              <p>{t(item.descKey)}</p>
              <Badge tone="muted">{t(item.badgeKey)}</Badge>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
