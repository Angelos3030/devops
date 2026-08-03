"""AI copywriter hook for the Vitrina premium generator.

Given a client intake, asks a cheap Claude model (Haiku) to write local, specific
Greek marketing copy (tagline, intro, story, CTA, service descriptions). The output
merges into the intake BEFORE `premium_generator` fills the templates.

Design contract:
- Fully optional. If `ANTHROPIC_API_KEY` is missing or anything fails, returns {}
  and the generator falls back to per-profession template defaults (zero-risk).
- Only marketing text is AI-written. Layout/design stays deterministic (templates).
- Client-provided services/photos always win over AI.
"""
from __future__ import annotations

import ipaddress
import json
import re
import socket
from typing import Any
from urllib.parse import urlparse

from . import config as cfg

# Marketing fields the AI is allowed to write (design/layout never touched).
_COPY_FIELDS = ("tagline", "intro", "story_title", "story_paragraphs", "cta_title")

_SYSTEM = (
    "Είσαι Έλληνας copywriter για μικρές τοπικές επιχειρήσεις. Γράφεις σύντομα, "
    "συγκεκριμένα και ανθρώπινα ελληνικά — ΟΧΙ μεταφρασμένα αγγλικά, ΟΧΙ κλισέ όπως "
    "«κορυφαία ποιότητα» ή «ο αξιόπιστος συνεργάτης σας». Επιστρέφεις ΜΟΝΟ έγκυρο JSON."
)

_SCHEMA_HINT = (
    '{\n'
    '  "tagline": "μία δυνατή πρόταση (max ~18 λέξεις) για το hero",\n'
    '  "intro": "μία πρόταση που περιγράφει τι κάνει η επιχείρηση",\n'
    '  "story_title": "τίτλος για την ενότητα «ποιοι είμαστε» (max ~9 λέξεις)",\n'
    '  "story_paragraphs": ["παράγραφος 1", "παράγραφος 2"],\n'
    '  "cta_title": "μία πρόσκληση για επικοινωνία",\n'
    '  "services": [{"name": "Υπηρεσία", "description": "μία πρόταση"}]\n'
    '}'
)


def _is_public_http_url(url: str) -> bool:
    """SSRF guard: μόνο http(s) προς δημόσια host (όχι localhost/ιδιωτικά IP)."""
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.hostname:
            return False
        # Απόρριψη αν ΟΠΟΙΑΔΗΠΟΤΕ διεύθυνση του host είναι ιδιωτική/loopback/link-local.
        for info in socket.getaddrinfo(p.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        return True
    except Exception:
        return False


def _fetch_reference_text(url: str, limit: int = 4000) -> str:
    """Κατεβάζει το υπάρχον site/σελίδα του πελάτη και επιστρέφει καθαρό κείμενο (για context).
    Fully optional — σε οποιοδήποτε σφάλμα επιστρέφει ''."""
    if not url or not _is_public_http_url(url):
        return ""
    try:
        import requests
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 VitrinaBot"},
                         allow_redirects=True)
        if not r.ok or "html" not in r.headers.get("Content-Type", "").lower():
            return ""
        html = r.text
        html = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", html)
        text = re.sub(r"(?s)<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:limit]
    except Exception as e:  # noqa: BLE001
        print(f"[site_copy] reference fetch skipped ({type(e).__name__}): {e}")
        return ""


def _extract_json(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    return json.loads(text[start:end + 1])


def write_copy(intake: dict[str, Any]) -> dict[str, Any]:
    """Return AI-written Greek copy fields, or {} on any failure."""
    if not cfg.ANTHROPIC_API_KEY:
        return {}
    try:
        import anthropic
    except Exception:
        return {}

    name = intake.get("name") or "η επιχείρηση"
    btype = intake.get("type") or intake.get("trade") or "τοπική επιχείρηση"
    city = intake.get("city") or ""
    extra = intake.get("description") or intake.get("style") or ""
    has_services = bool(intake.get("services"))

    # Αν ο πελάτης έδωσε υπάρχον site/σελίδα → το διαβάζουμε για τις ΠΡΑΓΜΑΤΙΚΕΣ υπηρεσίες.
    ref_url = intake.get("website") or intake.get("source_url") or intake.get("existing_url") or ""
    reference = _fetch_reference_text(ref_url) if ref_url else ""
    ref_block = (
        f"\n\nΑπό το υπάρχον site/σελίδα του πελάτη (χρησιμοποίησέ το για τις ΠΡΑΓΜΑΤΙΚΕΣ "
        f"υπηρεσίες και το ύφος — ΜΗΝ αντιγράψεις αυτούσια, ξαναγράψε το φρέσκα):\n\"\"\"\n"
        f"{reference}\n\"\"\""
    ) if reference else ""

    ask_services = "" if has_services else (
        "\n- Πρόσθεσε 4-6 υπηρεσίες με σύντομη περιγραφή στο πεδίο \"services\", "
        "ταξινομημένες από την πιο σημαντική/συχνή στη λιγότερο."
    )
    user = (
        f"Επιχείρηση: {name}\nΤύπος: {btype}\nΠεριοχή: {city}\n"
        f"Επιπλέον πληροφορίες: {extra}{ref_block}\n\n"
        f"Γράψε marketing copy στα ελληνικά για το site της. Τόνος τοπικός και άμεσος."
        f"{ask_services}\n\nΕπίστρεψε ΜΟΝΟ JSON με αυτή τη μορφή:\n{_SCHEMA_HINT}"
    )

    try:
        # base_url: επιτρέπει εναλλακτικό πάροχο (π.χ. Azure AI Foundry) χωρίς
        # αλλαγή κώδικα — κενό σημαίνει απευθείας Anthropic.
        client = anthropic.Anthropic(
            api_key=cfg.ANTHROPIC_API_KEY,
            **({"base_url": cfg.ANTHROPIC_BASE_URL} if cfg.ANTHROPIC_BASE_URL else {}),
        )
        resp = client.messages.create(
            model=cfg.MODEL_CHEAP,
            max_tokens=1200,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(getattr(b, "text", "") for b in resp.content)
        data = _extract_json(text)
    except Exception as e:  # network / auth / parse — fall back to defaults
        print(f"[site_copy] AI copy skipped ({type(e).__name__}): {e}")
        return {}

    out: dict[str, Any] = {}
    for key in _COPY_FIELDS:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            out[key] = val.strip()
        elif key == "story_paragraphs" and isinstance(val, list):
            paras = [str(p).strip() for p in val if str(p).strip()]
            if paras:
                out[key] = paras
    # services only if the client did not provide any
    if not has_services and isinstance(data.get("services"), list):
        svcs = [
            {"name": str(s.get("name", "")).strip(), "description": str(s.get("description", "")).strip()}
            for s in data["services"] if isinstance(s, dict) and str(s.get("name", "")).strip()
        ]
        if svcs:
            out["services"] = svcs[:6]
    return out


def enrich_with_copy(intake: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of intake with AI marketing copy merged in (no-op without key)."""
    copy = write_copy(intake)
    return {**intake, **copy} if copy else intake
