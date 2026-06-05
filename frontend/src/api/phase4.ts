export interface DatabaseBackend {
  name: string;
  purpose: string;
  required_for_tests: boolean;
  status: string;
}

export interface DatabaseStatus {
  mode: string;
  default_backend: string;
  summary: string;
  backends: DatabaseBackend[];
}

export interface DeploymentStatus {
  phase: string;
  frontend: {
    stack: string;
    dev_url: string;
    build_dir: string;
  };
  backend: {
    stack: string;
    dev_url: string;
    entrypoint: string;
  };
  artifacts: string[];
  safety: {
    live_trading_enabled: boolean;
    notes: string[];
  };
}

export const fallbackDatabase: DatabaseStatus = {
  mode: "optional",
  default_backend: "local_files",
  summary: "Phase 4 documents database-ready paths without requiring live services for tests.",
  backends: [
    {
      name: "local_files",
      purpose: "Parquet and JSONL local data, reports, audit logs, and fixtures.",
      required_for_tests: true,
      status: "available_by_default"
    },
    {
      name: "postgres",
      purpose: "Server-side experiments, task state, and metadata tables.",
      required_for_tests: false,
      status: "optional"
    },
    {
      name: "pgvector",
      purpose: "Vector search for RAG over documents, reports, and experiment memory.",
      required_for_tests: false,
      status: "optional"
    },
    {
      name: "neo4j",
      purpose: "Optional graph relationships across agents, tools, experiments, and documents.",
      required_for_tests: false,
      status: "optional"
    }
  ]
};

export const fallbackDeployment: DeploymentStatus = {
  phase: "v4-phase-4",
  frontend: {
    stack: "React + Vite",
    dev_url: "http://127.0.0.1:5173",
    build_dir: "frontend/dist"
  },
  backend: {
    stack: "FastAPI + Uvicorn",
    dev_url: "http://127.0.0.1:8000",
    entrypoint: "backend.app:app"
  },
  artifacts: [
    "docker-compose.yml",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    "docs/database_setup.md",
    "docs/fullstack_quickstart.md"
  ],
  safety: {
    live_trading_enabled: false,
    notes: [
      "Deployment skeleton exposes research APIs only.",
      "No broker, order, shell, or secrets path is exposed through Phase 4 status APIs."
    ]
  }
};

async function readJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchDatabaseStatus(): Promise<DatabaseStatus> {
  return readJson<DatabaseStatus>("/api/database/status");
}

export function fetchDeploymentStatus(): Promise<DeploymentStatus> {
  return readJson<DeploymentStatus>("/api/deployment/status");
}
