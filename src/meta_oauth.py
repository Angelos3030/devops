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

import hashlib
import re
import secrets
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
from . import theme_capabilities as tcaps

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
        "http://127.0.0.1:3700",
        "http://127.0.0.1:3701",
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


class ClientAsset(BaseModel):
    type: str = "other"
    title: str | None = None
    content: str | None = None
    url: str | None = None
    usage: str = "site"
    rights_ok: bool = False


@app.post("/create-checkout")
def create_checkout(req: CheckoutRequest,
                    authorization: str | None = Header(default=None)):
    """Authenticated, server-priced Checkout with a Stripe-owned 30-day trial."""
    from . import billing

    client = auth.require_client_access(req.client_id, authorization)
    try:
        billing.validate_runtime_configuration(retrieve_price=True)
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_collection="always",
            line_items=[{"price": cfg.STRIPE_PRICE_SITE, "quantity": 1}],
            client_reference_id=req.client_id,
            customer_email=client.get("email") or None,
            metadata={"client_id": req.client_id, "plan": "site"},
            subscription_data={
                "trial_period_days": billing.TRIAL_DAYS,
                "metadata": {"client_id": req.client_id, "plan": "site"},
            },
            success_url=(f"{cfg.APP_BASE_URL}/dashboard?client={req.client_id}"
                         "&checkout=success&session_id={CHECKOUT_SESSION_ID}"),
            cancel_url=f"{cfg.APP_BASE_URL}/dashboard?client={req.client_id}&checkout=cancel",
        )
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except stripe.StripeError:
        raise HTTPException(502, "Δεν μπορέσαμε να ανοίξουμε την ασφαλή πληρωμή.")
    return {
        "checkout_url": session.url,
        "amount_due_today": 0,
        "trial_days": billing.TRIAL_DAYS,
        "recurring_amount_cents": billing.SITE_AMOUNT_CENTS,
        "currency": billing.SITE_CURRENCY,
        "interval": billing.SITE_INTERVAL,
    }


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
            # Η κλάση ταξιδεύει μαζί με την εικόνα: ο renderer δεν επιτρέπεται
            # να μαντέψει αν αυτό είναι ο χώρος, η δουλειά ή το πρόσωπό του.
            gallery.append({"image": url, "title": a.get("title") or "Έργο",
                            "media_class": a.get("media_class")})
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
    # Χωρίς διεύθυνση ΚΑΙ χωρίς πόλη δεν υπάρχει τίποτα να γεωκωδικοποιηθεί: το
    # Nominatim απαντούσε με το κέντρο της Ελλάδας (38.99, 21.98) και το site
    # έπαιρνε καρφίτσα σε λάθος σημείο — μαζί με geo στο JSON-LD. Ψεύτικη τοποθεσία
    # είναι χειρότερη από καθόλου: τη βλέπει και η Google.
    if not (address or "").strip() and not (city or "").strip():
        return
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
    from . import quick_start as qs
    try:
        from . import premium_generator as pg
        from . import site_copy
        qs.mark(client_id, "copy", done=False)
        intake = _enrich_intake(client_id, form)
        intake = site_copy.enrich_with_copy(intake)  # AI copy if key present, else no-op
        qs.mark(client_id, "copy")
        qs.mark(client_id, "photos")   # οι εικόνες επιλέγονται μέσα στο enrich
        qs.mark(client_id, "geo", done=False)
        _ensure_geo(client_id, form.get("address") or "", form.get("city") or "")
        qs.mark(client_id, "geo")
        qs.mark(client_id, "design", done=False)
        recommended = pg.recommend_layout(intake)
        variants = pg.generate_variants(intake)
        for layout, html in variants.items():
            try:
                db.save_site_variant(client_id, layout, html,
                                     recommended=(layout == recommended))
            except Exception as e:
                print(f"[onboard bg] save variant {layout} failed: {e}")
        qs.mark(client_id, "design")
        qs.mark(client_id, "seo")
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
    # Το clients table κρατά μόνο τα βασικά στοιχεία. Η ελεύθερη περιγραφή είναι
    # κρίσιμη για το vertical matching (π.χ. type="Άλλο", description="νυχάδικο").
    # Αν χαθεί εδώ, το /designs βλέπει αργότερα μόνο το "Άλλο" και προτείνει
    # άσχετα templates. Κρατάμε τα υπόλοιπα intake fields στο JSON content row.
    initial_content = {
        key: data[key]
        for key in ("description", "style", "website")
        if data.get(key)
    }
    if initial_content:
        try:
            db.save_site_content(client_id, initial_content)
        except Exception as e:  # noqa: BLE001 — ο πελάτης δημιουργήθηκε, μη μπλοκάρεις
            print(f"[onboard] initial content save skipped: {e}")
    claim_token = secrets.token_urlsafe(32)
    try:
        db.create_client_claim(client_id, hashlib.sha256(claim_token.encode()).hexdigest())
    except Exception as e:
        print(f"[onboard] claim creation failed: {e}")
        claim_token = None
    bg.add_task(_build_site_bg, client_id, data)
    return {"client_id": client_id, "claim_token": claim_token}


class QuickStart(BaseModel):
    text: str


class ClaimSite(BaseModel):
    token: str


@app.post("/start")
def quick_start_endpoint(body: QuickStart, bg: BackgroundTasks):
    """Μία πρόταση → πελάτης, χωρίς φόρμα.

    «Site first, questions later»: ό,τι λείπει το ρωτάμε ΑΦΟΥ δει αποτέλεσμα.
    Κάθε βήμα πριν την πρώτη «ουάου» στιγμή είναι σημείο διαρροής."""
    from . import quick_start as qs
    text = (body.text or "").strip()
    if len(text) < 3:
        raise HTTPException(400, "Πες μας δυο λόγια για την επιχείρησή σου.")

    parsed = qs.parse(text)
    services = parsed.pop("services", [])
    try:
        client_id = db.create_client({k: v for k, v in parsed.items() if k != "description"})
    except Exception as e:
        raise HTTPException(500, f"Δεν μπόρεσα να αποθηκεύσω τον πελάτη: {e}")

    # Η ελεύθερη περιγραφή είναι το καύσιμο του vertical matching — αν χαθεί,
    # το /designs βλέπει μόνο τον τύπο και προτείνει άσχετα templates.
    content = {"description": parsed.get("description") or text}
    for key in ("style", "features", "booking", "pricing", "media_available"):
        if parsed.get(key) not in (None, "", []):
            content[key] = parsed[key]
    if services:
        # Ο parser επιστρέφει πλέον {title, desc}. Τα σκέτα κείμενα παραμένουν
        # δεκτά ώστε μια παλιότερη απάντηση του μοντέλου να μη ρίξει τη ροή.
        content["services"] = [
            s if isinstance(s, dict) else {"title": str(s), "desc": ""}
            for s in services
        ]
    try:
        db.save_site_content(client_id, content)
    except Exception as e:  # noqa: BLE001 — ο πελάτης δημιουργήθηκε, μη μπλοκάρεις
        print(f"[start] initial content save skipped: {e}")

    claim_token = secrets.token_urlsafe(32)
    try:
        db.create_client_claim(client_id, hashlib.sha256(claim_token.encode()).hexdigest())
    except Exception as e:
        # A missing migration must be visible in logs, but must not destroy the site
        # that was already generated. The dashboard will explain that ownership failed.
        print(f"[start] claim creation failed: {e}")
        claim_token = None

    qs.mark(client_id, "copy", done=False)
    bg.add_task(_build_site_bg, client_id, {**parsed, "description": text})
    return {"client_id": client_id, "parsed": parsed, "claim_token": claim_token}


@app.get("/progress/{client_id}")
def progress_endpoint(client_id: str,
                      authorization: str | None = Header(default=None),
                      x_vitrina_claim: str | None = Header(default=None)):
    """Τι κάνει η ομάδα αυτή τη στιγμή — για την οθόνη δημιουργίας."""
    auth.require_client_or_claim(client_id, authorization, x_vitrina_claim)
    from . import quick_start as qs
    snap = qs.snapshot(client_id)
    try:
        snap["ready"] = bool(db.list_site_variants(client_id))
    except Exception:  # noqa: BLE001
        snap["ready"] = False
    return snap


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
        "city": c.get("city"), "phone": c.get("phone"),
        # ΤΟ `clients.email` ΔΕΝ ΕΙΝΑΙ ΔΗΜΟΣΙΟ ΣΤΟΙΧΕΙΟ. Είναι η ταυτότητα
        # λογαριασμού/χρέωσης: το γράφει το checkout (βλ. `link_client_email`)
        # και πάνω του στηρίζεται το login. Ερχόταν εδώ ως αφετηρία και, χωρίς
        # καμία ενέργεια του πελάτη, τυπωνόταν στη ΔΗΜΟΣΙΑ σελίδα του.
        #
        # ΜΕΤΡΗΘΗΚΕ: `clients.email = private-billing@gmail.test`,
        # `site_content.email` κενό → το `/site-data` δημοσίευε το πρώτο, ενώ
        # η φόρμα «Email (φαίνεται στο site)» έδειχνε ΚΕΝΟ πεδίο. Ο πελάτης
        # δεν είχε τρόπο ούτε να το δει ούτε να το σβήσει: το άδειασμα ενός
        # ήδη άδειου πεδίου δεν κάνει τίποτα.
        #
        # Μοναδική πηγή αλήθειας για το δημόσιο email είναι το
        # `site_content.email`, που το γράφει ΡΗΤΑ ο πελάτης και το
        # επικαλύπτει παρακάτω. Κενό εδώ σημαίνει «δεν δείχνουμε email».
        "email": "",
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

    # Πολιτική εικόνων ανά site (opt-in, βλ. db/migrations/0002_media_semantics.sql).
    # Με 'real-only' καμία δανεική εικόνα δεν γεμίζει ενότητα ταυτότητας: όπου
    # λείπει πραγματικό υλικό, η σελίδα γίνεται τυπογραφική αντί να δανειστεί
    # πρόσωπο, χώρο ή δουλειά. Χωρίς τη ρύθμιση, η συμπεριφορά μένει η ίδια.
    policy = (_resolve_client(client_id) or {}).get("media_policy")
    if policy == "real-only":
        from . import media_semantics as msem
        assets = [
            msem.Asset(g["image"], g.get("media_class") or msem.ILLUSTRATIVE, g.get("title") or "")
            for g in (data.get("gallery") or []) if g.get("image")
        ]
        plan = msem.plan(assets, ("hero", "work", "space", "portrait", "product"))
        data["MEDIA_POLICY"] = "real-only"
        data["gallery"] = [a.to_dict() for a in assets if a.is_real]
        data["HERO_IS_REAL"] = not plan["typographic"]
        data["MEDIA_ILLUSTRATIVE"] = plan["typographic"]
        if plan["typographic"]:
            data["GALLERY_TITLE"] = msem.NEUTRAL_TITLE["work"]

    return {"layout": chosen, "layouts": list(pg.LAYOUTS), "data": data}


@app.get("/clients/lookup")
def lookup_clients(authorization: str | None = Header(default=None)):
    """Οι πελάτες ΤΟΥ συνδεδεμένου χρήστη (dashboard login → client records).

    Το email βγαίνει από το επαληθευμένο Supabase token — ποτέ από query param,
    αλλιώς οποιοσδήποτε θα μπορούσε να διαβάσει δεδομένα άλλων (GDPR)."""
    email = auth.current_email(authorization)
    return {"clients": db.get_clients_by_email(email)}


@app.post("/clients/{client_id}/claim")
def claim_site(client_id: str, body: ClaimSite,
               authorization: str | None = Header(default=None)):
    """Attach an anonymously generated site to the signed-in user exactly once."""
    email = auth.current_email(authorization)
    token = (body.token or "").strip()
    if len(token) < 32:
        raise HTTPException(400, "Μη έγκυρος σύνδεσμος ιδιοκτησίας.")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    try:
        claimed = db.claim_client_site(client_id, token_hash, email)
    except Exception as e:
        print(f"[claim] {client_id}: {e}")
        raise HTTPException(503, "Δεν μπόρεσα να αποθηκεύσω το site στον λογαριασμό σου.")
    if not claimed:
        raise HTTPException(404, "Ο σύνδεσμος ιδιοκτησίας έληξε ή χρησιμοποιήθηκε.")
    return {"ok": True, "client_id": client_id}


# --- Dashboard: περιεχόμενο που επεξεργάζεται ο πελάτης ---------------------

# Μόνο αυτά επιτρέπεται να αλλάξει ο πελάτης (allowlist — τίποτα αυθαίρετο στη DB).
_EDITABLE = {
    "name", "trade", "city", "phone", "hours", "areas",
    "tagline", "intro", "story_title", "story_paragraphs", "cta_title",
    "services", "template", "palette", "font_pair",
    # Local SEO / Google Maps
    "address", "gbp_url", "geo_lat", "geo_lng",
    # Επικοινωνία & social — χωρίς αυτά ο πελάτης δεν μπορούσε να διορθώσει
    # λάθος email ούτε να βάλει τη σελίδα του, χωρίς να μας ζητήσει βοήθεια.
    "email", "facebook", "instagram",
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
        "palette": intake.get("palette") or "original",
        "font_pair": intake.get("font_pair") or "editorial",
    }
    current.update({k: v for k, v in overrides.items() if k in _EDITABLE})
    return {"content": current, "rev": db.site_content_rev(client_id),
            "editor_version": db.editor_version(client_id),
            "templates": pg.recommend_templates(intake, limit=12),
            "all_templates": list(pg.REACT_TEMPLATES)}


@app.get("/clients/{client_id}/account")
def get_account(client_id: str, authorization: str | None = Header(default=None)):
    """Σύνοψη λογαριασμού για το dashboard: site, domain, συνδρομή."""
    from . import billing

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
        "subscription": {
            "plan": sub.get("plan"), "status": sub.get("status"),
            "trial_end": sub.get("trial_end"),
            "current_period_end": sub.get("current_period_end"),
            "cancel_at_period_end": bool(sub.get("cancel_at_period_end")),
            "canceled_at": sub.get("canceled_at"), "ended_at": sub.get("ended_at"),
            "entitlement": billing.entitlement(sub),
        },
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


class PublishRequest(BaseModel):
    message: str
    image_url: str | None = None
    targets: list[str] | None = None      # ["facebook"] και/ή ["instagram"]
    dry_run: bool = True                  # σκόπιμα True: η δημοσίευση θέλει ρητή πρόθεση


class SocialDraftRequest(BaseModel):
    caption: str
    image_url: str | None = None
    targets: list[str] | None = None
    scheduled_for: str | None = None


class SocialApprovalRequest(BaseModel):
    scheduled_for: str | None = None


@app.get("/clients/{client_id}/social-queue")
def social_queue(client_id: str, status: str | None = None, limit: int = 50,
                 authorization: str | None = Header(default=None)):
    """Content calendar / queue for the authenticated client."""
    auth.require_client_access(client_id, authorization)
    return {"posts": db.list_posts(client_id, status=status, limit=min(max(limit, 1), 100))}


@app.post("/clients/{client_id}/social-queue")
def create_social_draft(client_id: str, body: SocialDraftRequest,
                        authorization: str | None = Header(default=None)):
    """Create an approval-required draft. Never publishes immediately."""
    from . import social_engine
    client = auth.require_client_access(client_id, authorization)
    if not _has_posts_plan(client_id, client):
        raise HTTPException(403, "Το πακέτο Social χρειάζεται για αυτόματες δημοσιεύσεις.")
    try:
        post_id = social_engine.create_draft(
            client_id, body.caption, image_url=body.image_url,
            targets=body.targets, scheduled_for=body.scheduled_for,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return {"id": post_id, "status": "pending_approval"}


@app.post("/clients/{client_id}/social-queue/{post_id}/approve")
def approve_social_post(client_id: str, post_id: str, body: SocialApprovalRequest,
                        authorization: str | None = Header(default=None)):
    """Explicit approval is the only normal path into the publish queue."""
    auth.require_client_access(client_id, authorization)
    approved_by = auth.current_email(authorization)
    post = db.approve_post(client_id, post_id, approved_by, body.scheduled_for)
    if not post:
        raise HTTPException(409, "Το post δεν μπορεί να εγκριθεί στην τρέχουσα κατάστασή του.")
    return {"post": post}


@app.post("/clients/{client_id}/social-queue/{post_id}/reject")
def reject_social_post(client_id: str, post_id: str,
                       authorization: str | None = Header(default=None)):
    auth.require_client_access(client_id, authorization)
    post = db.reject_post(client_id, post_id)
    if not post:
        raise HTTPException(409, "Το post δεν μπορεί να απορριφθεί στην τρέχουσα κατάστασή του.")
    return {"post": post}


@app.post("/clients/{client_id}/social-queue/{post_id}/preview")
def preview_social_post(client_id: str, post_id: str,
                        authorization: str | None = Header(default=None)):
    """Meta payload preview; no network publication and no status transition."""
    from . import publisher
    auth.require_client_access(client_id, authorization)
    post = db.get_post(client_id, post_id)
    if not post:
        raise HTTPException(404, "Δεν βρέθηκε το post.")
    try:
        return publisher.publish(
            client_id, post.get("caption") or "", post.get("image_url"),
            post.get("targets"), dry_run=True,
        )
    except publisher.PublishError as e:
        raise HTTPException(400, str(e)) from None


@app.post("/clients/{client_id}/publish")
def publish_post(client_id: str, body: PublishRequest,
                 authorization: str | None = Header(default=None)):
    """Δημοσιεύει στη Σελίδα/Instagram του πελάτη.

    `dry_run` είναι **True από προεπιλογή**. Μια δημοσίευση είναι δημόσια και
    δεν ξεγίνεται· το να χρειάζεται ρητό `dry_run: false` σημαίνει ότι κανείς
    δεν ποστάρει κατά λάθος με ένα ξεχασμένο curl.
    """
    from . import publisher
    auth.require_client_access(client_id, authorization)
    if not body.message.strip():
        raise HTTPException(400, "Το κείμενο της δημοσίευσης είναι κενό.")
    if not body.dry_run:
        raise HTTPException(
            409,
            "Η άμεση δημοσίευση έχει απενεργοποιηθεί. Πρόσθεσε το post στην ουρά και έγκρινέ το.",
        )
    try:
        return publisher.publish(client_id, body.message.strip(),
                                 body.image_url, body.targets, body.dry_run)
    except publisher.PublishError as e:
        raise HTTPException(400, str(e)) from None


class ChatEdit(BaseModel):
    message: str
    expected_version: int | None = None
    idempotency_key: str | None = None


class ApplyEdit(BaseModel):
    message: str
    operations: list[dict]
    expected_version: int
    idempotency_key: str


class UndoEdit(BaseModel):
    expected_version: int
    idempotency_key: str


class _EditorSnapshotStore:
    def __init__(self, content: dict, assets: list[dict]):
        self.content, self.assets = content, assets
    def get_content(self, _client_id: str) -> dict: return dict(self.content)
    def get_assets(self, _client_id: str) -> list[dict]: return list(self.assets)


def _editor_context(client_id: str, authorization: str | None):
    current = get_content(client_id, authorization)["content"]
    version = db.editor_version(client_id)
    theme = current.get("template") or db.get_selected_design(client_id) or ""
    capabilities = {"palettes": ("original", *tcaps.get(theme).get("palettes", ()))}
    snapshot = _EditorSnapshotStore(current, db.get_client_assets(client_id, usage="site"))
    return current, version, capabilities, snapshot


@app.post("/clients/{client_id}/chat-edit")
def chat_edit(client_id: str, body: ChatEdit,
              authorization: str | None = Header(default=None)):
    """«Πες τι θέλεις να αλλάξει» — ο βοηθός εκτελεί αλλαγές με DeepSeek."""
    auth.require_client_access(client_id, authorization)
    msg = (body.message or "").strip()
    if not msg:
        raise HTTPException(400, "Γράψε τι θέλεις να αλλάξει.")

    current, version, capabilities, snapshot = _editor_context(client_id, authorization)

    # 1. Handle Undo Requests Directly
    undo_keywords = ["αναίρεσε", "αναιρεσε", "γύρνα πίσω", "γυρνα πισω", "undo", "revert"]
    if any(k in msg.lower() for k in undo_keywords):
        if body.expected_version is None or not body.idempotency_key:
            raise HTTPException(422, "Η αναίρεση χρειάζεται την τρέχουσα έκδοση του site.")
        from .ai_editor.store import DatabaseEditorStore, StaleRevisionError
        try:
            result = DatabaseEditorStore().undo(
                client_id, expected_version=body.expected_version,
                idempotency_key=body.idempotency_key)
        except StaleRevisionError:
            raise HTTPException(409, "Το site άλλαξε από άλλη καρτέλα.")
        return {"reply": "Η τελευταία αλλαγή αναιρέθηκε.", "changed": [],
                "content": result.get("content", current), "draft": False,
                "version": result.get("version", version)}

    from . import premium_generator as pg
    from .ai_editor.model import DeepSeekSiteEditingModel
    from .ai_editor.engine import EditingEngine

    # 2. Build SiteContext for DeepSeek
    intake = _intake_from_db(client_id)
    ctx = pg.normalize(intake)
    current_content = current

    model_context = {
        "business_name": current_content.get("name"),
        "vertical": current_content.get("trade"),
        "city": current_content.get("city"),
        "phone": current_content.get("phone"),
        "hours": current_content.get("hours"),
        "tagline": current_content.get("tagline"),
        "intro": current_content.get("intro"),
        "story_title": current_content.get("story_title"),
        "story_paragraphs": current_content.get("story_paragraphs"),
        "cta_title": current_content.get("cta_title"),
        "services": current_content.get("services"),
        "palette": current_content.get("palette"),
        "font_pair": current_content.get("font_pair"),
        "gallery_count": len(ctx.get("gallery") or [])
    }

    # 3. Call model to plan edit
    model = DeepSeekSiteEditingModel()
    plan = model.plan_edit(model_context, msg)

    if not plan:
        raise HTTPException(502, "Δεν ήταν δυνατή η επικοινωνία με τον βοηθό AI.")

    if plan.confidence < 0.75 or not plan.operations:
        return {
            "reply": plan.explanation,
            "changed": [],
            "content": {},
            "draft": False
        }

    # Validate and project only. The customer must explicitly approve it.
    res = EditingEngine.execute_plan(client_id, plan, store=snapshot,
                                     capabilities=capabilities, persist=False)
    if not res.success:
        return {
            "reply": f"Σφάλμα κατά την εκτέλεση: {res.message}",
            "changed": [],
            "content": {},
            "draft": False
        }

    operations_list = [op.model_dump() for op in plan.operations]
    changed_fields = [op.params.get("field") for op in plan.operations if op.op == "update_business_field"]

    return {
        "reply": plan.explanation,
        "changed": changed_fields,
        "content": res.after_state,
        "operations": operations_list,
        "version": version,
        "draft": True
    }


@app.post("/clients/{client_id}/editor/apply")
def apply_editor_proposal(client_id: str, body: ApplyEdit,
                          authorization: str | None = Header(default=None)):
    """Revalidate an approved proposal and atomically persist draft+revision."""
    auth.require_client_access(client_id, authorization)
    from .ai_editor.model import EditPlan
    from .ai_editor.engine import EditingEngine
    from .ai_editor.store import DatabaseEditorStore, StaleRevisionError
    current, version, capabilities, snapshot = _editor_context(client_id, authorization)

    # Η IDEMPOTENCY ΠΡΟΗΓΕΙΤΑΙ ΤΟΥ ΕΛΕΓΧΟΥ ΕΚΔΟΣΗΣ.
    #
    # Σε επανάληψη δικτύου ο client ξαναστέλνει το ΙΔΙΟ κλειδί με την ΑΡΧΙΚΗ
    # έκδοση. Η πρώτη αίτηση όμως πέτυχε και προχώρησε την έκδοση, οπότε ο
    # έλεγχος από κάτω έβλεπε αναντιστοιχία και γύριζε 409: ο πελάτης έβλεπε
    # «Το site άλλαξε από άλλη καρτέλα» ΜΕΤΑ από επιτυχημένη αποθήκευση, και
    # δεν είχε τρόπο να καταλάβει ότι η αλλαγή του είχε ήδη περάσει.
    #
    # Το ίδιο το RPC κάνει τον σωστό έλεγχο πρώτο· απλώς δεν έφτανε ποτέ εκεί.
    if body.idempotency_key:
        try:
            done = db.editor_idempotent_result(client_id, body.idempotency_key)
        except Exception:                       # η βάση δεν αποφασίζει τη ροή
            done = None
        if done:
            return {"ok": True, **done}

    if version != body.expected_version:
        raise HTTPException(409, "Το site άλλαξε από άλλη καρτέλα.")

    # Κενή λίστα πράξεων έγραφε κανονική έκδοση: το ιστορικό γέμιζε εγγραφές
    # που δεν άλλαζαν τίποτα, και η επόμενη «Αναίρεση» ανέτρεπε το τίποτα αντί
    # για την πραγματική αλλαγή του πελάτη.
    if not body.operations:
        raise HTTPException(422, "Δεν υπάρχουν αλλαγές για εφαρμογή.")

    try:
        plan = EditPlan(schema_version="1.0", intent="approved_edit",
                        explanation="Εγκεκριμένες αλλαγές", requires_confirmation=False,
                        confidence=1.0, operations=body.operations)
    except Exception:
        raise HTTPException(422, "Μη έγκυρο σχέδιο αλλαγών.")
    prepared = EditingEngine.execute_plan(client_id, plan, store=snapshot,
                                          capabilities=capabilities, persist=False)
    if not prepared.success:
        raise HTTPException(422, prepared.message)
    try:
        result = DatabaseEditorStore().commit_edit(
            client_id, expected_version=body.expected_version,
            idempotency_key=body.idempotency_key, message=body.message,
            operations=[op.model_dump() for op in plan.operations],
            before_state=prepared.before_state, after_state=prepared.after_state)
    except StaleRevisionError:
        raise HTTPException(409, "Το site άλλαξε από άλλη καρτέλα.")
    return {"ok": True, **result}


@app.post("/clients/{client_id}/editor/undo")
def undo_editor_change(client_id: str, body: UndoEdit,
                       authorization: str | None = Header(default=None)):
    auth.require_client_access(client_id, authorization)
    from .ai_editor.store import DatabaseEditorStore, StaleRevisionError
    try:
        result = DatabaseEditorStore().undo(
            client_id, expected_version=body.expected_version,
            idempotency_key=body.idempotency_key)
    except StaleRevisionError:
        raise HTTPException(409, "Το site άλλαξε από άλλη καρτέλα.")
    if not result.get("success"):
        raise HTTPException(404, "Δεν υπάρχει αλλαγή για αναίρεση.")
    return {"ok": True, **result}



# Πεδία που καταλήγουν σε `href`. Χωρίς έλεγχο σχήματος, ένα
# `data:text/html,<script>…</script>` γινόταν κανονικός σύνδεσμος στο δημόσιο
# site, και ένα `mailto:"><img src=x onerror=…>` τύπωνε σκουπίδια μέσα στη
# σελίδα. Δεν εκτελέστηκε κώδικας — ο browser κόβει `javascript:` και
# top-level `data:` — αλλά ο σύνδεσμος είναι φορέας phishing και η σελίδα
# δείχνει σπασμένη. Δεκτά ΜΟΝΟ http/https.
_URL_FIELDS = {"facebook", "instagram", "gbp_url"}
_URL_OK = re.compile(r"^https?://[^\s<>\"']{3,}$", re.I)
# Σκόπιμα χαλαρό: δεν είναι δουλειά μας να κρίνουμε τι είναι έγκυρο email,
# αλλά ούτε να δεχόμαστε markup.
_EMAIL_OK = re.compile(r"^[^\s<>\"'@]{1,64}@[^\s<>\"'@]{3,255}$")


def _safe_url(value: str) -> str:
    """Το URL αν είναι http/https, αλλιώς κενό. Το κενό σημαίνει «δεν το δείχνουμε»."""
    v = (value or "").strip()
    return v if _URL_OK.match(v) else ""


# ── Κανονικοποίηση social ───────────────────────────────────────────────────
#
# ΤΙ ΕΣΠΑΣΕ. Ο φρουρός από πάνω δέχεται ΜΟΝΟ `^https?://`. Σωστό για το
# `javascript:` και το `data:`, καταστροφικό για τον πελάτη: το dashboard του
# λέει να γράψει «instagram.com/tomagazimou» (placeholder) και μετά το πετάει
# σιωπηλά. Το PUT γύριζε 200 με το πεδίο άδειο. ΜΕΤΡΗΘΗΚΕ σε staging: 27
# γραμμές `site_content`, **μηδέν** αποθηκευμένα social. Χάνονταν όλα.
#
# Ο ΦΡΟΥΡΟΣ ΔΕΝ ΧΑΛΑΡΩΝΕΙ. Ό,τι δηλώνει ρητά επικίνδυνο scheme απορρίπτεται με
# σφάλμα — δεν «διορθώνεται» σιωπηλά, γιατί ένα `javascript:` που μετατρέπεται
# σε `https://javascript:...` κρύβει την πρόθεση αντί να τη σταματά.
#
# ΓΙΑΤΙ ΕΛΕΓΧΟΥΜΕ ΚΑΙ ΤΟΝ HOST. Το `SocialLinks.jsx` αποδίδει αυτά τα πεδία με
# το ΕΙΚΟΝΙΔΙΟ της πλατφόρμας. Ένας σύνδεσμος με το γλυφικό του Instagram που
# οδηγεί αλλού είναι φορέας phishing — το εικονίδιο είναι ο ισχυρισμός. Άρα το
# πεδίο `instagram` καταλήγει μόνο σε Instagram, το `facebook` μόνο σε Facebook.
# Το `gbp_url` ΔΕΝ αλλάζει συμβόλαιο: μένει ελεύθερο http/https (Google Maps,
# short links, `g.page`) και συνεχίζει να περνά από το `_safe_url`.

_SOCIAL_HOSTS = {
    "instagram": ("instagram.com", ("instagram.com", "www.instagram.com")),
    "facebook": ("facebook.com", ("facebook.com", "www.facebook.com",
                                  "m.facebook.com", "fb.com", "www.fb.com")),
}
# Ό,τι μοιάζει με scheme. Πιάνεται ΠΡΙΝ από κάθε προσπάθεια διόρθωσης, ώστε
# ρητή επικίνδυνη πρόθεση να μη γίνει ποτέ «σχεδόν σωστό URL».
_HAS_SCHEME = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.I)
_HANDLE_OK = re.compile(r"^[A-Za-z0-9._\-]{1,60}$")
# Το τμήμα μετά τον host: διαδρομή/ερώτημα, χωρίς κενά και markup.
_PATH_OK = re.compile(r"^[^\s<>\"'\\]{0,200}$")


class SocialValueError(ValueError):
    """Μη ασφαλής ή ακατανόητη τιμή — ο πελάτης πρέπει να το μάθει."""


def normalize_social(field: str, value: str) -> str:
    """Επιστρέφει κανονικό HTTPS URL της πλατφόρμας, ή σηκώνει σφάλμα.

    Κενό μένει κενό (ο πελάτης έσβησε το πεδίο — έγκυρη πρόθεση).
    """
    raw = (value or "").strip().strip("​")
    if not raw:
        return ""
    canonical, allowed = _SOCIAL_HOSTS[field]
    label = field.capitalize()

    # 1) Ρητό scheme: μόνο http/https συνεχίζουν. Τίποτα άλλο δεν «διορθώνεται».
    m = _HAS_SCHEME.match(raw)
    if m:
        scheme = m.group(1).lower()
        if scheme not in ("http", "https"):
            raise SocialValueError(
                f"Το {label} δέχεται μόνο διεύθυνση {canonical}. "
                f"Γράψε π.χ. {canonical}/tomagazimou")
        rest = raw[m.end():].lstrip("/")
    else:
        # 2) @handle → το χτίζουμε εμείς.
        if raw.startswith("@"):
            handle = raw[1:]
            if not _HANDLE_OK.match(handle):
                raise SocialValueError(
                    f"Το όνομα χρήστη «{raw[:40]}» δεν είναι έγκυρο. "
                    f"Γράψε π.χ. @tomagazimou")
            return f"https://{canonical}/{handle}"
        rest = raw.lstrip("/")

    host, _, path = rest.partition("/")
    host = host.split("@")[-1].split(":")[0].lower().rstrip(".")

    # 3) Σκέτο όνομα χρήστη χωρίς host («tomagazimou»).
    if "." not in host:
        if not _HANDLE_OK.match(rest):
            raise SocialValueError(
                f"Δεν κατάλαβα το «{raw[:40]}». Γράψε {canonical}/tomagazimou "
                f"ή @tomagazimou")
        return f"https://{canonical}/{rest}"

    if host not in allowed:
        raise SocialValueError(
            f"Αυτή η διεύθυνση δεν είναι {label} ({host}). "
            f"Το πεδίο {label} δέχεται μόνο {canonical}.")
    if not _PATH_OK.match(path):
        raise SocialValueError(f"Η διεύθυνση {label} περιέχει μη έγκυρους χαρακτήρες.")
    if not path.strip("/"):
        raise SocialValueError(
            f"Λείπει το όνομα της σελίδας. Γράψε π.χ. {canonical}/tomagazimou")

    # `http://` αναβαθμίζεται σε `https://`: ο σύνδεσμος είναι δημόσιος και οι
    # δύο πλατφόρμες ούτως ή άλλως ανακατευθύνουν.
    return f"https://{host}/{path}"


def _safe_email(value: str) -> str:
    v = (value or "").strip()
    return v if _EMAIL_OK.match(v) else ""


def _theme_of(client_id: str, incoming: dict | None = None) -> str:
    """Το theme που θα ΙΣΧΥΕΙ μετά την αποθήκευση.

    Αν ο πελάτης αλλάζει ταυτόχρονα theme και παλέτα, κρίνουμε με το ΝΕΟ theme.
    Χωρίς αυτό, μια αλλαγή σε theme κατηγορίας C θα κουβαλούσε μαζί παλέτα που
    το νέο theme δεν υποστηρίζει.
    """
    if incoming and isinstance(incoming.get("template"), str):
        return incoming["template"]
    try:
        return db.get_selected_design(client_id) or ""
    except Exception:  # noqa: BLE001 - ποτέ να μη μπλοκάρει την αποθήκευση
        return ""

class ContentUpdate(BaseModel):
    content: dict
    # Ο δείκτης που πήρε ο client στο GET. Κενό = «γράψε ό,τι να 'ναι»
    # (παλιοί clients). Γεμάτο και ξεπερασμένο = 409.
    rev: str | None = None


@app.put("/clients/{client_id}/content")
def put_content(client_id: str, body: ContentUpdate,
                authorization: str | None = Header(default=None)):
    """Αποθηκεύει τις αλλαγές του πελάτη. Το site τις δείχνει αμέσως."""
    from . import premium_generator as pg
    auth.require_client_access(client_id, authorization)

    # Έλεγξε ΠΡΙΝ καθαρίσεις: αν ο client κρατά ξεπερασμένο αντίγραφο, η
    # εγγραφή θα έσβηνε αλλαγή που έκανε άλλη καρτέλα στο μεταξύ.
    if body.rev:
        current_rev = db.site_content_rev(client_id)
        if current_rev and body.rev != current_rev:
            raise HTTPException(409, "Το site άλλαξε από αλλού. Φόρτωσε ξανά "
                                     "για να μη χαθούν οι αλλαγές.")

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
        elif k == "palette":
            # Δεν αρκεί «είναι έγκυρη παλέτα». Πρέπει να είναι έγκυρη ΓΙΑ ΑΥΤΟ
            # ΤΟ THEME: 10 themes δεν παίρνουν παλέτα καθόλου (η αλλαγή είναι
            # αόρατη ή καταστρέφει την ταυτότητα) και 12 παίρνουν μόνο υποσύνολο.
            # Η απόκρυψη του control στο UI ΔΕΝ είναι επιβολή — εδώ είναι η πύλη.
            if v in {"original", "warm", "forest", "ocean", "rose", "mono"} \
                    and tcaps.is_allowed(_theme_of(client_id, body.content), "set_palette", v):
                clean[k] = v
        elif k == "font_pair":
            if v in {"editorial", "modern", "friendly", "classic"} \
                    and tcaps.is_allowed(_theme_of(client_id, body.content), "set_font_pair", v):
                clean[k] = v
        elif k in _SOCIAL_HOSTS and isinstance(v, str):
            # Μη κενή τιμή που δεν κανονικοποιείται ΔΕΝ γίνεται σιωπηλά κενή:
            # ο πελάτης πρέπει να μάθει ότι δεν αποθηκεύτηκε. 422, με μήνυμα
            # που λέει τι να γράψει.
            try:
                clean[k] = normalize_social(k, v)[:1200]
            except SocialValueError as e:
                raise HTTPException(422, str(e))
        elif k in _URL_FIELDS and isinstance(v, str):
            clean[k] = _safe_url(v)[:1200]
        elif k == "email" and isinstance(v, str):
            clean[k] = _safe_email(v)[:320]
        elif isinstance(v, str):
            clean[k] = v[:1200]

    # ΣΥΓΧΩΝΕΥΣΗ, όχι αντικατάσταση.
    #
    # Το `save_site_content` κάνει upsert ΟΛΟΚΛΗΡΟ το `content`. Επειδή εδώ
    # χτίζαμε το `clean` από το μηδέν, ό,τι δεν ήταν στο _EDITABLE έσβηνε.
    # ΜΕΤΡΗΘΗΚΕ σε staging: μετά από ένα απλό «Αποθήκευση» χάνονταν και τα έξι
    # κλειδιά που γράφει το /start — description, style, features, booking,
    # pricing, media_available. Το `description` είναι το καύσιμο του vertical
    # matching· χωρίς αυτό οι προτάσεις theme χειροτερεύουν σιωπηλά, και ο
    # πελάτης δεν έχει τρόπο να το ξαναγράψει από πουθενά.
    existing = {}
    try:
        existing = db.get_site_content(client_id) or {}
    except Exception as e:  # noqa: BLE001 — ποτέ να μη μπλοκάρει την αποθήκευση
        print(f"[content] merge base unavailable: {e}")
    merged = {**existing, **clean}
    if clean.get("address") or clean.get("city"):
        # νέα διεύθυνση → οι παλιές συντεταγμένες δεν ισχύουν πια
        merged.pop("geo_lat", None)
        merged.pop("geo_lng", None)
    db.save_site_content(client_id, merged)
    if clean.get("address") or clean.get("city"):
        _ensure_geo(client_id, clean.get("address", ""), clean.get("city", ""))
    if clean.get("template"):
        try:
            db.set_selected_design(client_id, clean["template"])
        except Exception as e:  # noqa: BLE001
            print(f"[content] template selection not persisted: {e}")
    return {"ok": True, "saved": sorted(clean.keys())}


@app.get("/clients/{client_id}/designs")
def list_designs(client_id: str,
                 authorization: str | None = Header(default=None),
                 x_vitrina_claim: str | None = Header(default=None)):
    """Οι προτάσεις design του πελάτη + ποια είναι προτεινόμενη/επιλεγμένη + live URL.

    `templates`: smart-match — 12 διαφορετικές, συμβατές React κατευθύνσεις
    (αυτά δείχνει το /choose). `variants`: τα legacy static layouts (συμβατότητα)."""
    auth.require_client_or_claim(client_id, authorization, x_vitrina_claim)
    from . import premium_generator as pg
    rid = _resolve_client(client_id).get("id", client_id)
    variants = db.list_site_variants(rid)
    selected = db.get_selected_design(rid)
    deployed_url = db.get_live_site(rid)
    # ΜΙΑ ΑΠΟΦΑΣΗ ΕΠΑΓΓΕΛΜΑΤΟΣ, ΜΙΑ ΦΟΡΑ.
    #
    # Πριν: `recommend_templates()` και `vertical_of()` καλούνταν ξεχωριστά, με
    # δύο ανεξάρτητες κλήσεις του `_vertical`. Όταν η απόφαση περνούσε από το AI
    # fallback (32% των εισόδων), οι δύο μπορούσαν να διαφωνήσουν — μετρήθηκε
    # ετικέτα «Τεχνικά επαγγέλματα» πάνω από themes δικηγορικού γραφείου.
    # Το intake διαβάζεται επίσης μία φορά αντί για δύο.
    vertical, vertical_label = "", ""
    templates = []
    try:
        intake = _intake_from_db(client_id)
        vertical, vertical_label = pg.vertical_of(intake)
        templates = pg.recommend_templates(intake, limit=12, vertical=vertical)
    except Exception as e:  # noqa: BLE001 — ποτέ να μη μπλοκάρει το choose
        print(f"[designs] smart-match skipped: {e}")
    return {"variants": variants, "templates": templates,
            "selected": selected, "deployed_url": deployed_url,
            "vertical": vertical, "vertical_label": vertical_label}


@app.get("/clients/{client_id}/preview/{layout}", response_class=HTMLResponse)
def preview_design(client_id: str, layout: str):
    """Σερβίρει το HTML μιας πρότασης design για preview στον πελάτη."""
    variant = db.get_site_variant(client_id, layout)
    if not variant:
        raise HTTPException(404, "Δεν βρέθηκε αυτό το design.")
    return HTMLResponse(variant["html"])


@app.post("/clients/{client_id}/select-design")
def select_design(client_id: str, sel: SelectDesign, bg: BackgroundTasks,
                  authorization: str | None = Header(default=None),
                  x_vitrina_claim: str | None = Header(default=None)):
    """Ο πελάτης πάτησε Approve — καταγράφει την επιλογή και ξεκινά deploy στο background."""
    auth.require_client_or_claim(client_id, authorization, x_vitrina_claim)
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
def add_client_asset(client_id: str, asset: ClientAsset,
                     authorization: str | None = Header(default=None),
                     x_vitrina_claim: str | None = Header(default=None)):
    """Αποθηκεύει στοιχεία/links/assets που δίνει ο πελάτης για site/social.
    MVP: metadata + URL/text. Binary uploads θα μπουν αργότερα με Supabase Storage."""
    auth.require_client_or_claim(client_id, authorization, x_vitrina_claim)
    if not asset.rights_ok:
        raise HTTPException(400, "Πρέπει να επιβεβαιωθούν τα δικαιώματα χρήσης του asset.")
    asset_id = db.save_client_asset(client_id, asset.model_dump())
    return {"asset_id": asset_id}


@app.get("/clients/{client_id}/assets")
def list_client_assets(client_id: str, usage: str | None = None,
                       authorization: str | None = Header(default=None),
                       x_vitrina_claim: str | None = Header(default=None)):
    auth.require_client_or_claim(client_id, authorization, x_vitrina_claim)
    return {"assets": db.get_client_assets(client_id, usage=usage)}


@app.delete("/clients/{client_id}/assets/{asset_id}")
def delete_client_asset(client_id: str, asset_id: str,
                        authorization: str | None = Header(default=None)):
    """Διαγράφει φωτογραφία του πελάτη. Χωρίς αυτό, ο πελάτης δεν μπορούσε να
    αφαιρέσει ΚΑΜΙΑ εικόνα μετά την αγορά χωρίς να μας γράψει."""
    client = auth.require_client_access(client_id, authorization)
    rid = client.get("id", client_id)
    if not db.delete_client_asset(rid, asset_id):
        raise HTTPException(404, "Η φωτογραφία δεν βρέθηκε.")
    return {"ok": True, "deleted": asset_id}

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


def _fb_error(r: requests.Response) -> str:
    """Το μήνυμα της Meta, χωρίς ΤΙΠΟΤΑ δικό μας μέσα."""
    try:
        e = r.json().get("error", {})
        return f"{e.get('message', r.text[:200])} (code {e.get('code')})"
    except ValueError:
        return f"HTTP {r.status_code}"


def _exchange(payload: dict) -> str:
    """Ανταλλαγή για token — με POST, ώστε το app secret να ΜΗΝ μπει σε URL.

    Με GET, το `requests` βάζει το secret στο query string· όταν σκάσει, το
    μήνυμα του σφάλματος περιέχει ολόκληρο το URL και το secret καταλήγει
    αυτούσιο στα logs του Railway. Έγινε ακριβώς αυτό στις 04/08.
    """
    r = requests.post(f"{GRAPH}/oauth/access_token", data=payload, timeout=20)
    if not r.ok:
        # 400 εδώ σημαίνει σχεδόν πάντα: το secret δεν ταιριάζει με το App ID,
        # ή το redirect_uri διαφέρει από αυτό του διαλόγου.
        raise HTTPException(400, f"Το Facebook απέρριψε τη σύνδεση: {_fb_error(r)}")
    token = r.json().get("access_token")
    if not token:
        raise HTTPException(400, "Το Facebook δεν επέστρεψε access token.")
    return token


@app.get("/connect/callback")
def callback(code: str | None = None, state: str | None = None,
             error: str | None = None):
    if error or not code:
        raise HTTPException(400, f"OAuth error: {error}")
    our_client_id = state

    # 1) code → short-lived user token
    short_token = _exchange({
        "client_id": cfg.META_APP_ID,
        "client_secret": cfg.META_APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    })

    # 2) short → long-lived user token (~60 μέρες)
    long_user_token = _exchange({
        "grant_type": "fb_exchange_token",
        "client_id": cfg.META_APP_ID,
        "client_secret": cfg.META_APP_SECRET,
        "fb_exchange_token": short_token,
    })

    # 3) Pages του χρήστη (το page token είναι long-lived αν ο user token είναι)
    # Το token πάει σε header, όχι σε query — αλλιώς καταλήγει στα logs.
    r = requests.get(f"{GRAPH}/me/accounts",
                     params={"fields": "id,name,access_token,instagram_business_account"},
                     headers={"Authorization": f"Bearer {long_user_token}"},
                     timeout=20)
    if not r.ok:
        raise HTTPException(400, f"Το Facebook δεν έδωσε τις Σελίδες: {_fb_error(r)}")
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
