import { postJson } from "./client";
import {
  fallbackReviewQueue,
  fetchReviewQueue,
  type ReviewQueuePayload,
  type ReviewItem
} from "./phase7";

export { fallbackReviewQueue, fetchReviewQueue, type ReviewQueuePayload, type ReviewItem };

export function approveReview(reviewId: string): Promise<Record<string, unknown>> {
  return postJson(`/api/review/${encodeURIComponent(reviewId)}/approve`, {});
}

export function rejectReview(reviewId: string, reason = ""): Promise<Record<string, unknown>> {
  return postJson(`/api/review/${encodeURIComponent(reviewId)}/reject`, { reason });
}
