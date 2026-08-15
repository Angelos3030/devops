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

from . import ai
from . import config as cfg

# Marketing fields the AI is allowed to write (design/layout never touched).
_COPY_FIELDS = ("tagline", "intro", "story_title", "story_paragraphs", "cta_title")

# Μικρό, ντετερμινιστικό λεξιλόγιο ασφαλείας για παραμορφωμένους επαγγελματικούς
# όρους που έχουν εμφανιστεί σε πραγματικό benchmark. Δεν ξαναγράφει το ύφος και
# δεν προσθέτει facts· διορθώνει μόνο σαφώς λανθασμένα λήμματα πριν από το
# truth_guard, ώστε η ίδια προστασία να ισχύει σε κάθε theme.
_TERM_CORRECTIONS = (
    (re.compile(r"\bκομμώματι\b", re.IGNORECASE), "κούρεμα"),
    (re.compile(r"\bκομμώματα\b", re.IGNORECASE), "κούρεμα"),
    (re.compile(r"\bξεματιάσιμο\b", re.IGNORECASE), "αφαίρεση νεκρού τριχώματος"),
    (re.compile(r"\bτου\s+σκυλάκι\s+σας\b", re.IGNORECASE), "του σκύλου σας"),
)


def _normalize_terms(value: Any) -> Any:
    if isinstance(value, str):
        for pattern, replacement in _TERM_CORRECTIONS:
            value = pattern.sub(replacement, value)
        return value
    if isinstance(value, list):
        return [_normalize_terms(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_terms(item) for key, item in value.items()}
    return value

_SYSTEM = (
    "Είσαι Έλληνας copywriter για μικρές τοπικές επιχειρήσεις. Γράφεις σύντομα, "
    "συγκεκριμένα, γραμματικά σωστά και ανθρώπινα ελληνικά — ΟΧΙ μεταφρασμένα αγγλικά, ΟΧΙ κλισέ όπως "
    "«κορυφαία ποιότητα» ή «ο αξιόπιστος συνεργάτης σας». Επιστρέφεις ΜΟΝΟ έγκυρο JSON."
    "\n\nΑΠΟΛΥΤΟΣ ΚΑΝΟΝΑΣ — ΜΗΝ ΕΦΕΥΡΙΣΚΕΙΣ ΓΕΓΟΝΟΤΑ. Γράφεις μόνο ό,τι σου δόθηκε. "
    "ΑΠΑΓΟΡΕΥΟΝΤΑΙ, εκτός αν υπάρχουν ΑΥΤΟΛΕΞΕΙ στα στοιχεία που σου δίνονται: "
    "χρόνια λειτουργίας ή εμπειρίας, έτος ίδρυσης («από το 1998», «since», «depuis»), "
    "τιμές και ποσά, εγγυήσεις, πιστοποιήσεις, βραβεία, βαθμολογίες, κριτικές, "
    "αριθμοί πελατών ή έργων, συνεργασίες, χρόνος απόκρισης, 24/7 διαθεσιμότητα, "
    "ιατρικοί ισχυρισμοί, και υπερθετικά σαν γεγονός («ο καλύτερος», «Νο1»). "
    "Αν δεν ξέρεις κάτι, ΜΗΝ το γράψεις καθόλου — μη μαντεύεις και μη στρογγυλοποιείς. "
    "Ένα σύντομο, αληθινό κείμενο είναι σωστό· ένα πλούσιο κείμενο με έναν "
    "εφευρεμένο αριθμό είναι άχρηστο και θα απορριφθεί ολόκληρο."
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

_REVIEW_SYSTEM = (
    "Είσαι αυστηρός επιμελητής ελληνικών κειμένων για επαγγελματικά websites. "
    "Διόρθωσε μόνο γραμματική, σύνταξη, συμφωνία προσώπου και αφύσικες ή "
    "λανθασμένες λέξεις. Διατήρησε ακριβώς το νόημα, τα δεδομένα, τα πεδία και "
    "τη δομή JSON. ΜΗΝ προσθέσεις υπηρεσίες, υποσχέσεις, αριθμούς, ιδιότητες ή "
    "οποιοδήποτε νέο γεγονός. Επίστρεψε ΜΟΝΟ έγκυρο JSON."
)


def _proofread_copy(copy: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    """Best-effort Greek proofreading constrained by the customer's facts."""
    try:
        reviewed = ai.complete_json(
            _REVIEW_SYSTEM,
            "ΕΠΙΤΡΕΠΟΜΕΝΑ FACTS ΠΕΛΑΤΗ (η μοναδική πηγή αλήθειας):\n"
            + json.dumps(intake, ensure_ascii=False)
            + "\n\nΚΕΙΜΕΝΟ ΠΡΟΣ ΔΙΟΡΘΩΣΗ:\n"
            + json.dumps(copy, ensure_ascii=False)
            + "\n\nΑφαίρεσε κάθε λεπτομέρεια ή υπόσχεση που δεν στηρίζεται ρητά στα facts. "
              "Διόρθωσε όλα τα αφύσικα ελληνικά και κράτησε το κείμενο σύντομο.",
            max_tokens=1200,
        )
    except Exception:  # pragma: no cover - provider failure falls back safely
        return copy
    if not isinstance(reviewed, dict):
        return copy

    # Ο reviewer δεν επιτρέπεται να προσθέσει νέα πεδία ή να αλλάξει σχήμα.
    out = dict(copy)
    for key, original in copy.items():
        candidate = reviewed.get(key)
        if isinstance(original, str) and isinstance(candidate, str) and candidate.strip():
            out[key] = candidate.strip()
        elif isinstance(original, list) and isinstance(candidate, list):
            out[key] = candidate
    return out


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
    if not ai.available():
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

    # A category-only prompt (for example «έχω ξενοδοχείο») does not contain
    # enough facts for responsible AI copy. Calling the model here produced
    # invented services and generic claims that displaced the reviewed vertical
    # defaults. Use AI only when the customer supplied meaningful context,
    # explicit services, or an existing public website to ground the result.
    detail_words = re.findall(r"[\wά-ώΆ-Ώ]+", str(extra), flags=re.UNICODE)
    has_grounding = has_services or bool(reference) or len(detail_words) >= 5
    if not has_grounding:
        return {}

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

    data = ai.complete_json(_SYSTEM, user, max_tokens=1200)
    if not isinstance(data, dict):
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
    return _normalize_terms(_proofread_copy(out, intake))


def enrich_with_copy(intake: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of intake with AI marketing copy merged in (no-op without key).

    Το prompt ΔΕΝ αρκεί. Το benchmark των 10 sites έδειξε ότι το μοντέλο γεμίζει
    κενά με χρόνια, τιμές και εγγυήσεις ακόμη κι όταν δεν του δόθηκαν. Κάθε
    πεδίο περνά από ντετερμινιστικό έλεγχο πριν φτάσει σε site πελάτη· ό,τι δεν
    στηρίζεται στο intake κόβεται, και το πεδίο πέφτει πίσω στο ελεγμένο default.
    """
    copy = write_copy(intake)
    if not copy:
        return intake
    from . import truth_guard
    clean, removed = truth_guard.scrub_copy(copy, intake)
    if removed:
        kinds = ", ".join(sorted({c.kind for c in removed}))
        print(f"[truth] αφαιρέθηκαν {len(removed)} ατεκμηρίωτοι ισχυρισμοί ({kinds}): "
              + " | ".join(c.text for c in removed[:5]))
    return {**intake, **clean}
