import { readJson } from "./client";

export interface DatabaseTablesPayload {
  mode: string;
  status: string;
  required_for_tests: boolean;
  tables: string[];
  notes: string;
}

export interface RagDocumentsPayload {
  source: string;
  vector_store: string;
  documents: Array<{ document_id: string; type: string; title: string; snippet: string }>;
}

export interface GraphRelationshipsPayload {
  source: string;
  required_for_tests: boolean;
  relationships: Array<{ source: string; relation: string; target: string }>;
}

export const fallbackDatabaseTables: DatabaseTablesPayload = {
  mode: "local_files",
  status: "local_files",
  required_for_tests: false,
  tables: ["experiments", "experiment_metrics", "audit_logs", "paper_artifacts"],
  notes: "Database tables are optional; local artifact mode remains the default."
};

export const fallbackRagDocuments: RagDocumentsPayload = {
  source: "fallback_documents",
  vector_store: "fallback",
  documents: [
    {
      document_id: "doc-research-protocol",
      type: "research_protocol",
      title: "Metric family separation",
      snippet: "Do not mix oos.* with simulation.*, training.*, population.*, or audit.* metrics."
    }
  ]
};

export const fallbackGraph: GraphRelationshipsPayload = {
  source: "fallback_graph",
  required_for_tests: false,
  relationships: [
    { source: "ResearchAgent", relation: "calls", target: "BacktestTool" },
    { source: "EXP-20260602-008", relation: "evaluated_by", target: "Walk-forward OOS" }
  ]
};

export function fetchDatabaseTables(): Promise<DatabaseTablesPayload> {
  return readJson<DatabaseTablesPayload>("/api/database/tables");
}

export function fetchRagDocuments(): Promise<RagDocumentsPayload> {
  return readJson<RagDocumentsPayload>("/api/rag/documents");
}

export function fetchGraphRelationships(): Promise<GraphRelationshipsPayload> {
  return readJson<GraphRelationshipsPayload>("/api/graph/relationships");
}
