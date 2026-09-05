"""
Έλεγχος ταυτότητας πελάτη για το dashboard.

Ο πελάτης συνδέεται στο frontend με Supabase Auth (Google ή magic link) και
στέλνει το access token ως `Authorization: Bearer <token>`. Εδώ:

  1. επαληθεύουμε το token στο Supabase Auth API (`/auth/v1/user`) — δεν χρειάζεται
     JWT secret, και ένα ανακληθέν token απορρίπτεται αμέσως·
  2. ελέγχουμε ότι το email του χρήστη αντιστοιχεί στον πελάτη που ζητάει.

Ό,τι αφορά δεδομένα πελάτη ΠΡΕΠΕΙ να περνάει από `require_client_access`.
"""
from __future__ import annotations

import hashlib
import time

import requests
from fastapi import HTTPException

from . import config as cfg
from . import db

_CACHE: dict[str, tuple[float, str]] = {}   # token → (expires_at, email)
_CACHE_TTL = 120  # δευτ. — αρκετά μικρό ώστε ένα logout να μετράει γρήγορα


def _user_email_from_token(token: str) -> str:
    """Το email του συνδεδεμένου χρήστη, ή HTTPException 401."""
    now = time.time()
    hit = _CACHE.get(token)
    if hit and hit[0] > now:
        return hit[1]

    if not cfg.SUPABASE_URL:
        raise HTTPException(500, "Auth δεν έχει ρυθμιστεί (SUPABASE_URL).")
    try:
        r = requests.get(
            f"{cfg.SUPABASE_URL.rstrip('/')}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": cfg.SUPABASE_KEY},
            timeout=10,
        )
    except Exception as e:  # noqa: BLE001 — δίκτυο
        raise HTTPException(503, f"Δεν μπόρεσα να επαληθεύσω τη σύνδεση: {e}")

    if r.status_code != 200:
        raise HTTPException(401, "Μη έγκυρη ή ληγμένη σύνδεση. Συνδέσου ξανά.")
    email = (r.json() or {}).get("email") or ""
    if not email:
        raise HTTPException(401, "Ο λογαριασμός δεν έχει email.")

    _CACHE[token] = (now + _CACHE_TTL, email.lower())
    if len(_CACHE) > 500:  # απλό κλάδεμα
        for k in [k for k, v in list(_CACHE.items()) if v[0] < now]:
            _CACHE.pop(k, None)
    return email.lower()


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Χρειάζεται σύνδεση.")
    return authorization.split(" ", 1)[1].strip()


def current_email(authorization: str | None) -> str:
    """Το email του συνδεδεμένου χρήστη (401 αν δεν είναι συνδεδεμένος)."""
    return _user_email_from_token(_bearer(authorization))


def require_client_access(client_id: str, authorization: str | None) -> dict:
    """Επιστρέφει το client record ΜΟΝΟ αν ο συνδεδεμένος χρήστης το κατέχει."""
    email = current_email(authorization)
    client = db.get_client(client_id)
    if not client:
        raise HTTPException(404, "Δεν βρέθηκε ο πελάτης.")
    owner = (client.get("email") or "").lower()
    if not owner or owner != email:
        # Ίδιο μήνυμα με το 404 ώστε να μη διαρρέει ποιοι πελάτες υπάρχουν.
        raise HTTPException(404, "Δεν βρέθηκε ο πελάτης.")
    return client


def require_client_or_claim(client_id: str, authorization: str | None,
                            claim_token: str | None) -> dict:
    """Ιδιοκτήτης Ή η ανώνυμη συνεδρία που δημιούργησε αυτό το site.

    ΓΙΑΤΙ ΥΠΑΡΧΕΙ. Το funnel είναι site-first: ο επισκέπτης περιγράφει την
    επιχείρησή του, το site φτιάχνεται και ΜΕΤΑ κάνει λογαριασμό. Στο ενδιάμεσο
    δεν υπάρχει χρήστης — άρα το `require_client_access` θα έκοβε τη ροή.

    Πέντε endpoints έμεναν γι' αυτόν τον λόγο ΕΝΤΕΛΩΣ αφύλακτα. Μετρήθηκε:
    ένα `POST /clients/<ξένο id>/select-design` χωρίς κανένα header άλλαξε το
    theme άλλου πελάτη και σκανδάλισε deploy. Η ανωνυμία της ροής δεν
    δικαιολογεί ανωνυμία της ΤΑΥΤΟΤΗΤΑΣ: η συνεδρία κρατά ήδη μυστικό
    claim token 32+ χαρακτήρων. Αυτό είναι το διαπιστευτήριο.
    """
    token = (claim_token or "").strip()
    if len(token) >= 32:
        digest = hashlib.sha256(token.encode()).hexdigest()
        try:
            if db.valid_client_claim(client_id, digest):
                return db.get_client(client_id) or {"id": client_id}
        except Exception as exc:            # η βάση δεν αποφασίζει πρόσβαση
            print(f"[auth] claim check {client_id}: {exc}")
    return require_client_access(client_id, authorization)
