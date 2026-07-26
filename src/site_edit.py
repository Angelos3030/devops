"""
Chat-to-edit: ο πελάτης γράφει τι θέλει με απλά λόγια και το site αλλάζει.

Ασφάλεια by design: το AI **δεν γράφει κώδικα** και δεν αγγίζει τη βάση. Επιστρέφει
JSON patch μόνο πάνω σε συγκεκριμένα πεδία (allowlist) — ό,τι δεν αναγνωρίζεται
αγνοείται. Έτσι «άλλαξε το τηλέφωνο» δουλεύει, ενώ τίποτα δεν μπορεί να σπάσει
το site ή να διαρρεύσει δεδομένα.
"""
from __future__ import annotations

import json
from typing import Any

from . import config as cfg

# Πρέπει να ταιριάζει με το _EDITABLE στο meta_oauth.py
EDITABLE_FIELDS = (
    "name", "trade", "city", "phone", "hours", "areas",
    "tagline", "intro", "story_title", "story_paragraphs", "cta_title",
    "services", "template",
)

_SYSTEM = (
    "Είσαι ο βοηθός που επεξεργάζεται το site μιας μικρής ελληνικής επιχείρησης. "
    "Ο ιδιοκτήτης σου λέει τι θέλει με απλά λόγια και εσύ επιστρέφεις ΜΟΝΟ έγκυρο JSON.\n\n"
    "Κανόνες:\n"
    "- Άλλαξε ΜΟΝΟ ό,τι ζήτησε. Μη «βελτιώνεις» άλλα πεδία από μόνος σου.\n"
    "- Γράφε φυσικά ελληνικά, σύντομα, χωρίς κλισέ («κορυφαία ποιότητα», «αξιόπιστος συνεργάτης»).\n"
    "- Αν ζητάει άλλη εμφάνιση/στιλ/χρώματα, διάλεξε κατάλληλο `template` από τη λίστα.\n"
    "- Αν δεν καταλαβαίνεις τι θέλει, άσε το `changes` άδειο και ρώτησέ τον στο `reply`.\n"
    "- Αν ζητάει κάτι που δεν γίνεται από εδώ (π.χ. φωτογραφίες, domain, τιμολόγηση), "
    "εξήγησέ του σύντομα στο `reply` πού να πάει."
)

_SCHEMA = (
    '{\n'
    '  "changes": { "πεδίο": "νέα τιμή", ... },   // μόνο όσα αλλάζουν\n'
    '  "reply": "μία-δύο προτάσεις στα ελληνικά: τι άλλαξες ή τι χρειάζεσαι"\n'
    '}'
)


def _extract_json(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}


def chat_edit(message: str, content: dict[str, Any],
              templates: list[str]) -> dict[str, Any]:
    """Επιστρέφει {"changes": {...}, "reply": "..."} — ποτέ δεν πετάει exception."""
    if not cfg.ANTHROPIC_API_KEY:
        return {"changes": {}, "reply": "Ο βοηθός δεν είναι διαθέσιμος αυτή τη στιγμή. "
                                        "Μπορείς να αλλάξεις τα πεδία χειροκίνητα."}
    try:
        import anthropic
    except Exception:  # noqa: BLE001
        return {"changes": {}, "reply": "Ο βοηθός δεν είναι διαθέσιμος αυτή τη στιγμή."}

    editable_now = {k: v for k, v in content.items() if k in EDITABLE_FIELDS}
    user = (
        f"Τρέχον περιεχόμενο του site (JSON):\n{json.dumps(editable_now, ensure_ascii=False, indent=1)}\n\n"
        f"Διαθέσιμα templates για το `template`: {', '.join(templates)}\n\n"
        f"Ο ιδιοκτήτης ζητάει:\n«{message.strip()[:800]}»\n\n"
        f"Επίστρεψε ΜΟΝΟ JSON σε αυτή τη μορφή:\n{_SCHEMA}"
    )

    try:
        client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=cfg.MODEL_CHEAP,
            max_tokens=1500,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        data = _extract_json("".join(getattr(b, "text", "") for b in resp.content))
    except Exception as e:  # noqa: BLE001
        print(f"[site_edit] chat failed ({type(e).__name__}): {e}")
        return {"changes": {}, "reply": "Κάτι πήγε στραβά με τον βοηθό. Δοκίμασε ξανά σε λίγο."}

    changes = data.get("changes")
    if not isinstance(changes, dict):
        changes = {}
    changes = {k: v for k, v in changes.items() if k in EDITABLE_FIELDS}
    reply = str(data.get("reply") or "Έγινε.").strip()[:600]
    return {"changes": changes, "reply": reply}
