import { readJson } from "./client";

export interface ReviewItem {
  review_id: string;
  experiment_id: string;
  candidate_type: string;
  status: string;
  metric_family: string;
  human_confirmation_required: boolean;
  required_gates: string[];
  summary: string;
}

export interface ReviewQueuePayload {
  source: string;
  reviews: ReviewItem[];
}

export interface JobItem {
  job_id: string;
  type: string;
  status: string;
  progress: number;
  summary: string;
}

export interface JobsPayload {
  source: string;
  jobs: JobItem[];
}

export const fallbackReviewQueue: ReviewQueuePayload = {
  source: "fallback_review_queue",
  reviews: [
    {
      review_id: "review-demo-001",
      experiment_id: "EXP-20260602-008",
      candidate_type: "paper_claim",
      status: "pending",
      metric_family: "oos",
      human_confirmation_required: true,
      required_gates: ["backtest", "risk_check", "audit_log", "human_confirmation"],
      summary: "Review OOS baseline claim before paper-grade presentation."
    }
  ]
};

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

export function fetchReviewQueue(): Promise<ReviewQueuePayload> {
  return readJson<ReviewQueuePayload>("/api/review/queue");
}

export function fetchJobs(): Promise<JobsPayload> {
  return readJson<JobsPayload>("/api/jobs");
}
