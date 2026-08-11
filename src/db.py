"""
Πρόσβαση στη βάση (Supabase). Λεπτό wrapper — κράτα το απλό.
"""

import json
from datetime import datetime, timedelta, timezone
from supabase import create_client
from . import config as cfg

_sb = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY) if cfg.SUPABASE_URL else None


def _client():
    if _sb is None:
        from . import env
        raise RuntimeError(
            f"Supabase δεν έχει ρυθμιστεί. {env.banner()}\n"
            f"Χρειάζεται SUPABASE_URL_{'PRODUCTION' if env.is_production else 'STAGING'} "
            f"και το αντίστοιχο KEY."
        )
    return _sb


def _one(data: list[dict] | None) -> dict | None:
    return data[0] if data else None


# --- Stage 4A Agency Kernel -----------------------------------------------
# Thin persistence only. Admission/policy decisions live in agency_kernel.py.

def list_plan_capabilities(plan_key: str) -> list[dict]:
    return (_client().table("plan_capabilities").select("*")
            .eq("plan_key", plan_key).execute().data or [])


def list_workspace_entitlements(workspace_id: str) -> list[dict]:
    return (_client().table("workspace_entitlements").select("*")
            .eq("workspace_id", workspace_id).execute().data or [])


def list_agent_installations(workspace_id: str) -> list[dict]:
    return (_client().table("agent_installations").select("*")
            .eq("workspace_id", workspace_id).order("installed_at").execute().data or [])


def list_agency_actions(workspace_id: str, limit: int = 50) -> list[dict]:
    return (_client().table("agency_action_queue").select("*")
            .eq("workspace_id", workspace_id).order("updated_at", desc=True)
            .limit(limit).execute().data or [])


def get_agent_approval(workspace_id: str, approval_id: str) -> dict | None:
    res = (_client().table("agent_approvals").select("*")
           .eq("workspace_id", workspace_id).eq("id", approval_id).limit(1).execute())
    return _one(res.data)


def decide_agent_approval(workspace_id: str, approval_id: str, *,
                          status: str, decided_by: str,
                          reason: str | None = None) -> dict | None:
    """Atomic-enough optimistic decision: only a pending approval may change."""
    res = (_client().table("agent_approvals").update({
        "status": status,
        "decided_by": decided_by,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "decision_reason": reason,
    }).eq("workspace_id", workspace_id).eq("id", approval_id)
      .eq("status", "pending").execute())
    return _one(res.data)


def append_agency_audit(row: dict) -> str:
    res = _client().table("agency_audit_log").insert(row).execute()
    return res.data[0]["id"]


def get_active_clients(plans: tuple[str, ...] = ("social", "premium")) -> list[dict]:
    res = (_client().table("clients")
           .select("*").eq("status", "active").in_("plan", list(plans)).execute())
    return res.data or []


def create_client(intake: dict) -> str:
    """Δημιουργεί πελάτη από τα στοιχεία της φόρμας. Επιστρέφει το client_id (uuid).

    intake keys (από connect.html): name, type, city, phone, style, description
    """
    # ΠΟΤΕ «—» για ό,τι λείπει. Οι στήλες είναι NOT NULL με default '' — η παύλα
    # δεν χρειαζόταν ποτέ, και περνούσε στη σελίδα ως δεδομένο: «Ξενοδοχείο · —»,
    # «📞 —», «Εξυπηρετούμε: —», και χάρτης που έψαχνε «—, Ελλάδα». Το κενό είναι
    # η ειλικρινής τιμή: τα templates ξέρουν να κρύβουν ενότητα που δεν έχει στοιχεία.
    row = {
        "name": intake.get("name") or "",
        "business_type": intake.get("type") or intake.get("business_type") or "",
        "city": intake.get("city") or "",
        "phone": intake.get("phone"),
        "email": intake.get("email"),
        "status": "trial",
        "plan": "starter",
    }
    res = _client().table("clients").insert(row).execute()
    return res.data[0]["id"]


def delete_client(client_id: str) -> None:
    """Διαγράφει πελάτη (cascade: site_variants/assets/domains μέσω FK on delete cascade).
    Χρήσιμο για test cleanup και για GDPR data deletion."""
    _client().table("clients").delete().eq("id", client_id).execute()


def get_brand_profile(client_id: str) -> dict | None:
    res = (_client().table("brand_profiles")
           .select("profile").eq("client_id", client_id).limit(1).execute())
    return (res.data[0]["profile"] if res.data else None)


def save_brand_profile(client_id: str, profile: dict) -> None:
    _client().table("brand_profiles").upsert(
        {"client_id": client_id, "profile": profile}).execute()


def save_social_creds(client_id: str, page_id: str,
                      page_token: str, ig_user_id: str | None) -> None:
    """Αποθηκεύει Meta credentials από το OAuth callback.
    ⚠️ page_token: ΜΗΝ το logάρεις — κρυπτογράφησε σε production."""
    _client().table("social_accounts").upsert({
        "client_id": client_id,
        "fb_page_id": page_id,
        "page_token": page_token,
        "ig_user_id": ig_user_id,
    }).execute()


def get_social_creds(client_id: str) -> dict | None:
    """Επιστρέφει {"page_id", "page_token", "ig_user_id"} ή None αν δεν έχει συνδεθεί."""
    res = (_client().table("social_accounts")
           .select("fb_page_id,page_token,ig_user_id")
           .eq("client_id", client_id).limit(1).execute())
    if not res.data:
        return None
    row = res.data[0]
    return {
        "page_id": row["fb_page_id"],
        "page_token": row["page_token"],
        "ig_user_id": row.get("ig_user_id"),
    }


def save_post(client_id: str, caption: str, status: str = "pending_approval",
              image_url: str | None = None,
              fb_post_id: str | None = None,
              ig_post_id: str | None = None,
              targets: list[str] | None = None,
              scheduled_for: str | None = None,
              approval_required: bool = True) -> str:
    res = _client().table("posts").insert({
        "client_id": client_id, "caption": caption,
        "image_url": image_url, "status": status,
        "fb_post_id": fb_post_id, "ig_post_id": ig_post_id,
        "targets": targets or ["facebook", "instagram"],
        "scheduled_for": scheduled_for,
        "approval_required": approval_required,
    }).execute()
    return res.data[0]["id"]


def get_post(client_id: str, post_id: str) -> dict | None:
    res = (_client().table("posts").select("*")
           .eq("id", post_id).eq("client_id", client_id).limit(1).execute())
    return res.data[0] if res.data else None


def list_posts(client_id: str, status: str | None = None, limit: int = 50) -> list[dict]:
    q = (_client().table("posts").select("*").eq("client_id", client_id)
         .order("created_at", desc=True).limit(limit))
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


def approve_post(client_id: str, post_id: str, approved_by: str,
                 scheduled_for: str | None = None) -> dict | None:
    when = scheduled_for or datetime.now(timezone.utc).isoformat()
    res = (_client().table("posts").update({
        "status": "scheduled", "approved_at": datetime.now(timezone.utc).isoformat(),
        "approved_by": approved_by, "scheduled_for": when, "last_error": None,
    }).eq("id", post_id).eq("client_id", client_id)
      .in_("status", ["draft", "pending_approval", "failed"]).execute())
    return res.data[0] if res.data else None


def reject_post(client_id: str, post_id: str) -> dict | None:
    res = (_client().table("posts").update({
        "status": "rejected", "rejected_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", post_id).eq("client_id", client_id)
      .in_("status", ["draft", "pending_approval", "scheduled"]).execute())
    return res.data[0] if res.data else None


def due_posts(limit: int = 25) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return (_client().table("posts").select("*").eq("status", "scheduled")
            .lte("scheduled_for", now).order("scheduled_for").limit(limit).execute().data or [])


def claim_post(post_id: str) -> dict | None:
    """Optimistic claim: only a still-scheduled row can become publishing."""
    res = (_client().table("posts").update({"status": "publishing"})
           .eq("id", post_id).eq("status", "scheduled").execute())
    return res.data[0] if res.data else None


def finish_post(post_id: str, *, status: str, attempts: int,
                fb_post_id: str | None = None, ig_post_id: str | None = None,
                error: str | None = None, scheduled_for: str | None = None) -> None:
    patch = {"status": status, "attempts": attempts, "last_error": error}
    if status == "published":
        patch["published_at"] = datetime.now(timezone.utc).isoformat()
    if fb_post_id:
        patch["fb_post_id"] = fb_post_id
    if ig_post_id:
        patch["ig_post_id"] = ig_post_id
    if scheduled_for:
        patch["scheduled_for"] = scheduled_for
    _client().table("posts").update(patch).eq("id", post_id).execute()


def save_publish_log(post_id: str, client_id: str, *, dry_run: bool,
                     success: bool, result: dict, error: str | None = None) -> None:
    _client().table("publish_logs").insert({
        "post_id": post_id, "client_id": client_id, "dry_run": dry_run,
        "success": success, "result": result, "error": error,
    }).execute()


def save_site(client_id: str, url: str, preset: str, variant: int, html: str) -> None:
    _client().table("sites").insert({
        "client_id": client_id, "url": url, "preset": preset,
        "chosen_variant": variant, "html": html,
    }).execute()


# --- Design variants -------------------------------------------------------
# Αποθηκεύονται στον υπάρχοντα πίνακα `sites` (χωρίς νέα migration/DDL):
#   preset = layout, html = HTML, chosen_variant = 1 αν recommended αλλιώς 0,
#   url = 'preview' | 'selected'  (τα deployed live sites έχουν πραγματικό http url
#   και εξαιρούνται από τα παρακάτω queries μέσω του φίλτρου url in (preview,selected)).
_VARIANT_URLS = ["preview", "selected"]


def _variant_status(url: str | None) -> str:
    return "selected" if url == "selected" else "preview"


def save_site_variant(client_id: str, layout: str, html: str,
                      recommended: bool = False) -> None:
    """Αποθηκεύει μία από τις 3 προτάσεις design (studio/commerce/atelier).
    Καθαρίζει προηγούμενο preview ίδιου layout ώστε το regenerate να μη διπλασιάζει."""
    tbl = _client().table("sites")
    tbl.delete().eq("client_id", client_id).eq("preset", layout).in_("url", _VARIANT_URLS).execute()
    tbl.insert({"client_id": client_id, "preset": layout, "html": html,
                "chosen_variant": 1 if recommended else 0, "url": "preview"}).execute()


def get_site_variant(client_id: str, layout: str) -> dict | None:
    res = (_client().table("sites")
           .select("preset,html,chosen_variant,url,created_at")
           .eq("client_id", client_id).eq("preset", layout).in_("url", _VARIANT_URLS)
           .order("created_at", desc=True).limit(1).execute())
    if not res.data:
        return None
    r = res.data[0]
    return {"layout": r["preset"], "html": r["html"],
            "recommended": bool(r.get("chosen_variant")), "status": _variant_status(r.get("url"))}


def list_site_variants(client_id: str) -> list[dict]:
    res = (_client().table("sites")
           .select("preset,chosen_variant,url")
           .eq("client_id", client_id).in_("url", _VARIANT_URLS).execute())
    return [{"layout": r["preset"], "recommended": bool(r.get("chosen_variant")),
             "status": _variant_status(r.get("url"))} for r in (res.data or [])]


def set_selected_design(client_id: str, layout: str) -> None:
    """Ο πελάτης πάτησε Approve. Μαρκάρει το επιλεγμένο variant (url='selected').

    Τα premium React templates δεν έχουν αποθηκευμένο static HTML — σε αυτή την
    περίπτωση γράφουμε marker row, ώστε η επιλογή να διατηρείται κανονικά."""
    tbl = _client().table("sites")
    # reset τυχόν προηγούμενη επιλογή, μετά μαρκάρισε τη νέα
    tbl.update({"url": "preview"}).eq("client_id", client_id).eq("url", "selected").execute()
    res = tbl.update({"url": "selected"}).eq("client_id", client_id).eq("preset", layout).in_(
        "url", _VARIANT_URLS).execute()
    if not (res.data or []):  # React-only template → κράτα την επιλογή ως marker
        tbl.insert({"client_id": client_id, "preset": layout, "html": "",
                    "chosen_variant": 1, "url": "selected"}).execute()


def get_selected_design(client_id: str) -> str | None:
    res = (_client().table("sites").select("preset")
           .eq("client_id", client_id).eq("url", "selected").limit(1).execute())
    return (res.data[0]["preset"] if res.data else None)


def get_client(client_id: str) -> dict | None:
    """Ένα client record (για site-data reconstruction στο Next.js render)."""
    res = (_client().table("clients").select("*").eq("id", client_id).limit(1).execute())
    return res.data[0] if res.data else None


def get_client_by_domain(domain: str) -> dict | None:
    """Βρίσκει πελάτη από custom domain (domains table) — για multi-tenant routing."""
    res = (_client().table("domains").select("client_id")
           .eq("domain", domain).limit(1).execute())
    if not res.data:
        return None
    return get_client(res.data[0]["client_id"])


def get_site_content(client_id: str) -> dict:
    """Οι αλλαγές που έκανε ο πελάτης από το dashboard (υπερισχύουν των defaults)."""
    res = (_client().table("site_content").select("content")
           .eq("client_id", client_id).limit(1).execute())
    return (res.data[0].get("content") or {}) if res.data else {}


def save_site_content(client_id: str, content: dict) -> None:
    """Αποθηκεύει (upsert) τις αλλαγές του πελάτη."""
    from datetime import datetime, timezone
    (_client().table("site_content").upsert({
        "client_id": client_id,
        "content": content,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute())


def get_clients_by_email(email: str) -> list[dict]:
    """Οι πελάτες που ανήκουν σε ένα email (σύνδεση dashboard login → client record).
    Το selected design κρατιέται στο `sites` (url='selected'), όχι σε στήλη clients."""
    res = (_client().table("clients")
           .select("id,name,business_type,city,status")
           .eq("email", email).execute())
    return res.data or []


def create_client_claim(client_id: str, token_hash: str, *, ttl_hours: int = 24) -> None:
    """Persist a short-lived, hashed ownership token for a newly generated site."""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
    (_client().table("client_site_claims").upsert({
        "client_id": client_id,
        "token_hash": token_hash,
        "expires_at": expires_at.isoformat(),
        "claimed_at": None,
        "claimed_by": None,
    }, on_conflict="client_id").execute())


def valid_client_claim(client_id: str, token_hash: str) -> bool:
    """Return whether an unclaimed, unexpired onboarding token owns this site."""
    if not client_id or not token_hash:
        return False
    result = (_client().table("client_site_claims")
              .select("id")
              .eq("client_id", client_id)
              .eq("token_hash", token_hash)
              .is_("claimed_at", "null")
              .gt("expires_at", datetime.now(timezone.utc).isoformat())
              .limit(1).execute())
    return bool(result.data)


def claim_client_site(client_id: str, token_hash: str, email: str) -> bool:
    """Atomically attach a generated site to its authenticated owner."""
    result = _client().rpc("claim_client_site", {
        "p_client_id": client_id,
        "p_token_hash": token_hash,
        "p_email": email.strip().lower(),
    }).execute()
    return result.data is True


def get_live_site(client_id: str) -> str | None:
    """Το live URL του deployed site (row στο `sites` με πραγματικό http url)."""
    res = (_client().table("sites").select("url,created_at")
           .eq("client_id", client_id).like("url", "http%")
           .order("created_at", desc=True).limit(1).execute())
    return (res.data[0]["url"] if res.data else None)


def save_client_asset(client_id: str, asset: dict) -> str:
    """Αποθηκεύει asset metadata/URL/κείμενο που δίνει ο πελάτης για site/social."""
    row = {
        "client_id": client_id,
        "type": asset.get("type") or "other",
        "title": asset.get("title"),
        "content": asset.get("content"),
        "url": asset.get("url"),
        "usage": asset.get("usage") or "site",
        "rights_ok": bool(asset.get("rights_ok")),
    }
    res = _client().table("client_assets").insert(row).execute()
    return res.data[0]["id"]


def get_client_assets(client_id: str, usage: str | None = None) -> list[dict]:
    q = _client().table("client_assets").select("*").eq("client_id", client_id)
    if usage:
        q = q.in_("usage", [usage, "all"])
    res = q.execute()
    return res.data or []


def upload_to_storage(client_id: str, filename: str,
                      data: bytes, content_type: str) -> str:
    """
    Ανεβάζει αρχείο στο Supabase Storage bucket 'client-assets'.
    Επιστρέφει public URL.
    Πρώτα: Supabase Dashboard → Storage → New bucket → 'client-assets' (public).
    """
    import mimetypes
    path = f"{client_id}/{filename}"
    _client().storage.from_("client-assets").upload(
        path, data, {"content-type": content_type, "upsert": "true"}
    )
    return _client().storage.from_("client-assets").get_public_url(path)


def save_domain(client_id: str, domain: str, zone_id: str | None = None) -> None:
    _client().table("domains").upsert({
        "client_id": client_id,
        "domain": domain,
        "cloudflare_zone_id": zone_id,
        "status": "active",
    }).execute()


def get_domain(client_id: str) -> dict | None:
    res = (_client().table("domains")
           .select("domain,cloudflare_zone_id,status")
           .eq("client_id", client_id).limit(1).execute())
    return res.data[0] if res.data else None


def create_domain_order(client_id: str, domain: str,
                        amount_cents: int = 2400,
                        currency: str = "eur") -> str:
    res = _client().table("domain_orders").insert({
        "client_id": client_id,
        "domain": domain,
        "amount_cents": amount_cents,
        "currency": currency,
        "status": "pending",
    }).execute()
    return res.data[0]["id"]


def set_domain_order_checkout(order_id: str, stripe_session_id: str) -> None:
    _client().table("domain_orders").update({
        "stripe_session_id": stripe_session_id,
        "status": "checkout_created",
    }).eq("id", order_id).execute()


def get_domain_order_by_session(stripe_session_id: str) -> dict | None:
    res = (_client().table("domain_orders")
           .select("*").eq("stripe_session_id", stripe_session_id).limit(1).execute())
    return res.data[0] if res.data else None


def update_domain_order_status(stripe_session_id: str, status: str,
                               error: str | None = None) -> None:
    patch = {"status": status}
    if error is not None:
        patch["error"] = error
    _client().table("domain_orders").update(patch).eq(
        "stripe_session_id", stripe_session_id
    ).execute()


def list_domain_orders(status: str | None = None, limit: int = 50) -> list[dict]:
    """Παραγγελίες domain. Χωρίς `status` επιστρέφει τις πιο πρόσφατες όλων."""
    q = (_client().table("domain_orders")
         .select("id,client_id,domain,status,amount_cents,error,created_at")
         .order("created_at", desc=True).limit(limit))
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


def set_client_status(client_id: str, status: str, plan: str | None = None) -> None:
    patch = {"status": status}
    if plan:
        patch["plan"] = plan
    _client().table("clients").update(patch).eq("id", client_id).execute()


def get_client_by_stripe(customer_id: str) -> dict | None:
    res = (_client().table("subscriptions")
           .select("client_id").eq("stripe_customer_id", customer_id).limit(1).execute())
    return (res.data[0] if res.data else None)


def get_subscription(client_id: str) -> dict | None:
    """Η συνδρομή ενός πελάτη (για dashboard: κατάσταση + Stripe portal)."""
    res = (_client().table("subscriptions")
           .select("stripe_customer_id,stripe_sub_id,plan,status")
           .eq("client_id", client_id).limit(1).execute())
    return (res.data[0] if res.data else None)


def upsert_subscription(client_id: str, stripe_customer_id: str,
                        stripe_sub_id: str, plan: str, status: str) -> None:
    _client().table("subscriptions").upsert({
        "client_id": client_id,
        "stripe_customer_id": stripe_customer_id,
        "stripe_sub_id": stripe_sub_id,
        "plan": plan,
        "status": status,
    }).execute()


def link_client_email(client_id: str, email: str) -> str:
    """Συνδέει τον πελάτη με το email αγοράς — από αυτό εξαρτάται ΟΛΟ το login.

    Το `/clients/lookup` βρίσκει τα sites του χρήστη με `clients.email == email`.
    Η ροή «site first» (`POST /start`) δημιουργεί πελάτη ΧΩΡΙΣ email, οπότε χωρίς
    αυτό το βήμα ο πελάτης πληρώνει και μετά βλέπει άδειο dashboard για πάντα.

    Idempotent: αν υπάρχει ήδη το ίδιο email δεν γράφει. Δεν αντικαθιστά έγκυρο
    διαφορετικό email — ο πελάτης μπορεί να πλήρωσε με άλλο (π.χ. εταιρικό) και
    δεν θέλουμε να του κόψουμε την πρόσβαση που ήδη δουλεύει.

    Επιστρέφει: 'linked' | 'already' | 'kept-existing' | 'skipped'
    """
    email = (email or "").strip().lower()
    if not client_id or "@" not in email:
        return "skipped"
    try:
        rows = _client().table("clients").select("email").eq("id", client_id).execute().data
    except Exception as e:  # noqa: BLE001 — ποτέ μη ρίξεις το webhook
        print(f"[link_email] read failed: {e}")
        return "skipped"
    if not rows:
        return "skipped"

    current = (rows[0].get("email") or "").strip().lower()
    if current == email:
        return "already"
    if current and "@" in current:
        print(f"[link_email] {client_id}: κρατάω το υπάρχον {current}, δεν γράφω {email}")
        return "kept-existing"
    try:
        _client().table("clients").update({"email": email}).eq("id", client_id).execute()
        print(f"[link_email] {client_id} → {email}")
        return "linked"
    except Exception as e:  # noqa: BLE001
        print(f"[link_email] write failed: {e}")
        return "skipped"


def delete_client_asset(client_id: str, asset_id: str) -> bool:
    """Διαγράφει asset — ΜΟΝΟ αν ανήκει σε αυτόν τον πελάτη.

    Ο έλεγχος ιδιοκτησίας γίνεται εδώ και όχι στο endpoint: αλλιώς ένα λάθος
    σε οποιοδήποτε μελλοντικό call site θα επέτρεπε σε πελάτη να σβήσει
    φωτογραφία άλλου. Επιστρέφει False αν δεν βρέθηκε/δεν ανήκει.
    """
    if not client_id or not asset_id:
        return False
    res = (_client().table("client_assets").delete()
           .eq("id", asset_id).eq("client_id", client_id).execute())
    return bool(res.data)
