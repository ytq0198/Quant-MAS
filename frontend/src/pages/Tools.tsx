import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

const ALLOWED = ["run_backtest", "read_report", "risk_check", "query_memory"];
const DENIED = ["shell", "broker", "order", "secrets"];

export function Tools({ data }: { data: DashboardData }) {
  const { tools } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <Card title={t("tools.policy")} subtitle={t("tools.policySubtitle")}>
        <div className="policy-grid">
          <div>
            <h4 className="section-title">{t("common.allowed")}</h4>
            <div className="badge-row wrap">
              {ALLOWED.map((op) => (
                <Badge key={op} tone="success">
                  {op}
                </Badge>
              ))}
            </div>
          </div>
          <div>
            <h4 className="section-title">{t("common.denied")}</h4>
            <div className="badge-row wrap">
              {DENIED.map((op) => (
                <Badge key={op} tone="danger">
                  {op}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <div className="tool-grid">
        {tools.map((tool) => (
          <Card key={tool.name} title={tool.name}>
            <p className="muted">{tool.description}</p>
            <div className="badge-row wrap">
              {tool.allowed_operations.map((op) => (
                <Badge key={op} tone="success">
                  {op}
                </Badge>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
