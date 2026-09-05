"""Stripe-derived billing policy and fail-closed configuration checks."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import stripe

from . import config as cfg
from . import env

TRIAL_DAYS = 30
PAST_DUE_GRACE_DAYS = 7
SITE_AMOUNT_CENTS = 1499
SITE_CURRENCY = "eur"
SITE_INTERVAL = "month"

FULL_ACCESS = frozenset(("trialing", "active"))
NO_ACCESS = frozenset(("unpaid", "incomplete", "incomplete_expired", "paused"))
KNOWN_STATUSES = FULL_ACCESS | NO_ACCESS | frozenset(("past_due", "canceled"))


def _utc(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def effective_end(subscription: dict) -> datetime | None:
    ended_at = _utc(subscription.get("ended_at"))
    if ended_at is not None:
        return ended_at
    candidates = [_utc(subscription.get(k)) for k in
                  ("trial_end", "current_period_end")]
    return max((v for v in candidates if v is not None), default=None)


def entitlement(subscription: dict | None, *, now: datetime | None = None) -> dict:
    """Pure policy decision. It never mutates, deletes or unpublishes data."""
    now = now or datetime.now(timezone.utc)
    sub = subscription or {}
    status = str(sub.get("status") or "").lower()
    end = effective_end(sub)
    entitled = status in FULL_ACCESS
    reason = status or "missing_subscription"

    if status == "past_due":
        failed = _utc(sub.get("first_payment_failed_at"))
        grace_end = failed + timedelta(days=PAST_DUE_GRACE_DAYS) if failed else None
        entitled = bool(grace_end and now < grace_end)
        end = grace_end
        reason = "past_due_grace" if entitled else "past_due_grace_expired"
    elif status == "canceled":
        entitled = bool(end and now < end)
        reason = "canceled_access_remaining" if entitled else "canceled_effective"
    elif status not in FULL_ACCESS:
        entitled = False

    return {
        "entitled": entitled,
        "status": status or None,
        "reason": reason,
        "access_until": end.isoformat() if end else None,
        "data_preserved": True,
        "recovery_required": status in {"past_due", "unpaid", "incomplete"},
    }


def validate_runtime_configuration(*, retrieve_price: bool = False) -> dict:
    """Reject mixed/ambiguous Stripe mode and optionally verify the Price."""
    expected = env.stripe_mode()
    key = cfg.STRIPE_SECRET_KEY
    webhook = cfg.STRIPE_WEBHOOK_SECRET
    price_id = cfg.STRIPE_PRICE_SITE
    prefix = "sk_live_" if expected == "live" else "sk_test_"
    if not key.startswith(prefix):
        raise RuntimeError(f"Stripe {expected} environment requires a {prefix} key")
    if not webhook.startswith("whsec_"):
        raise RuntimeError("Stripe webhook secret is missing or invalid")
    if not price_id.startswith("price_"):
        raise RuntimeError("Stripe site Price ID is missing or invalid")

    stripe.api_key = key
    result = {"mode": expected, "price_id": price_id}
    if retrieve_price:
        price = stripe.Price.retrieve(price_id, expand=["product"])
        if hasattr(price, "to_dict"):
            price_data = price.to_dict()
        elif isinstance(price, dict):
            price_data = price
        else:
            raise RuntimeError("Stripe Price response has an unsupported shape")
        recurring = price_data.get("recurring") or {}
        if bool(price_data.get("livemode")) != (expected == "live"):
            raise RuntimeError("Stripe Price mode does not match the environment")
        if price_data.get("currency") != SITE_CURRENCY:
            raise RuntimeError("Stripe Price must use EUR")
        if price_data.get("unit_amount") != SITE_AMOUNT_CENTS:
            raise RuntimeError("Stripe Price must be EUR 14.99")
        if recurring.get("interval") != SITE_INTERVAL or recurring.get("interval_count", 1) != 1:
            raise RuntimeError("Stripe Price must recur monthly")
        if not price_data.get("active"):
            raise RuntimeError("Stripe Price is inactive")
        result.update({"amount_cents": price_data["unit_amount"],
                       "currency": price_data["currency"],
                       "interval": recurring["interval"],
                       "livemode": price_data["livemode"]})
    return result
