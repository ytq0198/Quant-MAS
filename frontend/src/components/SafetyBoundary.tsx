import type { StatusPayload } from "../api/status";
import { useLanguage } from "../i18n/LanguageContext";
import { Badge } from "./Badge";

export function SafetyBoundary({ status }: { status: StatusPayload }) {
  const { t, tApi } = useLanguage();

  return (
    <div className="safety-boundary">
      <div className="safety-boundary__head">
        <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
        <Badge tone="warning">{t("safety.humanReviewRequired")}</Badge>
      </div>
      <ul className="safety-boundary__list">
        {status.safety.principles.map((principle) => (
          <li key={principle}>{tApi(principle)}</li>
        ))}
      </ul>
    </div>
  );
}

export function WorkflowStepper() {
  const { t } = useLanguage();
  const steps = [
    t("workflow.data"),
    t("workflow.features"),
    t("workflow.model"),
    t("workflow.backtest"),
    t("workflow.risk"),
    t("workflow.oos"),
    t("workflow.audit"),
    t("workflow.humanReview"),
    t("workflow.paperExport")
  ];

  return (
    <div className="workflow-stepper" aria-label={t("workflow.ariaLabel")}>
      {steps.map((step, index) => (
        <div className="workflow-stepper__item" key={step}>
          <span className="workflow-stepper__dot">{index + 1}</span>
          <span className="workflow-stepper__label">{step}</span>
          {index < steps.length - 1 && <span className="workflow-stepper__line" />}
        </div>
      ))}
    </div>
  );
}
