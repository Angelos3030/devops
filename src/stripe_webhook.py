"""
Stripe webhook → ενεργοποίηση/απενεργοποίηση πελάτη.

Standalone:  uvicorn src.stripe_webhook:app --port 8000
Production:  το router περιλαμβάνεται στο src/main.py (ένα app, ένα port).

Ροή: πελάτης πλήρωσε → webhook → status=active → cron αρχίζει να ποστάρει.
"""

import stripe
from fastapi import APIRouter, FastAPI, Request, HTTPException
from . import config as cfg
from .db import get_client_by_stripe, set_client_status, upsert_subscription

stripe.api_key = cfg.STRIPE_SECRET_KEY

# Stripe price IDs από .env (βάλε τα πραγματικά από Dashboard → Products)
PLAN_BY_PRICE = {k: v for k, v in {
    cfg.STRIPE_PRICE_STARTER: "starter",
    cfg.STRIPE_PRICE_SOCIAL:  "social",
    cfg.STRIPE_PRICE_PREMIUM: "premium",
}.items() if k}

router = APIRouter()


@router.post("/stripe/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, cfg.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(400, "invalid signature")

    t = event["type"]
    obj = event["data"]["object"]

    if t in ("customer.subscription.created", "customer.subscription.updated"):
        cust = obj["customer"]
        sub_status = obj["status"]
        price = obj["items"]["data"][0]["price"]["id"]
        plan = PLAN_BY_PRICE.get(price, "starter")
        new_status = "active" if sub_status in ("active", "trialing") else "paused"

        row = get_client_by_stripe(cust)
        if not row:
            # Πρώτη εγγραφή: client_id από Stripe subscription metadata
            client_id = obj.get("metadata", {}).get("client_id")
            if not client_id:
                return {"ok": True}
            upsert_subscription(client_id, cust, obj["id"], plan, sub_status)
            row = {"client_id": client_id}

        set_client_status(row["client_id"], new_status, plan=plan)

    elif t == "customer.subscription.deleted":
        row = get_client_by_stripe(obj["customer"])
        if row:
            set_client_status(row["client_id"], "cancelled")

    return {"ok": True}


# Standalone app (για local test ή αν θες ξεχωριστό process)
app = FastAPI()
app.include_router(router)
