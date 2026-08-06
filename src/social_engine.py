"""Approval-first queue and worker for Vitrina social publishing."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from . import db, publisher

ALLOWED_TARGETS = {"facebook", "instagram"}


def clean_targets(targets: list[str] | None) -> list[str]:
    cleaned = list(dict.fromkeys(targets or ["facebook", "instagram"]))
    if not cleaned or any(target not in ALLOWED_TARGETS for target in cleaned):
        raise ValueError("Τα δίκτυα πρέπει να είναι facebook και/ή instagram.")
    return cleaned


def create_draft(client_id: str, caption: str, *, image_url: str | None = None,
                 targets: list[str] | None = None,
                 scheduled_for: str | None = None) -> str:
    if not caption.strip():
        raise ValueError("Το κείμενο της δημοσίευσης είναι κενό.")
    return db.save_post(
        client_id, caption.strip(), status="pending_approval", image_url=image_url,
        targets=clean_targets(targets), scheduled_for=scheduled_for,
        approval_required=True,
    )


def _target_succeeded(result: dict[str, Any]) -> bool:
    return bool(result.get("ok") or result.get("dry_run"))


def _result_ids(results: dict[str, Any], post: dict) -> tuple[str | None, str | None]:
    facebook = results.get("facebook") or {}
    instagram = results.get("instagram") or {}
    return (
        facebook.get("post_id") or post.get("fb_post_id"),
        instagram.get("media_id") or post.get("ig_post_id"),
    )


def process_post(post: dict, *, dry_run: bool = False) -> dict[str, Any]:
    """Publish one claimed row, retaining per-network progress for safe retries."""
    if post.get("approval_required", True) and not post.get("approved_at"):
        error = "Η δημοσίευση μπλοκαρίστηκε επειδή δεν υπάρχει καταγεγραμμένη έγκριση."
        db.finish_post(post["id"], status="pending_approval",
                       attempts=int(post.get("attempts") or 0), error=error)
        return {"ok": False, "blocked": "approval_required", "error": error}

    requested = clean_targets(post.get("targets"))
    remaining = [
        target for target in requested
        if not (target == "facebook" and post.get("fb_post_id"))
        and not (target == "instagram" and post.get("ig_post_id"))
    ]
    if not remaining:
        db.finish_post(post["id"], status="published", attempts=post.get("attempts", 0))
        return {"ok": True, "already_published": True, "results": {}}

    try:
        outcome = publisher.publish(
            post["client_id"], post.get("caption") or "", post.get("image_url"),
            remaining, dry_run,
        )
    except Exception as exc:  # publisher/network failure before per-target results
        outcome = {"dry_run": dry_run, "results": {}, "error": str(exc)}

    results = outcome.get("results") or {}
    errors = {
        target: (results.get(target) or {}).get("error", "Δεν επιστράφηκε αποτέλεσμα.")
        for target in remaining if not _target_succeeded(results.get(target) or {})
    }
    fb_id, ig_id = _result_ids(results, post)
    success = not errors and not outcome.get("error")
    error = outcome.get("error") or ("; ".join(f"{k}: {v}" for k, v in errors.items()) or None)
    db.save_publish_log(
        post["id"], post["client_id"], dry_run=dry_run,
        success=success, result=outcome, error=error,
    )

    if dry_run:
        db.finish_post(post["id"], status="scheduled", attempts=post.get("attempts", 0),
                       error=error)
        return {"ok": success, **outcome}

    attempts = int(post.get("attempts") or 0) + 1
    if success:
        db.finish_post(post["id"], status="published", attempts=attempts,
                       fb_post_id=fb_id, ig_post_id=ig_id)
    else:
        max_attempts = int(post.get("max_attempts") or 3)
        retry = attempts < max_attempts
        next_try = (datetime.now(timezone.utc) + timedelta(minutes=5 * attempts)).isoformat()
        db.finish_post(
            post["id"], status="scheduled" if retry else "failed", attempts=attempts,
            fb_post_id=fb_id, ig_post_id=ig_id, error=error,
            scheduled_for=next_try if retry else None,
        )
    return {"ok": success, **outcome}


def run_due(*, limit: int = 25, dry_run: bool = False) -> dict[str, int]:
    summary = {"due": 0, "claimed": 0, "published": 0, "failed": 0}
    for candidate in db.due_posts(limit):
        summary["due"] += 1
        post = db.claim_post(candidate["id"])
        if not post:
            continue
        summary["claimed"] += 1
        result = process_post(post, dry_run=dry_run)
        summary["published" if result.get("ok") else "failed"] += 1
    return summary
