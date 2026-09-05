"""Ένα μητρώο ενεργειών — μία αλήθεια για τη φόρμα ΚΑΙ για το chat.

ΓΙΑΤΙ ΥΠΑΡΧΕΙ. Το dashboard και ο βοηθός έγραφαν στο ίδιο `site_content`, αλλά
ο καθένας ήξερε διαφορετικά πράγματα. Ο βοηθός δεν είχε ιδέα ότι ο πελάτης
μπορεί να ανεβάσει λογότυπο από την ίδια οθόνη — και ΜΕΤΡΗΘΗΚΕ να απαντά:

    «Το λογότυπο δεν μπορώ να το ανεβάσω από εδώ. Πρέπει να επικοινωνήσεις
     με τον τεχνικό σου ή να χρησιμοποιήσεις το admin panel.»

Δεν υπάρχει τεχνικός. Δεν υπάρχει admin panel. Το κουμπί είναι δύο εκατοστά
πιο κάτω. Ένα μητρώο που περιγράφει ΤΙ ΜΠΟΡΕΙ ΝΑ ΓΙΝΕΙ και ΠΟΥ, κοινό και για
τις δύο διαδρομές, κάνει τέτοιες απαντήσεις αδύνατες.

ΤΙ ΔΕΝ ΚΑΝΕΙ. Δεν αντικαθιστά το `_EDITABLE` ούτε το `put_content`: αυτά
δουλεύουν και μένουν η μοναδική πύλη εγγραφής. Προσθέτει το λεξιλόγιο —
ανθρώπινα ονόματα, πού ζει κάθε ρύθμιση, και τι ΔΕΝ υποστηρίζεται ακόμη.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Action:
    """Μία ενέργεια που μπορεί να ζητήσει ο πελάτης, με ανθρώπινο όνομα."""
    key: str                 # το πεδίο στο site_content, ή pseudo-key για media
    label: str               # πώς το λέει ο πελάτης
    done: str                # τι του λέμε όταν γίνει, με {} για την τιμή
    where: str = "form"      # form | media | design
    via_chat: bool = True    # μπορεί να το αλλάξει ο βοηθός;
    preview: bool = True     # φαίνεται στο draft preview;


# ── ό,τι ΟΝΤΩΣ αλλάζει και φαίνεται ────────────────────────────────────────
ACTIONS: dict[str, Action] = {a.key: a for a in [
    # ταυτότητα επιχείρησης
    Action("name",    "όνομα επιχείρησης", "Άλλαξα το όνομα σε «{}»."),
    Action("trade",   "επάγγελμα",         "Άλλαξα το επάγγελμα σε «{}»."),
    Action("phone",   "τηλέφωνο",          "Άλλαξα το τηλέφωνο σε {}."),
    Action("email",   "email",             "Άλλαξα το email σε {}."),
    Action("city",    "πόλη",              "Άλλαξα την πόλη σε {}."),
    Action("address", "διεύθυνση",         "Άλλαξα τη διεύθυνση σε {}."),
    Action("hours",   "ωράριο",            "Ενημέρωσα το ωράριο: {}."),
    Action("areas",   "περιοχές που εξυπηρετείς", "Ενημέρωσα τις περιοχές: {}."),
    # επικοινωνία
    Action("gbp_url",   "προφίλ Google",  "Σύνδεσα το προφίλ σου στο Google.", via_chat=False),
    Action("facebook",  "Facebook",       "Σύνδεσα τη σελίδα σου στο Facebook."),
    Action("instagram", "Instagram",      "Σύνδεσα το Instagram σου."),
    # κείμενα
    Action("tagline",   "φράση παρουσίασης", "Άλλαξα τη φράση παρουσίασης."),
    Action("intro",     "εισαγωγικό κείμενο", "Ξαναέγραψα το εισαγωγικό κείμενο."),
    Action("story_title", "τίτλος ενότητας «η ιστορία μας»", "Άλλαξα τον τίτλο της ενότητας."),
    Action("story_paragraphs", "κείμενο «η ιστορία μας»", "Ξαναέγραψα το κείμενο της ενότητας."),
    Action("cta_title", "τίτλος πρόσκλησης", "Άλλαξα τον τίτλο της πρόσκλησης."),
    # υπηρεσίες
    Action("services", "υπηρεσίες", "Ενημέρωσα τις υπηρεσίες σου."),
    # σχεδίαση
    Action("palette",   "χρώματα",       "Άλλαξα τα χρώματα του site.", where="design"),
    Action("font_pair", "γραμματοσειρά", "Άλλαξα τη γραμματοσειρά.", where="design"),
    Action("template",  "σχέδιο",        "Άλλαξα το σχέδιο του site.", where="design"),
]}

# Ανθρώπινα ονόματα για τις επιλογές — ο πελάτης δεν διαβάζει ποτέ «rose».
PALETTE_EL = {"original": "τα αρχικά χρώματα του σχεδίου", "warm": "ζεστά",
              "forest": "πράσινα", "ocean": "μπλε", "rose": "ροζ", "mono": "ασπρόμαυρα"}
FONT_EL = {"editorial": "κλασική με χαρακτήρα", "modern": "μοντέρνα",
           "friendly": "φιλική και στρογγυλή", "classic": "παραδοσιακή"}

# ── ό,τι γίνεται, αλλά ΟΧΙ από τον βοηθό — και πού ακριβώς γίνεται ─────────
# Χωρίς αυτό ο βοηθός εφηύρισκε «τεχνικό» και «admin panel».
ELSEWHERE: dict[str, str] = {
    "logo_upload":   "Το λογότυπο ανεβαίνει από την καρτέλα «Στοιχεία», στην ενότητα «Λογότυπο».",
    "logo_generate": "Αν δεν έχεις λογότυπο, στην καρτέλα «Στοιχεία» υπάρχει «Δημιούργησε 3 προτάσεις».",
    "photo_upload":  "Οι φωτογραφίες ανεβαίνουν από την καρτέλα «Στοιχεία», στην ενότητα «Φωτογραφίες».",
    "photo_delete":  "Η διαγραφή φωτογραφίας γίνεται από την καρτέλα «Στοιχεία».",
    "billing":       "Η συνδρομή αλλάζει από το κουμπί «Συνδρομή» πάνω δεξιά.",
    "domain":        "Για δικό σου domain γράψε μας στο hello@getvitrina.gr.",
}

# ── ό,τι ΔΕΝ γίνεται ακόμη από πουθενά ────────────────────────────────────
# Το λέμε καθαρά. Ποτέ ψεύτικη επιτυχία, ποτέ παραπομπή σε ανύπαρκτο μέρος.
NOT_YET: tuple[str, ...] = (
    "σειρά φωτογραφιών",
)

HONEST_NO = "Αυτό δεν μπορώ να το αλλάξω ακόμη από εδώ."


# Αιτιατική με άρθρο — χωρίς αυτό το «Ενημέρωσα πόλη, τίτλος πρόσκλησης»
# διαβαζόταν σαν λίστα πεδίων βάσης, όχι σαν ελληνικά.
ACC: dict[str, str] = {
    'name': 'το όνομα',
    'trade': 'το επάγγελμα',
    'phone': 'το τηλέφωνο',
    'email': 'το email',
    'city': 'την πόλη',
    'address': 'τη διεύθυνση',
    'hours': 'το ωράριο',
    'areas': 'τις περιοχές που εξυπηρετείς',
    'gbp_url': 'το προφίλ Google',
    'facebook': 'το Facebook',
    'instagram': 'το Instagram',
    'tagline': 'τη φράση παρουσίασης',
    'intro': 'το εισαγωγικό κείμενο',
    'story_title': 'τον τίτλο της ενότητας',
    'story_paragraphs': 'το κείμενο της ενότητας',
    'cta_title': 'τον τίτλο της πρόσκλησης',
    'services': 'τις υπηρεσίες',
    'palette': 'τα χρώματα',
    'font_pair': 'τη γραμματοσειρά',
    'template': 'το σχέδιο',
}


def label(key: str) -> str:
    a = ACTIONS.get(key)
    return a.label if a else key


def acc(key: str) -> str:
    """Το όνομα σε αιτιατική, για προτάσεις τύπου «Ενημέρωσα …»."""
    return ACC.get(key, label(key))


def confirm(key: str, value) -> str:
    """Μία ανθρώπινη πρόταση για μία αλλαγή. Ποτέ όνομα πεδίου, ποτέ slug."""
    a = ACTIONS.get(key)
    if not a:
        return "Έγινε."
    if key == "palette":
        return f"Άλλαξα τα χρώματα σε {PALETTE_EL.get(str(value), str(value))}."
    if key == "font_pair":
        return f"Έβαλα {FONT_EL.get(str(value), str(value))} γραμματοσειρά."
    if key == "services":
        n = len(value) if isinstance(value, list) else 0
        return f"Ενημέρωσα τις υπηρεσίες σου — τώρα είναι {n}." if n else a.done
    if key == "story_paragraphs":
        return a.done
    if "{}" in a.done:
        text = str(value)
        return a.done.format(text if len(text) <= 60 else text[:57] + "…")
    return a.done


def summary(changes: dict) -> str:
    """Μία πρόταση για όλες τις αλλαγές μαζί — αυτό διαβάζει ο πελάτης."""
    keys = [k for k in changes if k in ACTIONS]
    if not keys:
        return HONEST_NO
    if len(keys) == 1:
        return confirm(keys[0], changes[keys[0]])
    parts = [acc(k) for k in keys]
    if len(parts) == 2:
        return f"Ενημέρωσα {parts[0]} και {parts[1]}."
    return "Ενημέρωσα " + ", ".join(parts[:-1]) + f" και {parts[-1]}."


def chat_editable() -> tuple[str, ...]:
    return tuple(k for k, a in ACTIONS.items() if a.via_chat)


def preview_fields() -> tuple[str, ...]:
    """Ό,τι πρέπει να φαίνεται στο draft ΠΡΙΝ ζητηθεί έγκριση.

    Το `email/facebook/instagram` έλειπαν από το DRAFT_FIELDS: ο πελάτης άλλαζε
    email από το chat, δεν έβλεπε τίποτα να αλλάζει, και απέρριπτε σωστή αλλαγή.
    """
    return tuple(k for k, a in ACTIONS.items() if a.preview)
