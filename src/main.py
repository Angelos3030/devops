"""
Production entry point — ένα FastAPI app, ένα port.
Τρέξε: uvicorn src.main:app --host 0.0.0.0 --port $PORT

Περιλαμβάνει:
  - /onboard, /connect/start, /connect/callback, /create-checkout  (meta_oauth)
  - /stripe/webhook                                                 (stripe_webhook)
  - /domain/suggest, /domain/check, /domain/purchase               (domain)
  - GET /healthz                                                    (liveness probe)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from .meta_oauth import app as _meta_app
from .stripe_webhook import router as stripe_router
from . import domain as dom
from .db import save_domain, upload_to_storage, save_client_asset

app = _meta_app
app.include_router(stripe_router)


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


@app.post("/domain/suggest")
def domain_suggest(req: DomainSuggestRequest):
    """Επιστρέφει 6-8 έξυπνες προτάσεις domain slug βάσει ονόματος/τύπου/πόλης."""
    slugs = dom.suggest_domains(req.name, req.business_type, req.city)
    return {"slugs": slugs, "tld": ".gr",
            "domains": [f"{s}.gr" for s in slugs]}


@app.post("/domain/check")
def domain_check(req: DomainCheckRequest):
    """Ελέγχει διαθεσιμότητα domain μέσω Cloudflare Registrar API."""
    try:
        results = dom.check_availability(req.slugs, req.tld)
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    return {"results": results}


@app.post("/domain/purchase")
def domain_purchase(req: DomainPurchaseRequest):
    """
    Αγοράζει domain, φτιάχνει Cloudflare zone, DNS records, ενημερώνει nameservers.
    Επιστρέφει nameservers για επιβεβαίωση.
    """
    try:
        result = dom.buy_and_setup(
            req.domain, req.client_id,
            pages_subdomain=req.pages_subdomain,
            railway_url=req.railway_url,
        )
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    return result


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
    return {"ok": True}
