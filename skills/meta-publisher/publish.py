"""
publish.py — Δημοσίευση σε Facebook Page & Instagram Business (direct Graph API).

Λειτουργικό για MVP. Χρειάζεται: page_token + page_id (+ ig_user_id για Instagram),
που τα παίρνεις από το OAuth flow (src/meta_oauth.py).

Εναλλακτικά μπορείς να ποστάρεις μέσω Meta MCP (ο agent καλεί τα tools) — τότε αυτό
το αρχείο δεν χρειάζεται. Διάλεξε ΕΝΑ μονοπάτι.

IG note: το image_url πρέπει να είναι ΔΗΜΟΣΙΑ προσβάσιμο URL (το Graph API το κατεβάζει).
"""

import time
import requests
from dataclasses import dataclass, field

GRAPH = "https://graph.facebook.com/v21.0"


@dataclass
class Post:
    caption: str
    hashtags: list[str] = field(default_factory=list)
    image_url: str | None = None      # IG απαιτεί εικόνα (δημόσιο URL)


def build_caption(post: Post) -> str:
    tags = " ".join(post.hashtags)
    return f"{post.caption}\n\n{tags}".strip()


def publish_facebook(page_id: str, page_token: str, post: Post) -> str:
    """FB: εικόνα (αν υπάρχει) αλλιώς κείμενο. Επιστρέφει post_id."""
    text = build_caption(post)
    if post.image_url:
        r = requests.post(f"{GRAPH}/{page_id}/photos", data={
            "url": post.image_url, "caption": text, "access_token": page_token,
        }, timeout=30)
    else:
        r = requests.post(f"{GRAPH}/{page_id}/feed", data={
            "message": text, "access_token": page_token,
        }, timeout=30)
    r.raise_for_status()
    return r.json().get("post_id") or r.json().get("id")


def publish_instagram(ig_user_id: str, page_token: str, post: Post) -> str:
    """IG: 2 βήματα (container → publish). Απαιτεί εικόνα. Επιστρέφει media id."""
    if not post.image_url:
        raise ValueError("Το Instagram απαιτεί εικόνα (δημόσιο URL).")
    # 1) media container
    r = requests.post(f"{GRAPH}/{ig_user_id}/media", data={
        "image_url": post.image_url,
        "caption": build_caption(post),
        "access_token": page_token,
    }, timeout=30)
    r.raise_for_status()
    creation_id = r.json()["id"]

    # 2) publish (μικρή αναμονή για επεξεργασία εικόνας)
    time.sleep(3)
    r = requests.post(f"{GRAPH}/{ig_user_id}/media_publish", data={
        "creation_id": creation_id, "access_token": page_token,
    }, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


def publish_all(creds: dict, post: Post) -> dict:
    """
    creds = {"page_id":..., "page_token":..., "ig_user_id":...(προαιρετικό)}
    Επιστρέφει αποτέλεσμα ανά πλατφόρμα (post_id ή error).
    """
    result: dict[str, str] = {}
    try:
        result["facebook"] = publish_facebook(
            creds["page_id"], creds["page_token"], post)
    except Exception as e:
        result["facebook"] = f"error: {e}"
    if creds.get("ig_user_id"):
        try:
            result["instagram"] = publish_instagram(
                creds["ig_user_id"], creds["page_token"], post)
        except Exception as e:
            result["instagram"] = f"error: {e}"
    return result
