"""
Δημοσίευση σε Facebook Page και Instagram Business μέσω Graph API.

Το OAuth αποθήκευε το page token και σταματούσε εκεί — τίποτα δεν δημοσίευε.
Αυτό είναι το κομμάτι που λείπει.

Δύο διαφορετικά APIs κάτω από το ίδιο όνομα:
  • Facebook  — μία κλήση· `/photos` αν υπάρχει εικόνα, αλλιώς `/feed`.
  • Instagram — ΔΥΟ κλήσεις (φτιάξε container → δημοσίευσε) και **απαιτεί**
    εικόνα. Δεν υπάρχει δημοσίευση μόνο με κείμενο στο Instagram.

Η εικόνα δίνεται ως **δημόσιο URL** — η Meta την κατεβάζει μόνη της, δεν
ανεβάζουμε bytes. Οι φωτογραφίες των πελατών μας είναι ήδη δημόσιες.

⚠️ Κάθε συνάρτηση εδώ κάνει ΠΡΑΓΜΑΤΙΚΗ δημοσίευση. Χρησιμοποίησε `dry_run=True`
για να δεις τι θα σταλεί χωρίς να σταλεί.
"""
from __future__ import annotations

from typing import Any

import requests

from . import db

GRAPH = "https://graph.facebook.com/v21.0"
TIMEOUT = 30


class PublishError(RuntimeError):
    """Η Meta απέρριψε τη δημοσίευση — το μήνυμα είναι δικό της, αυτούσιο."""


def _post(url: str, data: dict[str, Any]) -> dict:
    r = requests.post(url, data=data, timeout=TIMEOUT)
    if not r.ok:
        # Το σφάλμα της Meta λέει ακριβώς τι φταίει (permission, token, εικόνα).
        # Κρύβοντάς το θα ψάχναμε στα τυφλά.
        try:
            err = r.json().get("error", {})
            raise PublishError(f"{err.get('type', 'Error')}: {err.get('message', r.text[:200])}")
        except ValueError:
            raise PublishError(f"HTTP {r.status_code}: {r.text[:200]}") from None
    return r.json()


def publish_facebook(page_id: str, page_token: str, message: str,
                     image_url: str | None = None, dry_run: bool = False) -> dict:
    """Δημοσίευση σε Facebook Page. Με εικόνα → /photos, χωρίς → /feed."""
    if image_url:
        url = f"{GRAPH}/{page_id}/photos"
        data = {"url": image_url, "caption": message, "access_token": page_token}
    else:
        url = f"{GRAPH}/{page_id}/feed"
        data = {"message": message, "access_token": page_token}

    if dry_run:
        return {"dry_run": True, "endpoint": url.replace(GRAPH, ""),
                "fields": {k: v for k, v in data.items() if k != "access_token"}}

    res = _post(url, data)
    post_id = res.get("post_id") or res.get("id")
    return {"ok": True, "post_id": post_id,
            "url": f"https://www.facebook.com/{post_id}" if post_id else None}


def publish_instagram(ig_user_id: str, page_token: str, caption: str,
                      image_url: str, dry_run: bool = False) -> dict:
    """Δημοσίευση σε Instagram Business. Η εικόνα είναι ΥΠΟΧΡΕΩΤΙΚΗ."""
    if not image_url:
        raise PublishError("Το Instagram δεν δέχεται δημοσίευση χωρίς εικόνα.")

    create_url = f"{GRAPH}/{ig_user_id}/media"
    create_data = {"image_url": image_url, "caption": caption, "access_token": page_token}
    if dry_run:
        return {"dry_run": True, "endpoint": f"/{ig_user_id}/media → /media_publish",
                "fields": {"image_url": image_url, "caption": caption}}

    creation_id = _post(create_url, create_data).get("id")
    if not creation_id:
        raise PublishError("Η Meta δεν επέστρεψε creation_id.")

    res = _post(f"{GRAPH}/{ig_user_id}/media_publish",
                {"creation_id": creation_id, "access_token": page_token})
    media_id = res.get("id")
    return {"ok": True, "media_id": media_id,
            "url": f"https://www.instagram.com/p/{media_id}" if media_id else None}


def publish(client_id: str, message: str, image_url: str | None = None,
            targets: list[str] | None = None, dry_run: bool = False) -> dict:
    """Δημοσιεύει για έναν πελάτη σε όσα δίκτυα έχει συνδέσει.

    Κάθε δίκτυο αναφέρεται χωριστά: αν το Instagram αποτύχει (π.χ. λείπει
    εικόνα), το Facebook έχει ήδη δημοσιευτεί και δεν το ακυρώνουμε — ο πελάτης
    πρέπει να ξέρει τι βγήκε και τι όχι, όχι ένα σκέτο «απέτυχε».
    """
    creds = db.get_social_creds(client_id)
    if not creds:
        raise PublishError("Ο πελάτης δεν έχει συνδέσει λογαριασμό Facebook.")

    wanted = targets or ["facebook", "instagram"]
    out: dict[str, Any] = {"dry_run": dry_run, "results": {}}

    if "facebook" in wanted:
        try:
            out["results"]["facebook"] = publish_facebook(
                creds["page_id"], creds["page_token"], message, image_url, dry_run)
        except PublishError as e:
            out["results"]["facebook"] = {"ok": False, "error": str(e)}

    if "instagram" in wanted:
        if not creds.get("ig_user_id"):
            out["results"]["instagram"] = {
                "ok": False, "error": "Δεν υπάρχει συνδεδεμένος λογαριασμός Instagram Business."}
        else:
            try:
                out["results"]["instagram"] = publish_instagram(
                    creds["ig_user_id"], creds["page_token"], message, image_url or "", dry_run)
            except PublishError as e:
                out["results"]["instagram"] = {"ok": False, "error": str(e)}

    return out
