"""
Stripe webhook → ενεργοποίηση/απενεργοποίηση πελάτη.

Standalone:  uvicorn src.stripe_webhook:app --port 8000
Production:  το router περιλαμβάνεται στο src/main.py (ένα app, ένα port).

Ροή: πελάτης πλήρωσε → webhook → status=active → cron αρχίζει να ποστάρει.
"""

import json
import uuid

import stripe
from fastapi import APIRouter, FastAPI, Request, HTTPException
from . import config as cfg
from .db import (
    get_domain_order_by_session,
    process_stripe_billing_event,
    update_domain_order_status,
)

stripe.api_key = cfg.STRIPE_SECRET_KEY

# Stripe price IDs από .env (βάλε τα πραγματικά από Dashboard → Products)
PLAN_BY_PRICE = {k: v for k, v in {
    cfg.STRIPE_PRICE_SITE: "site",
    cfg.STRIPE_PRICE_STARTER: "starter",
    cfg.STRIPE_PRICE_SOCIAL:  "social",
    cfg.STRIPE_PRICE_PREMIUM: "premium",
}.items() if k}

router = APIRouter()

_BILLING_EVENTS = {
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",
    "invoice.payment_failed",
}


def _first_price(obj: dict) -> str | None:
    items = ((obj.get("items") or {}).get("data") or [])
    if items:
        return ((items[0].get("price") or {}).get("id"))
    lines = ((obj.get("lines") or {}).get("data") or [])
    if not lines:
        return None
    line = lines[0]
    return ((line.get("price") or {}).get("id")
            or (((line.get("pricing") or {}).get("price_details") or {}).get("price")))


def _invoice_subscription(obj: dict) -> str | None:
    return (obj.get("subscription")
            or ((((obj.get("parent") or {}).get("subscription_details") or {})
                 .get("subscription"))))


def _subscription_period(obj: dict) -> tuple[int | None, int | None]:
    """Stripe Basil moved subscription periods from the subscription to items."""
    start = obj.get("current_period_start")
    end = obj.get("current_period_end")
    if start is not None or end is not None:
        return start, end
    items = ((obj.get("items") or {}).get("data") or [])
    if not items:
        return None, None
    return items[0].get("current_period_start"), items[0].get("current_period_end")


def _transition(event: dict, obj: dict) -> dict:
    event_type = event["type"]
    metadata = obj.get("metadata") or {}
    client_id = metadata.get("client_id")
    malformed_client = False
    if client_id:
        try:
            client_id = str(uuid.UUID(str(client_id)))
        except (ValueError, TypeError, AttributeError):
            client_id = None
            malformed_client = True
    payload = {
        "event_id": event["id"], "event_type": event_type,
        "event_created": event["created"],
        "client_id": client_id,
        "customer_id": obj.get("customer"),
        "subscription_id": obj.get("id") if event_type.startswith("customer.subscription.")
                           else _invoice_subscription(obj),
        "price_id": _first_price(obj),
    }
    if malformed_client:
        payload.update({
            "disposition": "ignored_malformed",
            "error_message": "metadata.client_id is not a UUID",
        })
    if event_type.startswith("customer.subscription."):
        period_start, period_end = _subscription_period(obj)
        payload.update({
            "status": "canceled" if event_type.endswith(".deleted") else obj.get("status"),
            "trial_start": obj.get("trial_start"), "trial_end": obj.get("trial_end"),
            "current_period_start": period_start,
            "current_period_end": period_end,
            "cancel_at_period_end": obj.get("cancel_at_period_end"),
            "canceled_at": obj.get("canceled_at"), "ended_at": obj.get("ended_at"),
            "latest_invoice_id": obj.get("latest_invoice"),
        })
    elif event_type.startswith("invoice."):
        period = ((obj.get("lines") or {}).get("data") or [{}])[0].get("period") or {}
        paid_trial_invoice = (
            event_type == "invoice.paid"
            and obj.get("billing_reason") == "subscription_create"
            and int(obj.get("amount_paid") or 0) == 0
        )
        payload.update({
            "status": ("trialing" if paid_trial_invoice else "active")
                      if event_type == "invoice.paid" else "past_due",
            "current_period_start": period.get("start"),
            "current_period_end": period.get("end"),
            "latest_invoice_id": obj.get("id"),
        })
    elif event_type == "checkout.session.completed":
        payload.update({
            "subscription_id": obj.get("subscription"),
            "customer_email": ((obj.get("customer_details") or {}).get("email")
                               or obj.get("customer_email")),
        })
    return payload


@router.post("/stripe/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        stripe.Webhook.construct_event(
            payload, sig, cfg.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(400, "invalid signature")

    # ΤΑ ΔΕΔΟΜΕΝΑ ΔΙΑΒΑΖΟΝΤΑΙ ΑΠΟ ΤΟ ΙΔΙΟ ΤΟ JSON, ΟΧΙ ΑΠΟ ΤΟ StripeObject.
    #
    # Μετρήθηκε: από το stripe-python 12 και μετά το `StripeObject` ΔΕΝ είναι
    # πια dict και δεν έχει `.get()`. Κάθε `obj.get("metadata", {})` πετούσε
    # `AttributeError: get` → HTTP 500 → το Stripe ξαναπροσπαθούσε και
    # ξανααποτύγχανε. Αποτέλεσμα: καμία συνδρομή νέου πελάτη δεν αποθηκευόταν
    # ποτέ και κανένα email δεν συνδεόταν — ο πελάτης πλήρωνε και δεν έμπαινε.
    # Το `requirements.txt` έλεγε `stripe>=8.0.0` χωρίς άνω όριο, οπότε κάθε
    # build της παραγωγής τραβούσε την έκδοση που το σπάει.
    #
    # Η υπογραφή επαληθεύεται ΠΑΝΤΑ από το Stripe (πάνω). Εδώ διαβάζουμε μόνο
    # το ήδη επαληθευμένο σώμα, σε καθαρά dict — ανεξάρτητα από έκδοση.
    event = json.loads(payload)
    t = event["type"]
    obj = event["data"]["object"]

    if t == "checkout.session.completed":
        metadata = obj.get("metadata", {}) or {}
        if metadata.get("kind") == "domain_purchase":
            session_id = obj["id"]
            order = get_domain_order_by_session(session_id)
            if not order or order.get("status") == "active":
                return {"ok": True}

            client_id = metadata.get("client_id") or order.get("client_id")
            domain = metadata.get("domain") or order.get("domain")
            pages_subdomain = metadata.get("pages_subdomain") or "vitrina-7uq.pages.dev"
            railway_url = metadata.get("railway_url") or "greek-smb-agent-production.up.railway.app"

            if not client_id or not domain:
                update_domain_order_status(session_id, "failed", "missing client_id/domain metadata")
                return {"ok": True}

            update_domain_order_status(session_id, "paid")
            try:
                # Χωρίς registrar API (dns/manual) η παραγγελία ΔΕΝ είναι failed —
                # είναι πληρωμένη και περιμένει χειροκίνητη αγορά (~3 λεπτά).
                if cfg.DOMAIN_REGISTRAR in ("manual", "dns", ""):
                    print(f"[domain] ⚠ ΠΛΗΡΩΜΕΝΗ ΠΑΡΑΓΓΕΛΙΑ — αγόρασε χειροκίνητα: {domain} "
                          f"(client {client_id}) και μετά: python scripts/link_domain.py {domain}")
                    update_domain_order_status(session_id, "pending_fulfillment")
                    return {"ok": True}
                if cfg.DOMAIN_REGISTRAR != "papaki":
                    raise RuntimeError(f"Unsupported DOMAIN_REGISTRAR: {cfg.DOMAIN_REGISTRAR}")
                from .domain import buy_and_setup
                buy_and_setup(
                    domain,
                    client_id,
                    pages_subdomain=pages_subdomain,
                    railway_url=railway_url,
                )
                update_domain_order_status(session_id, "active")
            except Exception as e:
                update_domain_order_status(session_id, "failed", str(e))

            return {"ok": True}

    if t in _BILLING_EVENTS:
        try:
            transition = _transition(event, obj)
        except (KeyError, TypeError, ValueError) as exc:
            transition = {
                "event_id": event.get("id") or "",
                "event_type": t,
                "event_created": event.get("created"),
                "disposition": "ignored_malformed",
                "error_message": str(exc),
            }
        result = process_stripe_billing_event(transition)
        if not result.get("ok"):
            raise HTTPException(500, "billing transition failed")
        return {"ok": True, "duplicate": bool(result.get("duplicate")),
                "status": result.get("status")}

    return {"ok": True}


# Standalone app (για local test ή αν θες ξεχωριστό process)
app = FastAPI()
app.include_router(router)
