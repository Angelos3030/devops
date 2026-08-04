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
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from . import auth
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

# CORS — ώστε το landing/connect (getvitrina.gr) και το dashboard (sites service)
# να καλούν το API. Το regex καλύπτει τα Railway/Pages preview URLs, που αλλάζουν.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://getvitrina.gr",
        "https://www.getvitrina.gr",
        "https://vitrina-7uq.pages.dev",
        "https://db65ba76.vitrina-7uq.pages.dev",
        "https://app.getvitrina.gr",
        cfg.APP_BASE_URL,
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://([a-z0-9-]+\.)*(up\.railway\.app|pages\.dev)",
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
    website: str | None = None   # υπάρχον site/σελίδα → auto-fill υπηρεσιών (site_copy)


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


def _ensure_geo(client_id: str, address: str, city: str) -> None:
    """Γεωκωδικοποιεί μία φορά και αποθηκεύει — για το `geo` του schema + τον χάρτη."""
    try:
        content = db.get_site_content(client_id)
        if content.get("geo_lat") and content.get("geo_lng"):
            return
        from . import geocode as gc
        hit = gc.geocode(address or "", city or "")
        if not hit:
            return
        content.update({"geo_lat": str(hit["lat"]), "geo_lng": str(hit["lng"])})
        db.save_site_content(client_id, content)
        print(f"[geo] {client_id} -> {hit['lat']},{hit['lng']}")
    except Exception as e:  # noqa: BLE001 — καθαρά best-effort
        print(f"[geo] skipped: {e}")


def _build_site_bg(client_id: str, form: dict) -> None:
    """Τρέχει στο background: παράγει 3 premium designs (studio/commerce/atelier)
    ντετερμινιστικά (0 API tokens) και τα αποθηκεύει ως previews για έγκριση.
    Best-effort — αν λείπει DB, απλώς το logάρει."""
    try:
        from . import premium_generator as pg
        from . import site_copy
        intake = _enrich_intake(client_id, form)
        intake = site_copy.enrich_with_copy(intake)  # AI copy if key present, else no-op
        _ensure_geo(client_id, form.get("address") or "", form.get("city") or "")
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
        "address": c.get("address") or "",
        "tagline": c.get("style") or "",
    }
    intake = _enrich_intake(client_id, intake)

    # Ό,τι άλλαξε ο πελάτης από το dashboard υπερισχύει των defaults/AI copy.
    try:
        overrides = db.get_site_content(client_id)
    except Exception as e:  # noqa: BLE001 — ποτέ να μη σπάσει το render
        print(f"[intake] overrides skipped: {e}")
        overrides = {}
    if overrides:
        mapped = {"trade": "type"}  # dashboard key → intake key
        for k, v in overrides.items():
            if k in ("template",) or v in (None, "", [], {}):
                continue
            intake[mapped.get(k, k)] = v
        if isinstance(overrides.get("areas"), str):
            intake["areas"] = [a.strip() for a in overrides["areas"].split("·") if a.strip()]
    return intake


@app.get("/clients/{client_id}/site-data")
def site_data(client_id: str, layout: str = ""):
    """Δομημένα data του site (JSON) για το Next.js multi-tenant render.
    Επιστρέφει normalized context (name, services[], gallery[], story[]...) + layout."""
    import html as _html
    from . import premium_generator as pg
    rid = _resolve_client(client_id).get("id", client_id)  # uuid (domain → uuid) για downstream queries
    intake = _intake_from_db(client_id)
    ctx = pg.normalize(intake)
    # Δεκτά και τα React template keys (premium smart-match), όχι μόνο τα legacy layouts.
    known = (*pg.LAYOUTS, *pg.REACT_TEMPLATES)
    chosen = layout if layout in known else (
        db.get_selected_design(rid) or pg.recommend_templates(intake)[0] or ctx["_recommended"])

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
def lookup_clients(authorization: str | None = Header(default=None)):
    """Οι πελάτες ΤΟΥ συνδεδεμένου χρήστη (dashboard login → client records).

    Το email βγαίνει από το επαληθευμένο Supabase token — ποτέ από query param,
    αλλιώς οποιοσδήποτε θα μπορούσε να διαβάσει δεδομένα άλλων (GDPR)."""
    email = auth.current_email(authorization)
    return {"clients": db.get_clients_by_email(email)}


# --- Dashboard: περιεχόμενο που επεξεργάζεται ο πελάτης ---------------------

# Μόνο αυτά επιτρέπεται να αλλάξει ο πελάτης (allowlist — τίποτα αυθαίρετο στη DB).
_EDITABLE = {
    "name", "trade", "city", "phone", "hours", "areas",
    "tagline", "intro", "story_title", "story_paragraphs", "cta_title",
    "services", "template",
    # Local SEO / Google Maps
    "address", "gbp_url", "geo_lat", "geo_lng",
}


@app.get("/clients/{client_id}/content")
def get_content(client_id: str, authorization: str | None = Header(default=None)):
    """Τα τρέχοντα επεξεργάσιμα πεδία (defaults + ό,τι έχει αλλάξει ο πελάτης)."""
    from . import premium_generator as pg
    client = auth.require_client_access(client_id, authorization)
    intake = _intake_from_db(client_id)
    ctx = pg.normalize(intake)
    overrides = db.get_site_content(client_id)
    current = {
        "name": client.get("name") or "",
        "trade": client.get("business_type") or "",
        "city": client.get("city") or "",
        "phone": client.get("phone") or "",
        "hours": intake.get("hours") or ctx["HOURS"],
        "tagline": intake.get("tagline") or ctx["TAGLINE"],
        "intro": intake.get("intro") or ctx["INTRO"],
        "story_title": intake.get("story_title") or ctx["STORY_TITLE"],
        "cta_title": intake.get("cta_title") or ctx["CTA_TITLE"],
        "story_paragraphs": [p["p"] for p in ctx["story"]],
        "services": [{"name": s["title"], "description": s["desc"]} for s in ctx["services"]],
        "template": db.get_selected_design(client_id) or pg.recommend_templates(intake)[0],
    }
    current.update({k: v for k, v in overrides.items() if k in _EDITABLE})
    return {"content": current, "templates": pg.recommend_templates(intake, limit=8),
            "all_templates": list(pg.REACT_TEMPLATES)}


@app.get("/clients/{client_id}/account")
def get_account(client_id: str, authorization: str | None = Header(default=None)):
    """Σύνοψη λογαριασμού για το dashboard: site, domain, συνδρομή."""
    client = auth.require_client_access(client_id, authorization)
    try:
        sub = db.get_subscription(client_id) or {}
    except Exception:  # noqa: BLE001
        sub = {}
    domain = None
    try:
        rows = (db._client().table("domains").select("domain,status")
                .eq("client_id", client_id).limit(1).execute()).data
        domain = rows[0] if rows else None
    except Exception:  # noqa: BLE001
        pass
    return {
        "name": client.get("name"), "status": client.get("status"),
        "email": client.get("email"), "domain": domain,
        "subscription": {"plan": sub.get("plan"), "status": sub.get("status")},
        "has_billing": bool(sub.get("stripe_customer_id")),
    }


@app.post("/clients/{client_id}/billing-portal")
def billing_portal(client_id: str, authorization: str | None = Header(default=None)):
    """Stripe Customer Portal — ο πελάτης βλέπει/αλλάζει/ακυρώνει τη συνδρομή του."""
    auth.require_client_access(client_id, authorization)
    if not cfg.STRIPE_SECRET_KEY:
        raise HTTPException(500, "Λείπει STRIPE_SECRET_KEY.")
    sub = db.get_subscription(client_id) or {}
    customer = sub.get("stripe_customer_id")
    if not customer:
        raise HTTPException(400, "Δεν υπάρχει ενεργή συνδρομή ακόμα.")
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer,
            return_url=f"{cfg.APP_BASE_URL}/dashboard?client={client_id}",
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"Δεν άνοιξε το portal συνδρομής: {e}")
    return {"url": session.url}


# Πακέτα που περιλαμβάνουν τα εβδομαδιαία posts.
_POST_PLANS = {"social", "premium"}


def _has_posts_plan(client_id: str, client: dict) -> bool:
    """Η ενεργή συνδρομή υπερισχύει· το `clients.plan` είναι το fallback."""
    try:
        sub = db.get_subscription(client_id) or {}
        if sub.get("status") in ("active", "trialing"):
            return (sub.get("plan") or "") in _POST_PLANS
    except Exception:  # noqa: BLE001
        pass
    return (client.get("plan") or "") in _POST_PLANS


@app.get("/clients/{client_id}/posts")
def week_posts(client_id: str, authorization: str | None = Header(default=None)):
    """Η εβδομάδα του πελάτη σε έτοιμα posts (αντιγράφει & δημοσιεύει μόνος του).

    Δεν χρειάζεται έγκριση Meta — αυτή αφορά την ΑΥΤΟΜΑΤΗ δημοσίευση, που είναι
    ξεχωριστό βήμα."""
    from . import premium_generator as pg
    from . import social_posts as sp
    client = auth.require_client_access(client_id, authorization)
    intake = _intake_from_db(client_id)
    ctx = pg.normalize(intake)
    plan = sp.week_plan(ctx, pg._vertical(intake))

    # Τα posts είναι ξεχωριστό πακέτο. Χωρίς αυτό δείχνουμε ΕΝΑ δείγμα — ο πελάτης
    # βλέπει την αξία και αναβαθμίζει μόνος του, αντί για άδειο κλειδωμένο πλαίσιο.
    if not _has_posts_plan(client_id, client):
        return {"posts": plan[:1], "locked": True, "total": len(plan),
                "upgrade": {"plan": "social", "price": "€29.99/μήνα",
                            "pitch": "Και τα 7 posts της εβδομάδας, κάθε εβδομάδα."}}

    plan = sp.enrich_with_ai(plan, ctx)     # no-op χωρίς κλειδί
    return {"posts": plan, "locked": False, "vertical": pg._vertical(intake)}


class ChatEdit(BaseModel):
    message: str


@app.post("/clients/{client_id}/chat-edit")
def chat_edit(client_id: str, body: ChatEdit,
              authorization: str | None = Header(default=None)):
    """«Πες τι θέλεις να αλλάξει» — ο βοηθός το εφαρμόζει στο site.

    Το AI επιστρέφει μόνο JSON patch· ό,τι δεν είναι στο allowlist αγνοείται."""
    from . import premium_generator as pg
    from . import site_edit as se
    auth.require_client_access(client_id, authorization)
    if not (body.message or "").strip():
        raise HTTPException(400, "Γράψε τι θέλεις να αλλάξει.")

    current = get_content(client_id, authorization)["content"]
    intake = _intake_from_db(client_id)
    result = se.chat_edit(body.message, current, pg.recommend_templates(intake, limit=8))

    applied = {}
    if result["changes"]:
        merged = {**{k: v for k, v in current.items() if k in _EDITABLE}, **result["changes"]}
        saved = put_content(client_id, ContentUpdate(content=merged), authorization)
        applied = {k: result["changes"][k] for k in result["changes"] if k in saved["saved"]}
    return {"reply": result["reply"], "changed": sorted(applied.keys()), "content": applied}


class ContentUpdate(BaseModel):
    content: dict


@app.put("/clients/{client_id}/content")
def put_content(client_id: str, body: ContentUpdate,
                authorization: str | None = Header(default=None)):
    """Αποθηκεύει τις αλλαγές του πελάτη. Το site τις δείχνει αμέσως."""
    from . import premium_generator as pg
    auth.require_client_access(client_id, authorization)

    clean: dict = {}
    for k, v in (body.content or {}).items():
        if k not in _EDITABLE:
            continue
        if k == "services" and isinstance(v, list):
            clean[k] = [
                {"name": str(s.get("name", ""))[:80], "description": str(s.get("description", ""))[:400]}
                for s in v if isinstance(s, dict) and str(s.get("name", "")).strip()
            ][:8]
        elif k == "story_paragraphs" and isinstance(v, list):
            clean[k] = [str(p)[:1200] for p in v if str(p).strip()][:5]
        elif k == "template":
            if v in pg.REACT_TEMPLATES:
                clean[k] = v
        elif isinstance(v, str):
            clean[k] = v[:1200]

    db.save_site_content(client_id, clean)
    if clean.get("address") or clean.get("city"):
        # νέα διεύθυνση → ξαναϋπολόγισε συντεταγμένες
        cur = db.get_site_content(client_id)
        cur.pop("geo_lat", None); cur.pop("geo_lng", None)
        db.save_site_content(client_id, cur)
        _ensure_geo(client_id, clean.get("address", ""), clean.get("city", ""))
    if clean.get("template"):
        try:
            db.set_selected_design(client_id, clean["template"])
        except Exception as e:  # noqa: BLE001
            print(f"[content] template selection not persisted: {e}")
    return {"ok": True, "saved": sorted(clean.keys())}


@app.get("/clients/{client_id}/designs")
def list_designs(client_id: str):
    """Οι προτάσεις design του πελάτη + ποια είναι προτεινόμενη/επιλεγμένη + live URL.

    `templates`: smart-match — 4 React templates με το premium της κατηγορίας του πρώτο
    (αυτά δείχνει το /choose). `variants`: τα legacy static layouts (συμβατότητα)."""
    from . import premium_generator as pg
    rid = _resolve_client(client_id).get("id", client_id)
    variants = db.list_site_variants(rid)
    selected = db.get_selected_design(rid)
    deployed_url = db.get_live_site(rid)
    try:
        templates = pg.recommend_templates(_intake_from_db(client_id))
    except Exception as e:  # noqa: BLE001 — ποτέ να μη μπλοκάρει το choose
        print(f"[designs] smart-match skipped: {e}")
        templates = []
    return {"variants": variants, "templates": templates,
            "selected": selected, "deployed_url": deployed_url}


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
    from . import premium_generator as pg
    if sel.layout not in (*pg.LAYOUTS, *pg.REACT_TEMPLATES):
        raise HTTPException(400, f"Άγνωστο layout: {sel.layout}")
    rid = _resolve_client(client_id).get("id", client_id)
    try:
        db.set_selected_design(rid, sel.layout)
    except Exception as e:
        raise HTTPException(500, f"Δεν αποθηκεύτηκε η επιλογή: {e}")
    bg.add_task(_deploy_selected_bg, rid, sel.layout)
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
