"""
Γεωκωδικοποίηση διεύθυνσης → συντεταγμένες (για LocalBusiness `geo` + χάρτη).

Χρησιμοποιεί το Nominatim του OpenStreetMap: δωρεάν, χωρίς κλειδί. Όροι χρήσης:
ένα request/δευτ. και σαφές User-Agent — τα τηρούμε, και το αποτέλεσμα το
αποθηκεύουμε ώστε να μη ξαναρωτάμε για τον ίδιο πελάτη.

Το `geo` με 5+ δεκαδικά είναι από τα σήματα που ζητά η Google για τοπικές
επιχειρήσεις (βλ. seo-local checklist).
"""
from __future__ import annotations

import time

import requests

_UA = "VitrinaGR/1.0 (+https://getvitrina.gr; hello@getvitrina.gr)"
_ENDPOINT = "https://nominatim.openstreetmap.org/search"
_last_call = 0.0


def geocode(address: str = "", city: str = "", country: str = "Ελλάδα") -> dict | None:
    """Επιστρέφει {"lat": float, "lng": float, "display": str} ή None."""
    query = ", ".join([p for p in (address.strip(), city.strip(), country) if p])
    if not query.strip(", "):
        return None

    global _last_call
    wait = 1.05 - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)          # σεβασμός στο rate limit του Nominatim
    _last_call = time.time()

    try:
        r = requests.get(
            _ENDPOINT,
            params={"q": query, "format": "json", "limit": 1, "countrycodes": "gr",
                    "accept-language": "el"},
            headers={"User-Agent": _UA},
            timeout=12,
        )
        if not r.ok:
            return None
        rows = r.json() or []
    except Exception as e:  # noqa: BLE001 — ποτέ να μη σπάσει το site
        print(f"[geocode] skipped ({type(e).__name__}): {e}")
        return None

    if not rows:
        return None
    row = rows[0]
    try:
        return {"lat": round(float(row["lat"]), 6),
                "lng": round(float(row["lon"]), 6),
                "display": row.get("display_name", "")}
    except (KeyError, TypeError, ValueError):
        return None
