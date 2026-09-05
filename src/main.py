"""
Production entry point — ένα FastAPI app, ένα port.
Τρέξε: uvicorn src.main:app --host 0.0.0.0 --port $PORT

Περιλαμβάνει:
  - /onboard, /connect/start, /connect/callback, /create-checkout  (meta_oauth)
  - /stripe/webhook                                                 (stripe_webhook)
  - /domain/suggest, /domain/check, /domain/create-checkout        (domain)
  - GET /healthz                                                    (liveness probe)
"""

import hashlib
import re

import stripe
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header
from pydantic import BaseModel

from .meta_oauth import app as _meta_app
from .stripe_webhook import router as stripe_router
from .agency_api import router as agency_router
from .logo_designer import router as logo_designer_router
from . import domain as dom
from . import config as cfg
from . import auth, db
from .db import save_domain, upload_to_storage, save_client_asset

app = _meta_app
app.include_router(stripe_router)
app.include_router(agency_router)
app.include_router(logo_designer_router)
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
    """Διαθεσιμότητα από ΑΥΘΕΝΤΙΚΗ πηγή (RDAP ή registrar) — ποτέ από DNS.

    Τρία αποτελέσματα: `available`, `unavailable`, `unknown`. Το `unknown`
    είναι πλήρης απάντηση: σημαίνει «δεν ξέρουμε», και το UI ΔΕΝ επιτρέπεται
    να το παρουσιάσει ως ελεύθερο. Αποτυχία παρόχου δεν γίνεται ποτέ
    «διαθέσιμο» — αυτό ακριβώς έκανε ο παλιός DNS έλεγχος.
    """
    from . import domain_availability as availability
    names = [f"{s}{req.tld}" if not str(s).endswith(req.tld) else str(s)
             for s in req.slugs]
    results = []
    for item in availability.check_many(names):
        results.append(item.as_dict() if hasattr(item, "as_dict") else item)
    return {"results": results}


class DomainRequestBody(BaseModel):
    client_id: str
    domain: str
    claim_token: str = ""


@app.post("/domain/request")
def domain_request(req: DomainRequestBody,
                   authorization: str | None = Header(default=None)):
    """Ο πελάτης ζητά domain. ΔΕΝ αγοράζεται τίποτα εδώ.

    Δημιουργείται παραγγελία σε `pending_fulfillment` με αποθηκευμένο το
    αποτέλεσμα διαθεσιμότητας ΚΑΙ τη στιγμή του. Την αγορά την κάνει άνθρωπος,
    αφού ΞΑΝΑΕΛΕΓΞΕΙ — η διαθεσιμότητα αλλάζει.
    """
    from . import auth as _auth
    from . import db
    from . import domain_availability as availability

    # Το funnel είναι site-first: μπορεί να μην υπάρχει ακόμα λογαριασμός.
    # Ο κάτοχος ΤΑΥΤΟΠΟΙΕΙΤΑΙ πάντα — είτε με σύνδεση είτε με claim token.
    _auth.require_client_or_claim(req.client_id, authorization, req.claim_token)

    try:
        result = availability.check(req.domain)
    except availability.InvalidDomain as e:
        raise HTTPException(400, str(e))

    if result.status == availability.UNAVAILABLE:
        raise HTTPException(409, f"Το {result.display} είναι ήδη κατοχυρωμένο.")
    if result.status == availability.UNKNOWN:
        # Δεν μπλοκάρουμε τον πελάτη επειδή δεν απάντησε ο πάροχος, αλλά
        # καταγράφουμε ρητά ότι ΔΕΝ επιβεβαιώθηκε. Ο operator θα το δει.
        print(f"[domain] αίτημα χωρίς επιβεβαίωση διαθεσιμότητας: "
              f"{result.domain} ({result.reason})")

    order = db.create_domain_request(req.client_id, result.domain,
                                     result.as_dict())
    return {
        "order_id": order["id"],
        "domain": result.domain,
        "display": result.display,
        "status": order["status"],
        "availability": result.as_dict(),
        "message": ("Το αίτημα καταγράφηκε. Θα ελέγξουμε ξανά τη διαθεσιμότητα "
                    "και θα το κατοχυρώσουμε — θα ενημερωθείς μόλις γίνει."),
    }


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
    # Τι ΔΕΙΧΝΕΙ η φωτογραφία, δηλωμένο από τον πελάτη. Δεν το συμπεραίνουμε:
    # μοντέλο που μαντεύει «αυτό είναι ο χώρος σου» δημοσιεύει τον ισχυρισμό.
    media_class: str = Form(""),       # REAL_WORK | REAL_SPACE | REAL_OWNER_PERSON | REAL_BUSINESS
    rights_ok: bool = Form(True),
    claim_token: str = Form(""),
    authorization: str | None = Header(default=None),
):
    """
    Δέχεται αρχείο (εικόνα συμπιεσμένη από frontend), ανεβάζει στο Supabase Storage,
    και αποθηκεύει URL στη client_assets. Επιστρέφει {"url", "asset_id"}.

    Supabase Storage bucket: 'client-assets' (πρέπει να το δημιουργήσεις χειροκίνητα:
    Dashboard → Storage → New bucket → Name: client-assets → Public: ON).
    """
    _require_upload_access(client_id, authorization, claim_token)

    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(400, f"Μη επιτρεπτός τύπος: {file.content_type}")
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(400, "Μέγιστο μέγεθος: 10MB")

    data = await file.read()
    # ΑΔΕΙΟ Ή ΚΟΛΟΒΟ ΑΡΧΕΙΟ. Το ανέβασμα πετύχαινε με 0 bytes και η εικόνα
    # κατέληγε ΣΠΑΣΜΕΝΗ στο δημόσιο site του πελάτη — φάνηκε σε έλεγχο
    # κινητού, όχι στο ανέβασμα.
    #
    # Το όριο είναι 24 bytes, όχι 100: ένα έγκυρο PNG 1×1 είναι περίπου 70
    # bytes και το πρώτο κατώφλι που δοκίμασα το απέρριπτε. Την πραγματική
    # δουλειά την κάνει ο έλεγχος υπογραφής από κάτω· εδώ κόβεται μόνο ό,τι
    # δεν χωράει ούτε επικεφαλίδα.
    if len(data) < 24:
        raise HTTPException(400, "Το αρχείο είναι άδειο ή κατεστραμμένο.")
    # Η υπογραφή πρέπει να συμφωνεί με τον δηλωμένο τύπο: ένα .png που δεν
    # ξεκινά με PNG magic bytes δεν είναι png, ό,τι κι αν λέει ο browser.
    _SIG = ((b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg"),
            (b"GIF8", "image/gif"), (b"RIFF", "image/webp"))
    if not any(data.startswith(sig) for sig, _ in _SIG):
        raise HTTPException(400, "Το αρχείο δεν είναι έγκυρη εικόνα.")
    try:
        url = upload_to_storage(client_id, f"{asset_type}-{file.filename}", data,
                                file.content_type)
    except Exception as e:
        raise HTTPException(502, f"Storage upload απέτυχε: {e}")

    from .media_semantics import CLASSES, REAL_BUSINESS
    declared = media_class if media_class in CLASSES else (REAL_BUSINESS if asset_type == "photo" else None)
    asset_id = save_client_asset(client_id, {
        "type": asset_type,
        "url": url,
        "title": file.filename,
        "usage": "site",
        "rights_ok": rights_ok,
        "media_class": declared,
    })
    return {"url": url, "asset_id": asset_id}


def _require_upload_access(client_id: str, authorization: str | None,
                           claim_token: str) -> None:
    """Allow an authenticated owner or the short-lived onboarding owner token."""
    if authorization:
        auth.require_client_access(client_id, authorization)
        return
    if len(claim_token or "") < 32:
        raise HTTPException(401, "Χρειάζεται σύνδεση για την αποστολή αρχείων.")
    token_hash = hashlib.sha256(claim_token.encode()).hexdigest()
    if not db.valid_client_claim(client_id, token_hash):
        raise HTTPException(401, "Ο σύνδεσμος αποστολής έληξε ή δεν είναι έγκυρος.")


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
