import { useState } from "react";

import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { approveReview, rejectReview } from "../api/review";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

function reviewTone(status: string): "warning" | "success" | "danger" | "default" {
  if (status.includes("required") || status === "pending") return "warning";
  if (status.includes("approved")) return "success";
  if (status.includes("rejected")) return "danger";
  return "default";
}

export function RiskReview({ data, onRefresh }: { data: DashboardData; onRefresh: () => void }) {
  const { risk, reviewQueue } = data;
  const { t } = useLanguage();
  const [actionMessage, setActionMessage] = useState("");
  const [busyId, setBusyId] = useState("");

  async function handleApprove(reviewId: string) {
    setBusyId(reviewId);
    setActionMessage("");
    try {
      const result = await approveReview(reviewId);
      setActionMessage(String(result.status ?? t("risk.approved")));
      onRefresh();
    } catch {
      setActionMessage(t("risk.actionFailed"));
    } finally {
      setBusyId("");
    }
  }

  async function handleReject(reviewId: string) {
    setBusyId(reviewId);
    setActionMessage("");
    try {
      const result = await rejectReview(reviewId, "Rejected from research console.");
      setActionMessage(String(result.status ?? t("risk.rejected")));
      onRefresh();
    } catch {
      setActionMessage(t("risk.actionFailed"));
    } finally {
      setBusyId("");
    }
  }

  return (
    <div className="page page--split">
      <Card title={t("risk.title")} subtitle={t("risk.subtitle")}>
        <div className="badge-row">
          <Badge tone={reviewTone(risk.status)}>{risk.status}</Badge>
          <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
        </div>
        <ul className="check-list">
          {risk.checks.map((check) => (
            <li key={check.name}>
              <span>{check.name}</span>
              <Badge tone={check.status === "passed" ? "success" : "warning"}>{check.status}</Badge>
            </li>
          ))}
        </ul>
        <p className="muted">{risk.decision}</p>
      </Card>

      <Card
        title={t("risk.reviewQueue")}
        subtitle={t("risk.queueSubtitle", {
          source: reviewQueue.source,
          count: reviewQueue.reviews.length
        })}
      >
        {actionMessage && <p className="muted">{actionMessage}</p>}
        {reviewQueue.reviews.length === 0 ? (
          <p className="muted">{t("risk.noPending")}</p>
        ) : (
          <div className="stack">
            {reviewQueue.reviews.map((review) => (
              <div className="list-card" key={review.review_id}>
                <strong>{review.review_id}</strong>
                <p>{review.summary}</p>
                <div className="badge-row">
                  <Badge tone="info">{review.metric_family}</Badge>
                  <Badge tone={reviewTone(review.status)}>{review.status}</Badge>
                </div>
                {review.status === "pending" && (
                  <div className="form-row">
                    <button
                      type="button"
                      className="btn btn--primary"
                      disabled={busyId === review.review_id}
                      onClick={() => void handleApprove(review.review_id)}
                    >
                      {t("risk.approve")}
                    </button>
                    <button
                      type="button"
                      className="btn btn--secondary"
                      disabled={busyId === review.review_id}
                      onClick={() => void handleReject(review.review_id)}
                    >
                      {t("risk.reject")}
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
