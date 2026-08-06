"""
Production entry point — ένα FastAPI app, ένα port.
Τρέξε: uvicorn src.main:app --host 0.0.0.0 --port $PORT

Περιλαμβάνει:
  - /onboard, /connect/start, /connect/callback, /create-checkout  (meta_oauth)
  - /stripe/webhook                                                 (stripe_webhook)
  - /domain/suggest, /domain/check, /domain/create-checkout        (domain)
  - GET /healthz                                                    (liveness probe)
"""

import re

import stripe
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from .meta_oauth import app as _meta_app
from .stripe_webhook import router as stripe_router
from . import domain as dom
from . import config as cfg
from .db import save_domain, upload_to_storage, save_client_asset

app = _meta_app
app.include_router(stripe_router)
stripe.api_key = cfg.STRIPE_SECRET_KEY


# ---------------------------------------------------------------------------
# Domain endpoints
# ---------------------------------------------------------------------------

class DomainSuggestRequest(BaseModel):
    name: str
    business_type: str = ""
    city: str = ""


class DomainCheckRequest(BaseModel):
    slugs: list[str]
    tld: str = ".gr"


class DomainPurchaseRequest(BaseModel):
    client_id: str
    domain: str                         # πλήρες, π.χ. "mitsos-taverna.gr"
    pages_subdomain: str = "vitrina-7uq.pages.dev"
    railway_url: str = "greek-smb-agent-production.up.railway.app"
    admin_token: str | None = None


class DomainCheckoutRequest(BaseModel):
    client_id: str
    domain: str
    pages_subdomain: str = "vitrina-7uq.pages.dev"
    railway_url: str = "greek-smb-agent-production.up.railway.app"


@app.post("/domain/suggest")
def domain_suggest(req: DomainSuggestRequest):
    """Επιστρέφει 6-8 έξυπνες προτάσεις domain slug βάσει ονόματος/τύπου/πόλης."""
    slugs = dom.suggest_domains(req.name, req.business_type, req.city)
    return {"slugs": slugs, "tld": ".gr",
            "domains": [f"{s}.gr" for s in slugs]}


@app.post("/domain/check")
def domain_check(req: DomainCheckRequest):
    """Ελέγχει διαθεσιμότητα domain μέσω του configured registrar adapter."""
    try:
        results = dom.check_availability(req.slugs, req.tld)
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    return {"results": results}


@app.post("/domain/create-checkout")
def domain_create_checkout(req: DomainCheckoutRequest):
    """One-time Stripe Checkout για αγορά/ρύθμιση domain μετά από user approval."""
    if not cfg.STRIPE_SECRET_KEY:
        raise HTTPException(500, "Λείπει STRIPE_SECRET_KEY.")
    if not _is_valid_gr_domain(req.domain):
        raise HTTPException(400, "Το domain πρέπει να είναι έγκυρο .gr domain.")

    try:
        from . import db
        order_id = db.create_domain_order(req.client_id, req.domain)
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "unit_amount": 2400,
                    "product_data": {
                        "name": f"Domain {req.domain}",
                        "description": "Ετήσια αγορά/κράτηση .gr domain και αυτόματη σύνδεση με Vitrina.",
                    },
                },
                "quantity": 1,
            }],
            metadata={
                "kind": "domain_purchase",
                "order_id": order_id,
                "client_id": req.client_id,
                "domain": req.domain,
                "pages_subdomain": req.pages_subdomain,
                "railway_url": req.railway_url,
            },
            payment_intent_data={"metadata": {
                "kind": "domain_purchase",
                "order_id": order_id,
                "client_id": req.client_id,
                "domain": req.domain,
            }},
            success_url=(
                "https://getvitrina.gr/connect.html"
                f"?step=domain_success&client_id={req.client_id}&domain={req.domain}"
            ),
            cancel_url=(
                "https://getvitrina.gr/connect.html"
                f"?step=domain_cancel&client_id={req.client_id}&domain={req.domain}"
            ),
        )
        db.set_domain_order_checkout(order_id, session.id)
    except Exception as e:
        raise HTTPException(502, f"Δεν δημιουργήθηκε checkout για domain: {e}")
    return {"checkout_url": session.url, "amount_cents": 2400, "currency": "eur"}


@app.post("/domain/purchase")
def domain_purchase(req: DomainPurchaseRequest):
    """
    Internal/admin fallback. Το δημόσιο flow πρέπει να περνάει από /domain/create-checkout.
    """
    expected = getattr(cfg, "DOMAIN_ADMIN_TOKEN", "")
    if not expected or req.admin_token != expected:
        raise HTTPException(403, "Χρησιμοποίησε /domain/create-checkout ώστε να προηγηθεί πληρωμή.")
    try:
        result = dom.buy_and_setup(
            req.domain, req.client_id,
            pages_subdomain=req.pages_subdomain,
            railway_url=req.railway_url,
        )
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    return result


def _is_valid_gr_domain(domain: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]\.gr", domain.lower()))


@app.post("/clients/{client_id}/upload")
async def upload_asset(
    client_id: str,
    file: UploadFile = File(...),
    asset_type: str = Form("photo"),   # logo | photo | menu | other
    rights_ok: bool = Form(True),
):
    """
    Δέχεται αρχείο (εικόνα συμπιεσμένη από frontend), ανεβάζει στο Supabase Storage,
    και αποθηκεύει URL στη client_assets. Επιστρέφει {"url", "asset_id"}.

    Supabase Storage bucket: 'client-assets' (πρέπει να το δημιουργήσεις χειροκίνητα:
    Dashboard → Storage → New bucket → Name: client-assets → Public: ON).
    """
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(400, f"Μη επιτρεπτός τύπος: {file.content_type}")
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(400, "Μέγιστο μέγεθος: 10MB")

    data = await file.read()
    try:
        url = upload_to_storage(client_id, f"{asset_type}-{file.filename}", data,
                                file.content_type)
    except Exception as e:
        raise HTTPException(502, f"Storage upload απέτυχε: {e}")

    asset_id = save_client_asset(client_id, {
        "type": asset_type,
        "url": url,
        "title": file.filename,
        "usage": "site",
        "rights_ok": rights_ok,
    })
    return {"url": url, "asset_id": asset_id}


@app.get("/healthz")
def healthz():
    from . import ai
    return {
        "ok": True,
        "ai": {
            "configured": ai.available(),
            "provider": ai.provider() or None,
            "model": ai.model() if ai.available() else None,
            "key_type": "anthropic" if cfg.AI_API_KEY.startswith("sk-ant-") else "other",
            "last_error": ai.LAST_ERROR,
        },
    }
