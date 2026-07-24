"""
Meta OAuth flow — «Σύνδεση με Facebook» → Page token + IG Business id.

FastAPI app. Τρέξε: uvicorn src.meta_oauth:app --port 8001

Ροή:
  1. /connect/start   → redirect στο Facebook OAuth dialog (εδώ φαίνεται η συγκατάθεση)
  2. /connect/callback→ code → short-lived token → long-lived → pages + IG → αποθήκευση

⚠️ Σημειώσεις:
  - Σε DEV mode δουλεύει μόνο για testers/admins της app (αρκεί για το screencast).
  - Τα tokens είναι ΕΥΑΙΣΘΗΤΑ — αποθήκευσε κρυπτογραφημένα (εδώ απλό για MVP).
  - Το `redirect_uri` πρέπει να είναι ΑΚΡΙΒΩΣ ίδιο και στο App settings (Valid OAuth URIs).
"""

import urllib.parse
import requests
import stripe
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from . import config as cfg
from . import db

stripe.api_key = cfg.STRIPE_SECRET_KEY

# Stripe price IDs — βάλε τα πραγματικά στο .env από Dashboard → Products.
_PRICE_BY_PLAN = {
    "site": cfg.STRIPE_PRICE_SITE,        # MVP: Website only, €14.99/μήνα
    "starter": cfg.STRIPE_PRICE_STARTER,
    "social": cfg.STRIPE_PRICE_SOCIAL,
    "premium": cfg.STRIPE_PRICE_PREMIUM,
}

app = FastAPI()

# CORS — ώστε το landing/connect (getvitrina.gr) να καλεί το API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://getvitrina.gr",
        "https://www.getvitrina.gr",
        "https://vitrina-7uq.pages.dev",
        "https://db65ba76.vitrina-7uq.pages.dev",
        "https://app.getvitrina.gr",
        "http://localhost:8001",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"], allow_headers=["*"],
)


class Intake(BaseModel):
    name: str
    type: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None
    style: str | None = None
    description: str | None = None


class CheckoutRequest(BaseModel):
    client_id: str
    plan: str = "site"   # MVP default: Website only, €14.99/μήνα


class ClientAsset(BaseModel):
    type: str = "other"
    title: str | None = None
    content: str | None = None
    url: str | None = None
    usage: str = "site"
    rights_ok: bool = False


@app.post("/create-checkout")
def create_checkout(req: CheckoutRequest):
    """Δημιουργεί Stripe Checkout URL. Βάζει client_id σε metadata για το webhook."""
    price_id = _PRICE_BY_PLAN.get(req.plan)
    if not price_id:
        raise HTTPException(400, f"Άγνωστο plan ή λείπει Stripe price id: {req.plan}")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        subscription_data={"metadata": {"client_id": req.client_id}},
        success_url="https://getvitrina.gr/connect.html?step=success",
        cancel_url="https://getvitrina.gr/connect.html?step=cancel",
    )
    return {"checkout_url": session.url}


_PHOTO_TYPES = {"photo", "gallery", "image", "work", "project"}


def _enrich_intake(client_id: str, form: dict) -> dict:
    """Χτίζει πλήρες intake για τον generator: στοιχεία φόρμας + uploaded assets
    (φωτογραφίες → gallery, υπηρεσίες, tagline). Best-effort ανά asset source."""
    intake = dict(form)
    intake.setdefault("tagline", form.get("style") or "")
    try:
        assets = db.get_client_assets(client_id, usage="site")
    except Exception:
        assets = []
    gallery, services = [], []
    for a in assets:
        atype = (a.get("type") or "").lower()
        url = a.get("url")
        if atype in _PHOTO_TYPES and url:
            gallery.append({"image": url, "title": a.get("title") or "Έργο"})
        elif atype == "service":
            services.append({"name": a.get("title") or "Υπηρεσία",
                             "description": a.get("content") or ""})
        elif atype == "logo" and url:
            intake["logo"] = url
    if gallery:
        intake["gallery"] = gallery
    if services:
        intake["services"] = services
    return intake


def _build_site_bg(client_id: str, form: dict) -> None:
    """Τρέχει στο background: παράγει 3 premium designs (studio/commerce/atelier)
    ντετερμινιστικά (0 API tokens) και τα αποθηκεύει ως previews για έγκριση.
    Best-effort — αν λείπει DB, απλώς το logάρει."""
    try:
        from . import premium_generator as pg
        from . import site_copy
        intake = _enrich_intake(client_id, form)
        intake = site_copy.enrich_with_copy(intake)  # AI copy if key present, else no-op
        recommended = pg.recommend_layout(intake)
        variants = pg.generate_variants(intake)
        for layout, html in variants.items():
            try:
                db.save_site_variant(client_id, layout, html,
                                     recommended=(layout == recommended))
            except Exception as e:
                print(f"[onboard bg] save variant {layout} failed: {e}")
        print(f"[onboard bg] 3 designs έτοιμα για {client_id} (recommended={recommended})")
    except Exception as e:
        print(f"[onboard bg] site building failed for {client_id}: {e}")


@app.post("/onboard")
def onboard_endpoint(intake: Intake, bg: BackgroundTasks):
    """Δημιουργεί πελάτη από τη φόρμα (connect.html) και επιστρέφει client_id.
    Το βαρύ site-building τρέχει στο background ώστε το UI να προχωρά αμέσως."""
    data = intake.model_dump()
    try:
        client_id = db.create_client(data)
    except Exception as e:
        raise HTTPException(500, f"Δεν μπόρεσα να αποθηκεύσω τον πελάτη: {e}")
    bg.add_task(_build_site_bg, client_id, data)
    return {"client_id": client_id}


class SelectDesign(BaseModel):
    layout: str


def _client_slug(client_id: str) -> str:
    """Ασφαλές Cloudflare Pages project slug από το client_id."""
    import re as _re
    return "c" + _re.sub(r"[^a-z0-9]", "", client_id.lower())[:16]


def _deploy_selected_bg(client_id: str, layout: str) -> None:
    """Μετά το Approve: deploy του επιλεγμένου HTML σε Cloudflare Pages (best-effort)."""
    try:
        from . import deploy
        variant = db.get_site_variant(client_id, layout)
        if not variant:
            print(f"[deploy] δεν βρέθηκε variant {layout} για {client_id}")
            return
        url = deploy.deploy_site(_client_slug(client_id), variant["html"])
        db.save_site(client_id, url=url, preset=layout, variant=0, html=variant["html"])
        print(f"[deploy] {client_id} → {url}")
    except Exception as e:
        print(f"[deploy] deploy skipped/failed for {client_id}: {e}")


def _resolve_client(client_id: str) -> dict:
    """Client record από uuid Ή custom domain. Domain-first ώστε να ΜΗΝ περάσει ποτέ
    domain string στη uuid-typed `clients.id` (θα έσκαγε με 500 invalid-uuid)."""
    if "." in str(client_id):
        return db.get_client_by_domain(client_id) or {}
    return db.get_client(client_id) or {}


def _intake_from_db(client_id: str) -> dict:
    """Ανακατασκευάζει intake από το client record + assets (για Next.js render).
    Το `client_id` μπορεί να είναι uuid Ή custom domain (multi-tenant routing)."""
    c = _resolve_client(client_id)
    client_id = c.get("id", client_id)
    intake = {
        "name": c.get("name"), "type": c.get("business_type"),
        "city": c.get("city"), "phone": c.get("phone"), "email": c.get("email"),
        "tagline": c.get("style") or "",
    }
    return _enrich_intake(client_id, intake)


@app.get("/clients/{client_id}/site-data")
def site_data(client_id: str, layout: str = ""):
    """Δομημένα data του site (JSON) για το Next.js multi-tenant render.
    Επιστρέφει normalized context (name, services[], gallery[], story[]...) + layout."""
    import html as _html
    from . import premium_generator as pg
    rid = _resolve_client(client_id).get("id", client_id)  # uuid (domain → uuid) για downstream queries
    intake = _intake_from_db(client_id)
    ctx = pg.normalize(intake)
    chosen = layout if layout in pg.LAYOUTS else (db.get_selected_design(rid) or ctx["_recommended"])

    # normalize() html-escapes για τα static HTML templates· το React κάνει το δικό του escaping,
    # οπότε για το JSON επιστρέφουμε RAW κείμενο (αλλιώς φαίνεται διπλό escape: "&amp;").
    def _unesc(v):
        if isinstance(v, str):
            return _html.unescape(v)
        if isinstance(v, list):
            return [_unesc(x) for x in v]
        if isinstance(v, dict):
            return {k: _unesc(x) for k, x in v.items()}
        return v

    data = {k: _unesc(v) for k, v in ctx.items() if not k.startswith("_")}
    return {"layout": chosen, "layouts": list(pg.LAYOUTS), "data": data}


@app.get("/clients/lookup")
def lookup_clients(email: str):
    """Βρίσκει τους πελάτες ενός email (dashboard login → client records).
    MVP: απλό lookup. Phase 2: επαλήθευση Supabase JWT αντί για raw email."""
    return {"clients": db.get_clients_by_email(email)}


@app.get("/clients/{client_id}/designs")
def list_designs(client_id: str):
    """Λίστα με τις 3 προτάσεις design + ποια είναι προτεινόμενη/επιλεγμένη + live URL."""
    variants = db.list_site_variants(client_id)
    selected = db.get_selected_design(client_id)
    deployed_url = db.get_live_site(client_id)
    return {"variants": variants, "selected": selected, "deployed_url": deployed_url}


@app.get("/clients/{client_id}/preview/{layout}", response_class=HTMLResponse)
def preview_design(client_id: str, layout: str):
    """Σερβίρει το HTML μιας πρότασης design για preview στον πελάτη."""
    variant = db.get_site_variant(client_id, layout)
    if not variant:
        raise HTTPException(404, "Δεν βρέθηκε αυτό το design.")
    return HTMLResponse(variant["html"])


@app.post("/clients/{client_id}/select-design")
def select_design(client_id: str, sel: SelectDesign, bg: BackgroundTasks):
    """Ο πελάτης πάτησε Approve — καταγράφει την επιλογή και ξεκινά deploy στο background."""
    if sel.layout not in ("studio", "commerce", "atelier"):
        raise HTTPException(400, f"Άγνωστο layout: {sel.layout}")
    try:
        db.set_selected_design(client_id, sel.layout)
    except Exception as e:
        raise HTTPException(500, f"Δεν αποθηκεύτηκε η επιλογή: {e}")
    bg.add_task(_deploy_selected_bg, client_id, sel.layout)
    return {"ok": True, "selected": sel.layout, "deploying": True}


@app.post("/clients/{client_id}/assets")
def add_client_asset(client_id: str, asset: ClientAsset):
    """Αποθηκεύει στοιχεία/links/assets που δίνει ο πελάτης για site/social.
    MVP: metadata + URL/text. Binary uploads θα μπουν αργότερα με Supabase Storage."""
    if not asset.rights_ok:
        raise HTTPException(400, "Πρέπει να επιβεβαιωθούν τα δικαιώματα χρήσης του asset.")
    asset_id = db.save_client_asset(client_id, asset.model_dump())
    return {"asset_id": asset_id}


@app.get("/clients/{client_id}/assets")
def list_client_assets(client_id: str, usage: str | None = None):
    return {"assets": db.get_client_assets(client_id, usage=usage)}

GRAPH = "https://graph.facebook.com/v21.0"

# Temporary store: client_id → {pages: [...]} — lives in process memory, fine for Railway MVP.
_pending: dict[str, dict] = {}
# ΠΡΕΠΕΙ να ταιριάζει ΑΚΡΙΒΩΣ στο Meta App → Settings → Valid OAuth Redirect URIs
# Ανανέωσε και εκεί αν αλλάξεις το domain.
REDIRECT_URI = "https://api.getvitrina.gr/connect/callback"
SCOPES = ",".join([
    "instagram_basic",
    "instagram_content_publish",
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
])


@app.get("/connect/start")
def start(client_id: str):
    """Ξεκινά το OAuth. client_id = ο δικός μας πελάτης (για να ξέρουμε ποιον συνδέουμε)."""
    url = (
        "https://www.facebook.com/v21.0/dialog/oauth"
        f"?client_id={cfg.META_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={client_id}"
        f"&scope={SCOPES}"
    )
    return RedirectResponse(url)


@app.get("/connect/callback")
def callback(code: str | None = None, state: str | None = None,
             error: str | None = None):
    if error or not code:
        raise HTTPException(400, f"OAuth error: {error}")
    our_client_id = state

    # 1) code → short-lived user token
    r = requests.get(f"{GRAPH}/oauth/access_token", params={
        "client_id": cfg.META_APP_ID,
        "client_secret": cfg.META_APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }, timeout=20)
    r.raise_for_status()
    short_token = r.json()["access_token"]

    # 2) short → long-lived user token (~60 μέρες)
    r = requests.get(f"{GRAPH}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": cfg.META_APP_ID,
        "client_secret": cfg.META_APP_SECRET,
        "fb_exchange_token": short_token,
    }, timeout=20)
    r.raise_for_status()
    long_user_token = r.json()["access_token"]

    # 3) Pages του χρήστη (το page token είναι long-lived αν ο user token είναι)
    r = requests.get(f"{GRAPH}/me/accounts", params={
        "access_token": long_user_token,
        "fields": "id,name,access_token,instagram_business_account",
    }, timeout=20)
    r.raise_for_status()
    pages = r.json().get("data", [])
    if not pages:
        return HTMLResponse("<h3>Δεν βρέθηκε Σελίδα Facebook. "
                            "Βεβαιώσου ότι διαχειρίζεσαι μια Page.</h3>")

    # 4) Προσωρινή αποθήκευση — ο χρήστης επιλέγει Σελίδα στο επόμενο βήμα.
    # Δεν περνάμε tokens στο URL.
    _pending[our_client_id] = {"pages": pages}
    return RedirectResponse(
        f"https://getvitrina.gr/connect.html"
        f"?client_id={urllib.parse.quote_plus(our_client_id)}&step=select_page"
    )


@app.get("/connect/pages")
def get_pending_pages(client_id: str):
    """Επιστρέφει λίστα Σελίδων για επιλογή — χωρίς tokens."""
    pending = _pending.get(client_id)
    if not pending:
        raise HTTPException(404, "Δεν βρέθηκε εκκρεμής σύνδεση. Ξαναπροσπάθησε από την αρχή.")
    return {"pages": [
        {"id": p["id"], "name": p["name"],
         "has_instagram": bool(p.get("instagram_business_account", {}).get("id"))}
        for p in pending["pages"]
    ]}


@app.post("/connect/finalize")
def finalize_page_selection(client_id: str, page_id: str):
    """Αποθηκεύει credentials για τη Σελίδα που επέλεξε ο χρήστης."""
    pending = _pending.pop(client_id, None)
    if not pending:
        raise HTTPException(404, "Η σύνδεση έχει λήξει. Ξαναπροσπάθησε από την αρχή.")
    selected = next((p for p in pending["pages"] if p["id"] == page_id), None)
    if not selected:
        raise HTTPException(400, "Άγνωστη Σελίδα.")
    ig = selected.get("instagram_business_account", {})
    ig_user_id = ig.get("id")
    _store_credentials(client_id, selected["id"], selected["access_token"], ig_user_id)
    return {"ok": True, "page_name": selected["name"], "ig_user_id": ig_user_id}


def _store_credentials(client_id: str | None, page_id: str,
                       page_token: str, ig_user_id: str | None) -> None:
    """Αποθηκεύει Meta credentials στη Supabase (direct Graph API path).
    ⚠️ page_token: ΜΗΝ εμφανίζεται σε logs — αποθηκεύεται κρυπτογραφημένα σε production."""
    if not client_id:
        raise ValueError("client_id απαιτείται για αποθήκευση credentials")
    db.save_social_creds(client_id, page_id, page_token, ig_user_id)
    print(f"[store] client={client_id} page={page_id} ig={ig_user_id} token=***")
