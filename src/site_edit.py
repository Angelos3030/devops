"""
Chat-to-edit: ο πελάτης γράφει τι θέλει με απλά λόγια και το site αλλάζει.

Ασφάλεια by design: το AI **δεν γράφει κώδικα** και δεν αγγίζει τη βάση. Επιστρέφει
JSON patch μόνο πάνω σε συγκεκριμένα πεδία (allowlist) — ό,τι δεν αναγνωρίζεται
αγνοείται. Έτσι «άλλαξε το τηλέφωνο» δουλεύει, ενώ τίποτα δεν μπορεί να σπάσει
το site ή να διαρρεύσει δεδομένα.
"""
from __future__ import annotations

import json
import re
from typing import Any

from . import ai
from . import site_actions as _sa

# Παράγεται από το μητρώο ενεργειών — μία αλήθεια για φόρμα και chat.
# Πριν ήταν χειρόγραφο αντίγραφο του _EDITABLE και είχε ήδη αποκλίνει.
EDITABLE_FIELDS = _sa.chat_editable()

_SYSTEM = (
    "Είσαι ο βοηθός που επεξεργάζεται το site μιας μικρής ελληνικής επιχείρησης. "
    "Ο ιδιοκτήτης σου λέει τι θέλει με απλά λόγια και εσύ επιστρέφεις ΜΟΝΟ έγκυρο JSON.\n\n"
    "Κανόνες:\n"
    "- Άλλαξε ΜΟΝΟ ό,τι ζήτησε. Μη «βελτιώνεις» άλλα πεδία από μόνος σου.\n"
    "- Γράφε ΑΠΟΚΛΕΙΣΤΙΚΑ στα ελληνικά, σύντομα, χωρίς κλισέ.\n"
    "- Αν ζητάει άλλη εμφάνιση/στιλ/χρώματα, διάλεξε κατάλληλο `template` από τη λίστα.\n"
    "- Αν ζητάει μόνο χρώματα, κράτα το template και βάλε `palette`: "
    "original, warm, forest, ocean, rose ή mono.\n"
    "- Αν ζητάει μόνο γραμματοσειρά, βάλε `font_pair`: "
    "editorial, modern, friendly ή classic.\n"
    "- Αν δεν καταλαβαίνεις τι θέλει, άσε το `changes` άδειο και ρώτησέ τον στο `reply`.\n"
    "\n"
    "ΕΙΣΑΙ Η VITRINA. Δεν υπάρχει «τεχνικός», δεν υπάρχει «admin panel», δεν υπάρχει "
    "«πάροχος φιλοξενίας» να τον στείλεις. ΠΟΤΕ μην τον παραπέμψεις σε τρίτον.\n"
    "\n"
    "Αυτά ΔΕΝ τα αλλάζεις εσύ, αλλά τα κάνει ο ίδιος από την ΙΔΙΑ οθόνη — πες του "
    "ακριβώς πού, με αυτά τα λόγια:\n"
    + "\n".join(f"- {v}" for v in _sa.ELSEWHERE.values()) + "\n"
    "\n"
    "Αν ζητάει κάτι που δεν γίνεται ακόμη από πουθενά (π.χ. σειρά φωτογραφιών), πες "
    f"«{_sa.HONEST_NO}» και τίποτα άλλο. Ποτέ ψεύτικη επιτυχία.\n"
    "\n"
    "ΠΟΤΕ μη γράψεις στον πελάτη ονόματα πεδίων ή αγγλικά κλειδιά "
    "(π.χ. palette, font_pair, cta_title, rose, editorial). Μίλα για «τα χρώματα», "
    "«τη γραμματοσειρά», «τον τίτλο»."
)

_SCHEMA = (
    '{\n'
    '  "changes": { "πεδίο": "νέα τιμή", ... },   // μόνο όσα αλλάζουν\n'
    '  "reply": "μία-δύο προτάσεις στα ελληνικά: τι άλλαξες ή τι χρειάζεσαι"\n'
    '}'
)


def chat_edit(message: str, content: dict[str, Any],
              templates: list[str]) -> dict[str, Any]:
    """Επιστρέφει {"changes": {...}, "reply": "..."} — ποτέ δεν πετάει exception."""
    if not ai.available():
        return {"changes": {}, "reply": "Ο βοηθός δεν είναι διαθέσιμος αυτή τη στιγμή. "
                                        "Μπορείς να αλλάξεις τα πεδία χειροκίνητα."}

    editable_now = {k: v for k, v in content.items() if k in EDITABLE_FIELDS}
    user = (
        f"Τρέχον περιεχόμενο του site (JSON):\n{json.dumps(editable_now, ensure_ascii=False, indent=1)}\n\n"
        f"Διαθέσιμα templates για το `template`: {', '.join(templates)}\n\n"
        f"Ο ιδιοκτήτης ζητάει:\n«{message.strip()[:800]}»\n\n"
        f"Επίστρεψε ΜΟΝΟ JSON σε αυτή τη μορφή:\n{_SCHEMA}"
    )

    data = ai.complete_json(_SYSTEM, user, max_tokens=1500)
    if not isinstance(data, dict):
        return {"changes": {}, "reply": "Κάτι πήγε στραβά με τον βοηθό. Δοκίμασε ξανά σε λίγο."}

    changes = data.get("changes")
    if not isinstance(changes, dict):
        changes = {}
    changes = {k: v for k, v in changes.items() if k in EDITABLE_FIELDS}

    # ΟΤΑΝ ΚΑΤΙ ΑΛΛΑΞΕ, ΤΟ ΛΕΜΕ ΕΜΕΙΣ — ΟΧΙ ΤΟ ΜΟΝΤΕΛΟ.
    # Η ελεύθερη απάντηση ήταν η πηγή και των δύο σφαλμάτων που μετρήθηκαν:
    # διαρροή εσωτερικών ονομάτων («το χρωματικό σχήμα είναι ήδη ρόζ (rose
    # palette)… (warm)») και κατάρρευση γλώσσας (κορεατικοί χαρακτήρες μέσα
    # σε ελληνική πρόταση). Η επιβεβαίωση παράγεται ντετερμινιστικά από το
    # μητρώο: ίδια διατύπωση κάθε φορά, μηδέν εσωτερικά ονόματα.
    if changes:
        return {"changes": changes, "reply": _sa.summary(changes)}

    return {"changes": {}, "reply": _clean(str(data.get("reply") or ""))}


# Εσωτερικά ονόματα που δεν επιτρέπεται να φτάσουν ποτέ στον πελάτη.
_LEAK = tuple(EDITABLE_FIELDS) + (
    "original", "warm", "forest", "ocean", "rose", "mono",
    "editorial", "modern", "friendly", "classic",
    "allowlist", "json", "payload", "endpoint", "field",
)
# Παραπομπές σε τρίτους που δεν υπάρχουν.
_INVENTED = ("τεχνικ", "admin", "panel", "webmaster", "διαχειριστ", "πάροχο", "hosting")

# Επιτρεπτά σύμβολα, ως αριθμητικά εύρη. Γράφτηκαν έτσι επίτηδες: κάθε
# προσπάθεια να μπουν ως κυριολεκτικοί χαρακτήρες μέσα σε regex αλλοιώθηκε
# περνώντας από το κέλυφος — μια φορά άφησε μάλιστα null byte στο αρχείο.
_ALLOWED_RANGES = (
    (0x0009, 0x000D),   # tab, newline, carriage return
    (0x0020, 0x024F),   # κενό, στίξη, ψηφία, λατινικό + επεκτάσεις
    (0x0370, 0x03FF),   # ελληνικό
    (0x1F00, 0x1FFF),   # πολυτονικό
    (0x2010, 0x203A),   # παύλες, εισαγωγικά, αποσιωπητικά
    (0x20AC, 0x20AC),   # ευρώ
    (0x2212, 0x2212),   # μείον
)


def _out_of_script(text: str) -> bool:
    """True αν υπάρχει χαρακτήρας εκτός ελληνικού/λατινικού/στίξης."""
    return any(
        not any(lo <= ord(ch) <= hi for lo, hi in _ALLOWED_RANGES)
        for ch in text
    )


def _clean(reply: str) -> str:
    """Φίλτρο ασφαλείας για την ελεύθερη απάντηση (μόνο όταν ΔΕΝ άλλαξε τίποτα).

    Το prompt το απαγορεύει ήδη· αυτό είναι το δίχτυ από κάτω. Ένα μοντέλο που
    ξεχνιέται δεν πρέπει να μπορεί να στείλει τον πελάτη σε ανύπαρκτο «τεχνικό»
    ούτε να του δείξει ονόματα πεδίων.
    """
    text = " ".join(reply.split())[:600]
    if not text:
        return _sa.HONEST_NO
    low = text.lower()
    if any(w in low for w in _INVENTED):
        return _sa.HONEST_NO
    if any(re.search(rf"\b{re.escape(w)}\b", low) for w in _LEAK):
        return _sa.HONEST_NO
    # Γράμματα εκτός ελληνικού/λατινικού — σημάδι κατάρρευσης γλώσσας.
    # ΜΕΤΡΗΘΗΚΕ: «Το χρωματικό σχήμα είναι ήδη ρόζ … 따뜻ό» έφτασε σε πελάτη.
    # Τα εύρη γράφονται με ρητά escapes, όχι με κυριολεκτικούς χαρακτήρες.
    if _out_of_script(text):
        return _sa.HONEST_NO
    return text
