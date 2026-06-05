import { useCallback, useEffect, useRef, useState } from "react";

import {
  createJob,
  exportPaperArtifacts,
  fetchJobDetail,
  isTerminalStatus,
  type CreateJobRequest,
  type JobItem
} from "../api/jobs";

export function useJobRunner(onComplete?: () => void) {
  const [activeJob, setActiveJob] = useState<JobItem | null>(null);
  const [events, setEvents] = useState<Array<{ type: string; message: string; timestamp?: string }>>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const timerRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const pollJob = useCallback(
    (jobId: string) => {
      stopPolling();
      timerRef.current = window.setInterval(() => {
        void fetchJobDetail(jobId)
          .then((payload) => {
            if (!payload.job) return;
            setActiveJob(payload.job);
            setEvents(payload.events ?? []);
            if (isTerminalStatus(payload.job.status)) {
              stopPolling();
              onComplete?.();
            }
          })
          .catch(() => {
            stopPolling();
          });
      }, 1500);
    },
    [onComplete, stopPolling]
  );

  useEffect(() => () => stopPolling(), [stopPolling]);

  const submitJob = useCallback(
    async (request: CreateJobRequest) => {
      setSubmitting(true);
      setError("");
      try {
        const payload = await createJob(request);
        setActiveJob(payload.job);
        setEvents([{ type: "job.submitted", message: payload.job.summary }]);
        pollJob(payload.job.job_id);
        return payload.job;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Job submission failed.";
        setError(message);
        throw err;
      } finally {
        setSubmitting(false);
      }
    },
    [pollJob]
  );

  const submitPaperExport = useCallback(async () => {
    setSubmitting(true);
    setError("");
    try {
      const payload = await exportPaperArtifacts();
      setActiveJob(payload.job);
      pollJob(payload.job.job_id);
      return payload.job;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Export failed.";
      setError(message);
      throw err;
    } finally {
      setSubmitting(false);
    }
  }, [pollJob]);

  return {
    activeJob,
    events,
    submitting,
    error,
    submitJob,
    submitPaperExport,
    clearActiveJob: () => {
      stopPolling();
      setActiveJob(null);
      setEvents([]);
      setError("");
    }
  };
}
