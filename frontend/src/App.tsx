import { useState } from "react";

import { AppShell } from "./components/AppShell";
import { useLanguage } from "./i18n/LanguageContext";
import { useDashboardData } from "./hooks/useDashboardData";
import { Overview } from "./pages/Overview";
import { Experiments } from "./pages/Experiments";
import { Backtests } from "./pages/Backtests";
import { OOSViewer } from "./pages/OOSViewer";
import { RiskReview } from "./pages/RiskReview";
import { Agents } from "./pages/Agents";
import { Tools } from "./pages/Tools";
import { MemoryRAG } from "./pages/MemoryRAG";
import { AuditLogs } from "./pages/AuditLogs";
import { PaperArtifacts } from "./pages/PaperArtifacts";
import { Database } from "./pages/Database";
import { Observability } from "./pages/Observability";
import { Settings } from "./pages/Settings";
import type { PageId } from "./types/navigation";

export function App() {
  const [page, setPage] = useState<PageId>("overview");
  const data = useDashboardData();
  const { t } = useLanguage();
  const selectedExperimentId =
    data.experiments.experiments[0]?.experiment_id ?? data.status.baselines.oos_experiment;

  function renderPage() {
    if (data.loading && page === "overview") {
      return <div className="loading-state">{t("common.loading")}</div>;
    }

    switch (page) {
      case "overview":
        return <Overview data={data} onNavigate={setPage} />;
      case "experiments":
        return <Experiments data={data} onRefresh={() => void data.refresh()} />;
      case "backtests":
        return <Backtests data={data} onRefresh={() => void data.refresh()} />;
      case "oos":
        return <OOSViewer data={data} onRefresh={() => void data.refresh()} />;
      case "risk":
        return <RiskReview data={data} onRefresh={() => void data.refresh()} />;
      case "agents":
        return <Agents data={data} />;
      case "tools":
        return <Tools data={data} />;
      case "memory":
        return <MemoryRAG data={data} />;
      case "audit":
        return <AuditLogs data={data} />;
      case "paper":
        return <PaperArtifacts data={data} onRefresh={() => void data.refresh()} />;
      case "database":
        return <Database data={data} />;
      case "observability":
        return <Observability data={data} onRefresh={() => void data.refresh()} />;
      case "settings":
        return <Settings data={data} onRefresh={data.refresh} />;
      default:
        return <Overview data={data} onNavigate={setPage} />;
    }
  }

  return (
    <AppShell
      page={page}
      onNavigate={setPage}
      status={data.status}
      auth={data.auth}
      source={data.source}
      loading={data.loading}
      onRefresh={() => void data.refresh()}
      selectedExperimentId={selectedExperimentId}
    >
      {renderPage()}
    </AppShell>
  );
}
