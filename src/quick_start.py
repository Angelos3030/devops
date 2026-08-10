"""
Μία πρόταση → πελάτης. Η καρδιά του «site first, questions later».

Ο ιδιοκτήτης γράφει «έχω καφετέρια στον Γέρακα» και προχωράμε αμέσως στο site.
Καμία φόρμα, κανένα βήμα. Ό,τι λείπει το ρωτάμε ΑΦΟΥ δει αποτέλεσμα.

Δύο επίπεδα: το AI κάνει τη σωστή δουλειά· τα regex είναι το δίχτυ ασφαλείας
ώστε η ροή να μη σπάει ποτέ όταν λείπει κλειδί ή πέσει ο provider.
"""
from __future__ import annotations

import re
import threading
import time
from typing import Any

from . import ai

# ---------------------------------------------------------------- επαγγέλματα
# Χωρίς τόνους και στα δύο μέρη της σύγκρισης — ο πελάτης γράφει «καφετέρια»,
# «Καφετέρια» ή «ΚΑΦΕΤΕΡΙΑ» και πρέπει να πιάνονται όλα.
TRADES: tuple[tuple[str, str], ...] = (
    ("Καφετέρια", r"καφε|καφετ|coffee|espresso|brunch|μπραντς"),
    ("Φούρνος", r"φουρν|αρτοποι|ψωμ|bakery"),
    ("Ζαχαροπλαστείο", r"ζαχαροπλ|γλυκ|patisserie|παγωτ"),
    ("Ταβέρνα", r"ταβερν|εστιατορ|μεζεδοπωλ|ουζερ|restaurant"),
    ("Ψησταριά", r"ψησταρ|σουβλα|grill|γυραδ"),
    ("Πιτσαρία", r"πιτσα|pizza"),
    ("Μπαρ", r"\bbar\b|μπαρ|cocktail|κοκτειλ"),
    ("Κομμωτήριο", r"κομμωτ|κουρε|barber|μαλλ|hair"),
    ("Νυχάδικο", r"νυχ|nail|μανικιουρ|πεντικιουρ"),
    ("Ινστιτούτο αισθητικής", r"αισθητικ|beauty|spa|περιποιησ"),
    ("Μασάζ", r"μασαζ|massage|φυσικοθεραπ"),
    ("Γυμναστήριο", r"γυμναστηρ|gym|fitness|pilates|πιλατες|crossfit|yoga|γιογκα"),
    ("Οδοντιατρείο", r"οδοντ|dentist|ορθοδοντ"),
    ("Ιατρείο", r"ιατρειο|γιατρ|ιατρ|παθολογ|καρδιολογ|παιδιατρ|δερματολογ|ψυχολογ|διαιτολογ|διατροφολογ"),
    ("Κτηνιατρείο", r"κτηνιατρ|vet\b"),
    ("Φαρμακείο", r"φαρμακει"),
    ("Δικηγορικό γραφείο", r"δικηγορ|νομικ|lawyer"),
    ("Λογιστικό γραφείο", r"λογιστ|φοροτεχν|accountant"),
    ("Υδραυλικός", r"υδραυλικ|plumber|αποφραξ"),
    ("Ηλεκτρολόγος", r"ηλεκτρολογ|electrician"),
    ("Ξυλουργός", r"ξυλουργ|επιπλοποι|μαραγκ|carpenter"),
    ("Συνεργείο αυτοκινήτων", r"συνεργει|φανοποι|βουλκανιζ|service αυτοκιν"),
    ("Ξενοδοχείο", r"ξενοδοχ|hotel|δωματ|καταλυμ|airbnb|ενοικιαζ"),
    ("Κατάστημα", r"καταστημ|μαγαζ|shop|store|boutique|μπουτικ"),
)

# «στον Γέρακα», «στη Γλυφάδα», «στο Χαλάνδρι» → η πόλη είναι μετά το άρθρο.
_CITY_RE = re.compile(
    r"\bστ(?:ον?|ην?|ο|α)\s+([Α-ΩΆΈΉΊΌΎΏA-Z][\wΆ-ώα-ω]+(?:\s+[Α-ΩΆΈΉΊΌΎΏA-Z][\wΆ-ώα-ω]+)?)"
)
# «Καφέ Ολύμπια», «"Το Στέκι"», «λέγεται Μαρία»
_NAME_RE = re.compile(r"[«\"']([^»\"']{2,60})[»\"']|(?:λεγεται|ονομαζεται|το λενε)\s+([\wΆ-ώα-ω ]{2,40})")

_SYSTEM = (
    "Διαβάζεις μία πρόταση ενός Έλληνα επαγγελματία για την επιχείρησή του και "
    "επιστρέφεις ΜΟΝΟ έγκυρο JSON. Μην επινοείς τίποτα: αν κάτι δεν λέγεται, βάλε null. "
    "Ποτέ μην φαντάζεσαι επωνυμία, τηλέφωνο, χρόνια εμπειρίας ή υπηρεσίες."
)
_SCHEMA = (
    '{"name": "επωνυμία ή null", '
    '"type": "το είδος της ΕΠΙΧΕΙΡΗΣΗΣ σε ονομαστική — «Ταβέρνα», «Κομμωτήριο», '
    '«Οδοντιατρείο». ΠΟΤΕ το επάγγελμα του ατόμου («ταβερνιάρης», «κομμώτρια»)", '
    '"city": "πόλη/περιοχή σε ονομαστική («στον Γέρακα» → «Γέρακας») ή null", '
    '"services": ["έως 4 συνηθισμένες υπηρεσίες για ΑΥΤΟ το είδος επιχείρησης, '
    'γενικές, χωρίς επινοημένες λεπτομέρειες, τιμές ή χρόνια"]}'
)


def _strip_tones(text: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def _guess_trade(text: str) -> str | None:
    flat = _strip_tones(text).lower()
    for label, pattern in TRADES:
        if re.search(pattern, flat):
            return label
    return None


def _guess_city(text: str) -> str | None:
    match = _CITY_RE.search(text)
    if not match:
        return None
    # Κρατάμε την πόλη όπως γράφτηκε. Η αιτιατική («στον Γέρακα») διορθώνεται
    # από το AI όταν υπάρχει· δεν κάνουμε γραμματική με regex — βγάζει τέρατα.
    return match.group(1).strip()


def _guess_name(text: str) -> str | None:
    match = _NAME_RE.search(_strip_tones(text))
    if not match:
        return None
    return (match.group(1) or match.group(2) or "").strip() or None


def parse(text: str) -> dict[str, Any]:
    """Ελεύθερο κείμενο → πεδία intake. Δεν πετάει ποτέ exception."""
    text = (text or "").strip()[:400]
    fallback = {
        "name": _guess_name(text),
        "type": _guess_trade(text),
        "city": _guess_city(text),
        "services": [],
    }

    if ai.available() and text:
        try:
            data = ai.complete_json(
                _SYSTEM,
                f"Πρόταση: «{text}»\n\nΕπίστρεψε ΜΟΝΟ JSON:\n{_SCHEMA}",
                max_tokens=400,
            )
            if isinstance(data, dict):
                # Το `type` τροφοδοτεί το vertical matching, οπότε το λεξιλόγιο του
                # TRADES είναι ΑΥΘΕΝΤΙΑ όταν πιάνει: είναι τα ίδια ονόματα που ξέρει
                # το verticalProfiles.js. Το AI έδινε «ταβερνιάτης» αντί «Ταβέρνα».
                for key in ("name", "city"):
                    value = data.get(key)
                    if isinstance(value, str) and value.strip():
                        fallback[key] = value.strip()[:80]
                if not fallback["type"]:
                    value = data.get("type")
                    if isinstance(value, str) and value.strip():
                        fallback["type"] = value.strip()[:80]
                services = data.get("services")
                if isinstance(services, list):
                    fallback["services"] = [str(s)[:60] for s in services[:4] if s]
        except Exception as exc:  # noqa: BLE001 — η ροή δεν σπάει ποτέ για το AI
            print(f"[quick_start] AI parse skipped: {exc}")

    # Χωρίς επωνυμία δεν υπάρχει site. Αν δεν τη βρήκαμε, τη ζητάμε ΜΕΤΑ το preview —
    # προσωρινά χρησιμοποιούμε το επάγγελμα, ποτέ επινοημένο όνομα.
    if not fallback["name"]:
        fallback["name"] = fallback["type"] or "Η επιχείρησή μου"
    if not fallback["type"]:
        fallback["type"] = "Άλλο"
    fallback["description"] = text
    return fallback


# ------------------------------------------------------------------ πρόοδος
# Η αναμονή είναι προϊόν: ο πελάτης βλέπει ΤΙ γίνεται, όχι spinner.
# Κρατιέται στη μνήμη επίτηδες — είναι εφήμερη κατάσταση 60 δευτερολέπτων,
# δεν αξίζει εγγραφή στη βάση. Αν πέσει ο server, το UI δείχνει το τελικό
# αποτέλεσμα ούτως ή άλλως γιατί ρωτάει και για τα designs.
STAGES: tuple[tuple[str, str], ...] = (
    ("copy", "Γράφουμε τα κείμενα στα ελληνικά"),
    ("photos", "Διαλέγουμε φωτογραφίες για το επάγγελμά σου"),
    ("geo", "Βάζουμε χάρτη, διεύθυνση και ωράριο"),
    ("design", "Δοκιμάζουμε εμφανίσεις και κρατάμε τις 3 καλύτερες"),
    ("seo", "Ετοιμάζουμε το site για την Google"),
)

_PROGRESS: dict[str, dict[str, Any]] = {}
_LOCK = threading.Lock()


def mark(client_id: str, stage: str, done: bool = True) -> None:
    """Σημειώνει ότι ένα στάδιο ξεκίνησε ή τελείωσε. Ποτέ δεν πετάει."""
    if not client_id:
        return
    try:
        with _LOCK:
            entry = _PROGRESS.setdefault(client_id, {"started": time.time(), "stages": {}})
            entry["stages"][stage] = {"done": done, "at": time.time()}
            if len(_PROGRESS) > 400:          # φραγμός μνήμης
                oldest = min(_PROGRESS, key=lambda k: _PROGRESS[k]["started"])
                _PROGRESS.pop(oldest, None)
    except Exception:  # noqa: BLE001
        pass


def snapshot(client_id: str) -> dict[str, Any]:
    with _LOCK:
        entry = _PROGRESS.get(client_id)
        stages = dict(entry["stages"]) if entry else {}
        started = entry["started"] if entry else None
    return {
        "stages": [
            {
                "id": sid,
                "label": label,
                "state": ("done" if stages[sid]["done"] else "running") if sid in stages else "waiting",
            }
            for sid, label in STAGES
        ],
        "elapsed": round(time.time() - started, 1) if started else 0,
    }
