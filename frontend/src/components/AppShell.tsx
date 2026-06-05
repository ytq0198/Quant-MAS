import { useState, type ReactNode } from "react";

import type { AuthMePayload } from "../api/auth";
import type { StatusPayload } from "../api/status";
import type { PageId } from "../types/navigation";
import { ContextPanel } from "./ContextPanel";
import { Header } from "./Header";
import { PageToolbar } from "./PageToolbar";
import { Sidebar } from "./Sidebar";

export function AppShell({
  page,
  onNavigate,
  status,
  auth,
  source,
  loading,
  onRefresh,
  selectedExperimentId,
  children
}: {
  page: PageId;
  onNavigate: (page: PageId) => void;
  status: StatusPayload;
  auth: AuthMePayload;
  source: "api" | "fallback";
  loading: boolean;
  onRefresh: () => void;
  selectedExperimentId: string;
  children: ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="layout">
      <Sidebar
        active={page}
        onNavigate={onNavigate}
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed((value) => !value)}
      />
      <div className="layout__main">
        <Header page={page} source={source} auth={auth} onRefresh={onRefresh} loading={loading} />
        <div className="layout__body">
          <main className="layout__content">
            <PageToolbar />
            {children}
          </main>
          {page !== "settings" && (
            <ContextPanel status={status} selectedExperimentId={selectedExperimentId} />
          )}
        </div>
      </div>
    </div>
  );
}
