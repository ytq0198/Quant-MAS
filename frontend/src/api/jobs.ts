import { postJson, readJson } from "./client";

export type JobType = "backtest" | "walk_forward_oos" | "paper_export";

export interface JobItem {
  job_id: string;
  type: string;
  status: string;
  progress: number;
  summary: string;
  submitted_by?: string;
  created_at?: string;
  updated_at?: string;
  error?: string;
  result?: Record<string, unknown> | null;
}

export interface JobsPayload {
  source: string;
  jobs: JobItem[];
}

export interface JobDetailPayload {
  source: string;
  job: JobItem | null;
  events: Array<{ timestamp?: string; type: string; message: string }>;
  message?: string;
}

export interface CreateJobRequest {
  type: JobType;
  params?: Record<string, unknown>;
  summary?: string;
}

export const fallbackJobs: JobsPayload = {
  source: "fallback_jobs",
  jobs: [
    {
      job_id: "job-demo-001",
      type: "artifact_export",
      status: "completed",
      progress: 1,
      summary: "Fallback paper artifact export job."
    }
  ]
};

export function fetchJobs(): Promise<JobsPayload> {
  return readJson<JobsPayload>("/api/jobs");
}

export function fetchJobDetail(jobId: string): Promise<JobDetailPayload> {
  return readJson<JobDetailPayload>(`/api/jobs/${encodeURIComponent(jobId)}`);
}

export function createJob(request: CreateJobRequest): Promise<{ source: string; job: JobItem }> {
  return postJson("/api/jobs", request);
}

export function exportPaperArtifacts(params: Record<string, string> = {}): Promise<{ source: string; job: JobItem }> {
  return postJson("/api/artifacts/export", params);
}

export function isTerminalStatus(status: string): boolean {
  return status === "completed" || status === "failed";
}
