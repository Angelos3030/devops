"""
Πρόσβαση στη βάση (Supabase). Λεπτό wrapper — κράτα το απλό.
"""

import json
from supabase import create_client
from . import config as cfg

_sb = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY) if cfg.SUPABASE_URL else None


def _client():
    if _sb is None:
        raise RuntimeError("Supabase δεν έχει ρυθμιστεί (SUPABASE_URL/KEY).")
    return _sb


def get_active_clients(plans: tuple[str, ...] = ("social", "premium")) -> list[dict]:
    res = (_client().table("clients")
           .select("*").eq("status", "active").in_("plan", list(plans)).execute())
    return res.data or []


def create_client(intake: dict) -> str:
    """Δημιουργεί πελάτη από τα στοιχεία της φόρμας. Επιστρέφει το client_id (uuid).

    intake keys (από connect.html): name, type, city, phone, style, description
    """
    row = {
        "name": intake.get("name") or "—",
        "business_type": intake.get("type") or intake.get("business_type") or "—",
        "city": intake.get("city") or "—",
        "phone": intake.get("phone"),
        "email": intake.get("email"),
        "status": "trial",
        "plan": "starter",
    }
    res = _client().table("clients").insert(row).execute()
    return res.data[0]["id"]


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


def save_post(client_id: str, caption: str, status: str = "published",
              image_url: str | None = None,
              fb_post_id: str | None = None,
              ig_post_id: str | None = None) -> None:
    _client().table("posts").insert({
        "client_id": client_id, "caption": caption,
        "image_url": image_url, "status": status,
        "fb_post_id": fb_post_id, "ig_post_id": ig_post_id,
    }).execute()


def save_site(client_id: str, url: str, preset: str, variant: int, html: str) -> None:
    _client().table("sites").insert({
        "client_id": client_id, "url": url, "preset": preset,
        "chosen_variant": variant, "html": html,
    }).execute()


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


def set_client_status(client_id: str, status: str, plan: str | None = None) -> None:
    patch = {"status": status}
    if plan:
        patch["plan"] = plan
    _client().table("clients").update(patch).eq("id", client_id).execute()


def get_client_by_stripe(customer_id: str) -> dict | None:
    res = (_client().table("subscriptions")
           .select("client_id").eq("stripe_customer_id", customer_id).limit(1).execute())
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
