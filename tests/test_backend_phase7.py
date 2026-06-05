from backend.services.jobs import get_job_detail, list_jobs
from backend.services.review import approve_review, get_review_detail, list_review_queue, reject_review


def test_review_queue_fallback_contains_pending_human_confirmation_item():
    payload = list_review_queue()

    assert payload["source"] == "fallback_review_queue"
    assert payload["reviews"][0]["status"] == "pending"
    assert payload["reviews"][0]["human_confirmation_required"] is True
    assert "audit_log" in payload["reviews"][0]["required_gates"]


def test_review_detail_returns_fallback_item():
    payload = get_review_detail("review-demo-001")

    assert payload["review"]["review_id"] == "review-demo-001"
    assert payload["review"]["metric_family"] == "oos"


def test_approve_and_reject_review_are_audit_friendly():
    approved = approve_review("review-demo-001", reviewer="reviewer")
    rejected = reject_review("review-demo-001", reviewer="reviewer", reason="Needs more OOS evidence.")

    assert approved["status"] == "approved"
    assert approved["audit_event"]["event_type"] == "review.approved"
    assert rejected["status"] == "rejected"
    assert rejected["audit_event"]["event_type"] == "review.rejected"
    assert rejected["reason"] == "Needs more OOS evidence."


def test_jobs_fallback_contains_artifact_export_job():
    payload = list_jobs()

    assert payload["source"] == "fallback_jobs"
    assert payload["jobs"][0]["type"] == "artifact_export"
    assert payload["jobs"][0]["status"] in {"queued", "completed"}


def test_job_detail_returns_events():
    payload = get_job_detail("job-demo-001")

    assert payload["job"]["job_id"] == "job-demo-001"
    assert payload["events"]
