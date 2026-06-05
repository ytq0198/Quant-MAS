import { useState } from "react";

import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { runAgent } from "../api/phase2";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function Agents({ data }: { data: DashboardData }) {
  const { agents } = data;
  const { t } = useLanguage();
  const [consoleLog, setConsoleLog] = useState<string[]>([]);
  const [running, setRunning] = useState(false);

  async function handleRun(agentName: string) {
    setRunning(true);
    try {
      const result = await runAgent(agentName, "Summarize latest OOS baseline for research report.");
      setConsoleLog((prev) => [`[${result.status}] ${result.agent}: ${result.summary}`, ...prev].slice(0, 8));
    } catch {
      setConsoleLog((prev) => [t("agents.fallbackRun", { agent: agentName }), ...prev].slice(0, 8));
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="page">
      <div className="agent-grid">
        {agents.map((agent) => (
          <Card key={agent.name} title={agent.name}>
            <p className="muted">{agent.role}</p>
            <div className="badge-row">
              <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
            </div>
            <div className="detail-block">
              <h4>{t("common.allowed")}</h4>
              <p>{agent.tools.join(" · ")}</p>
            </div>
            <div className="detail-block">
              <h4>{t("common.denied")}</h4>
              <p>{t("agents.deniedList")}</p>
            </div>
            <button
              type="button"
              className="btn btn--primary"
              disabled={running}
              onClick={() => void handleRun(agent.name)}
            >
              {t("agents.mockRun")}
            </button>
          </Card>
        ))}
      </div>

      <Card title={t("agents.console")} subtitle={t("agents.consoleSubtitle")}>
        <pre className="console-panel">
          {consoleLog.length === 0 ? t("agents.consoleEmpty") : consoleLog.join("\n")}
        </pre>
      </Card>
    </div>
  );
}
