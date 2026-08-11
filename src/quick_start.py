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
    # Οι συγκεκριμένες ιατρικές κατηγορίες προηγούνται από το γενικό
    # «αισθητική»: η φράση «αισθητική οδοντιατρική» είναι οδοντιατρείο.
    ("Οδοντιατρείο", r"οδοντ|dentist|ορθοδοντ"),
    ("Ιατρείο", r"ιατρειο|γιατρ|ιατρ|παθολογ|καρδιολογ|παιδιατρ|δερματολογ|ψυχολογ|διαιτολογ|διατροφολογ"),
    ("Κτηνιατρείο", r"κτηνιατρ|vet\b"),
    ("Φαρμακείο", r"φαρμακει"),
    ("Ινστιτούτο αισθητικής", r"αισθητικ|beauty|spa|περιποιησ"),
    ("Μασάζ", r"μασαζ|massage|φυσικοθεραπ"),
    ("Γυμναστήριο", r"γυμναστηρ|gym|fitness|pilates|πιλατες|crossfit|yoga|γιογκα"),
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
    r"\bστ(?:ον?|ην?|ο|α)\s+([A-ZΑ-ΩΆΈΉΊΌΎΏa-zα-ωάέήίόύώϊϋΐΰ][\wΆ-ώα-ω]+"
    r"(?:\s+[A-ZΑ-ΩΆΈΉΊΌΎΏa-zα-ωάέήίόύώϊϋΐΰ][\wΆ-ώα-ω]+)?)",
    re.IGNORECASE,
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
    # Σκέτοι τίτλοι έβγαζαν αριθμημένη λίστα χωρίς περιεχόμενο («01 Διαμονή» και
    # τίποτα από κάτω). Η περιγραφή ζητείται στην ΙΔΙΑ κλήση — δεν κοστίζει δεύτερη.
    '"services": [{"name": "έως 4 συνηθισμένες υπηρεσίες για ΑΥΤΟ το είδος '
    'επιχείρησης, γενικές, χωρίς επινοημένες λεπτομέρειες, τιμές ή χρόνια", '
    '"desc": "μία πρόταση που εξηγεί την υπηρεσία, χωρίς υποσχέσεις ή αριθμούς"}]}'
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


# Το δεύτερο σκέλος του regex πιάνει διώνυμα («Νέα Σμύρνη», «Άγιος Στέφανος»),
# αλλά με IGNORECASE κόλλαγε και την επόμενη κοινή λέξη: «στην Πάρο με 12 δωμάτια»
# έδινε πόλη «Πάρο με» — και ο χάρτης έψαχνε «Πάρο με, Ελλάδα».
_CITY_TAIL = {"με", "και", "που", "για", "στο", "στη", "στον", "στην", "απο", "σε",
              "εχω", "εχει", "ειναι", "θα", "να", "το", "του", "της", "των"}


def _guess_city(text: str) -> str | None:
    match = _CITY_RE.search(text)
    if not match:
        return None
    words = match.group(1).split()
    while len(words) > 1 and _strip_tones(words[-1]).lower() in _CITY_TAIL:
        words.pop()
    # Κρατάμε την πόλη όπως γράφτηκε. Η αιτιατική («στον Γέρακα») διορθώνεται
    # από το AI όταν υπάρχει· δεν κάνουμε γραμματική με regex — βγάζει τέρατα.
    return " ".join(words).strip() or None


def _guess_name(text: str) -> str | None:
    match = _NAME_RE.search(_strip_tones(text))
    if not match:
        return None
    return (match.group(1) or match.group(2) or "").strip() or None


_TRADE_LABELS = {_strip_tones(label).lower() for label, _ in TRADES}


def _is_category(value: str, detected_type: str | None) -> bool:
    """Είναι απλώς το είδος της επιχείρησης, όχι επωνυμία;

    Στο «ξενοδοχείο» το μοντέλο επέστρεφε name="Ξενοδοχείο" — και το site
    υπέγραφε «Ξενοδοχείο» σαν να ήταν μάρκα. Η επωνυμία λείπει· τη ζητάμε στις
    συμπληρωματικές ερωτήσεις, δεν τη φτιάχνουμε από την κατηγορία."""
    flat = _strip_tones(str(value or "")).strip().lower()
    if not flat:
        return True
    return flat in _TRADE_LABELS or flat == _strip_tones(str(detected_type or "")).lower()


def _clean_services(raw: Any) -> list[dict[str, str]]:
    """[{title, desc}] — δέχεται και τη σκέτη λίστα κειμένων παλιότερων απαντήσεων."""
    out: list[dict[str, str]] = []
    for item in raw[:4]:
        if isinstance(item, dict):
            title = str(item.get("name") or item.get("title") or "").strip()[:60]
            desc = str(item.get("desc") or item.get("description") or "").strip()[:200]
        else:
            title, desc = str(item).strip()[:60], ""
        if title:
            out.append({"title": title, "desc": desc})
    return out


def _same_place(a: str, b: str) -> bool:
    """Ίδιος τόπος σε άλλη πτώση; «Πάρο» ↔ «Πάρος», «Γέρακα» ↔ «Γέρακας».

    Συγκρίνουμε το κοινό στέλεχος: οι ελληνικές καταλήξεις αλλάζουν, η ρίζα όχι.
    Σκοπός είναι μόνο να επιτραπεί η διόρθωση πτώσης — ποτέ αλλαγή πόλης."""
    fa, fb = _strip_tones(a).lower(), _strip_tones(b).lower()
    stem = min(len(fa), len(fb), 5)
    return stem >= 3 and fa[:stem] == fb[:stem]


def _is_grounded(text: str, detected_type: str | None) -> bool:
    """Έδωσε ο πελάτης αρκετά ώστε το AI να έχει πάνω σε τι να πατήσει;

    Ίδιος κανόνας με το `site_copy.write_copy`: μια σκέτη κατηγορία («ξενοδοχείο»)
    δεν περιέχει γεγονότα. Το μοντέλο τότε γεμίζει το κενό — για ξενοδοχείο
    επέστρεψε «Πρόσφυση» και «Καθαρισμός δωματίων» χωρίς περιγραφές, που
    εκτόπισαν τις ελεγμένες υπηρεσίες του vertical."""
    words = re.findall(r"[\wά-ώΆ-Ώ]+", text, flags=re.UNICODE)
    without_category = [w for w in words
                        if _strip_tones(w).lower() not in _TRADE_LABELS]
    return len(without_category) >= 4


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
                    # Deterministic extraction wins when it has a value. This
                    # prevents the model from changing an explicit city/name.
                    if not fallback[key] and isinstance(value, str) and value.strip():
                        fallback[key] = value.strip()[:80]
                # Εξαίρεση: το AI διορθώνει την πτώση («στην Πάρο» → «Πάρος»).
                # Δεκτό ΜΟΝΟ αν είναι ο ίδιος τόπος — αλλιώς θα άλλαζε την πόλη
                # που έγραψε ρητά ο πελάτης.
                ai_city = str(data.get("city") or "").strip()[:80]
                if ai_city and fallback["city"] and _same_place(ai_city, fallback["city"]):
                    fallback["city"] = ai_city
                if not fallback["type"]:
                    value = data.get("type")
                    if isinstance(value, str) and value.strip():
                        fallback["type"] = value.strip()[:80]
                if _is_category(fallback["name"], fallback["type"]):
                    fallback["name"] = None
                services = data.get("services")
                # Υπηρεσίες από το AI ΜΟΝΟ όταν ο πελάτης είπε κάτι συγκεκριμένο.
                # Αλλιώς μένουν κενές και το normalize() βάζει τις ελεγμένες του
                # vertical — που έχουν και περιγραφή, όχι μόνο τίτλο.
                if isinstance(services, list) and _is_grounded(text, fallback["type"]):
                    fallback["services"] = _clean_services(services)
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
