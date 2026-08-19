"""Guards που τρέχουν ΠΡΙΝ ένα port φτάσει σε READY_FOR_REVIEW.

Καθένας υπάρχει επειδή μια συγκεκριμένη αποτυχία πέρασε απαρατήρητη στο πρώτο
proof (Frost Bakery) και έφτασε μέχρι το build:

  contract  — το theme κατανάλωνε `d.name`, `d.about`, `d.hours` που δεν υπάρχουν
              και καλούσε `<Brand d={d}>` αντί `data={d}`. Τέσσερα runtime 500.
  copy_leak — έμειναν αγγλικοί τίτλοι του πρωτοτύπου («Pick your perfect scoop»)
              πάνω από ελληνικό ξυλουργείο. Το trust_guard δεν τους πιάνει:
              δεν είναι ψευδής ισχυρισμός, είναι αμετάφραστο filler.
  media     — το πρωτότυπο έχει 7 φωτογραφίες, το port απέδωσε ΜΗΔΕΝ εικόνες
              γιατί δεν άγγιξε καθόλου το `d.gallery`.

Όλοι αποτυγχάνουν ΚΛΕΙΣΤΑ: αμφιβολία σημαίνει απόρριψη, όχι σιωπηλό πέρασμα.
"""
from __future__ import annotations

import re
from typing import Any

# Πεδία που έγραψα λάθος στο πρώτο συμβόλαιο. Δεν αρκεί να μην τα προτείνουμε —
# αν εμφανιστούν, το port σπάει σε runtime και πρέπει να κοπεί εδώ με όνομα.
KNOWN_BAD_ALIASES = {
    "name": "NAME", "tagline": "TAGLINE", "city": "CITY", "phone": "PHONE",
    "trade": "TRADE", "areas": "AREAS", "intro": "INTRO", "email": "EMAIL",
    "address": "ADDRESS", "hours": "HOURS", "about": "story", "social": "—",
    "mapQuery": "—", "services_list": "services", "images": "gallery",
}


class GuardFailure(RuntimeError):
    """Παράβαση συμβολαίου — το port δεν προχωρά."""


def _jsx_of(files: list[dict[str, str]]) -> tuple[str, str]:
    jsx = next((f["content"] for f in files if f["path"].endswith(".jsx")), "")
    css = next((f["content"] for f in files if f["path"].endswith(".css")), "")
    return jsx, css


# --------------------------------------------------------------- 1. contract
def check_contract(files: list[dict[str, str]], contract: dict[str, Any]) -> list[str]:
    jsx, _ = _jsx_of(files)
    if not jsx:
        return ["δεν βρέθηκε αρχείο .jsx"]
    problems: list[str] = []
    prop = contract["prop_name"]

    sig = re.search(r"export default function \w+\(\{([^}]*)\}\)", jsx)
    if not sig:
        problems.append("δεν βρέθηκε default export με destructured props")
    elif not re.search(rf"\b{prop}\s*:", sig.group(1)):
        problems.append(f"η υπογραφή δεν καταναλώνει το prop «{prop}» που περνά το route: "
                        f"«{sig.group(1).strip()}»")

    known = set(contract["fields"])
    used = set(re.findall(r"\bd\.([A-Za-z_][A-Za-z0-9_]*)", jsx))
    for f in sorted(used - known):
        hint = KNOWN_BAD_ALIASES.get(f)
        problems.append(f"άγνωστο πεδίο d.{f}" + (f" — εννοούσες d.{hint};" if hint else ""))

    # Τύπος: .map() πάνω σε string είναι εγγυημένο runtime crash.
    for f, meta in contract["fields"].items():
        if meta["type"] == "string" and re.search(rf"\bd\.{f}\s*(?:\?\.)?\.?map\(", jsx):
            problems.append(f"d.{f} είναι string αλλά καλείται .map() πάνω του")

    # Shared components με λάθος prop όνομα.
    for comp, expected in contract["canonical_usage"]["shared_prop"].items():
        for m in re.finditer(rf"<{comp}\s+([A-Za-z_]+)=", jsx):
            if m.group(1) != expected:
                problems.append(f"<{comp} {m.group(1)}=…> — περιμένει «{expected}»")

    # Διαδρομές import. Όλα τα themes και τα shared ζουν στον ΙΔΙΟ φάκελο, άρα
    # μόνο `./X`. Το Medic Care έγραψε `../components/Brand` και έσπασε το build
    # — σφάλμα που κοστίζει δύο λεπτά build για να φανεί, ενώ εδώ κοστίζει μηδέν.
    for m in re.finditer(r"from\s+'([^']+)'", jsx):
        path = m.group(1)
        if not path.startswith("./"):
            problems.append(f"import από «{path}» — τα themes και τα shared είναι "
                            "στον ίδιο φάκελο, γράψε './<Name>'")
    return problems


# -------------------------------------------------------------- 2. copy leak
def check_copy_leak(files: list[dict[str, str]], source_html: str,
                    allowed: tuple[str, ...] = ()) -> list[str]:
    """Κείμενο του πρωτοτύπου που έμεινε αμετάφραστο μέσα στο theme.

    Μέθοδος: βγάζουμε τις ορατές φράσεις του πρωτοτύπου, κρατάμε όσες είναι
    ουσιαστικές (>=3 λέξεις ή τιμή/διεύθυνση), και ελέγχουμε ποιες επιβιώνουν
    αυτούσιες στο JSX **έξω από `d.` bindings**.
    """
    jsx, _ = _jsx_of(files)
    if not jsx:
        return ["δεν βρέθηκε αρχείο .jsx"]

    clean = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", source_html)
    phrases = {re.sub(r"\s+", " ", t).strip()
               for t in re.findall(r">([^<>{}]{8,90})<", clean)}
    meaningful = {p for p in phrases
                  if len(p.split()) >= 3 and not p.startswith("&") and any(c.isalpha() for c in p)}

    leaks: list[str] = []
    low_allowed = {a.lower() for a in allowed}
    for p in meaningful:
        if p.lower() in low_allowed:
            continue
        if p in jsx:
            leaks.append(f"κείμενο πρωτοτύπου αυτούσιο: «{p[:70]}»")

    # Ταυτότητα πηγής: τιμές, τηλέφωνα, διευθύνσεις, emails σε literal μορφή.
    for pat, label in ((r"[$€£]\s?\d+(?:[.,]\d+)?", "τιμή"),
                       (r"\b\d{3}[-\s]\d{3}[-\s]\d{4}\b", "τηλέφωνο"),
                       (r"[\w.+-]+@[\w-]+\.[\w.]+", "email"),
                       (r"\b\d{1,4}\s+[A-Z][a-z]+\s+(?:Street|St|Road|Rd|Ave|Avenue)\b", "διεύθυνση")):
        for hit in set(re.findall(pat, jsx)):
            if f"d." in jsx[max(0, jsx.find(hit) - 40):jsx.find(hit)]:
                continue
            leaks.append(f"{label} hardcoded στο theme: «{hit}»")
    return sorted(set(leaks))[:12]


# ------------------------------------------------------------------ 3. media
def check_media(files: list[dict[str, str]], source_html: str) -> list[str]:
    """Αν το πρωτότυπο είναι εικονο-κεντρικό, το port πρέπει να δέσει media.

    Fail closed: όταν το πρωτότυπο έχει ουσιαστικές εικόνες και το theme δεν
    αναφέρει καθόλου `d.gallery`, δεν περνά. Το Frost πέρασε build με ΜΗΔΕΝ
    εικόνες ενώ το πρωτότυπο είχε επτά.
    """
    jsx, _ = _jsx_of(files)
    imgs = len(re.findall(r"<img\b", source_html, re.I))
    bg = len(re.findall(r"background(?:-image)?\s*:\s*url\(", source_html, re.I))
    image_led = (imgs + bg) >= 3
    if not image_led:
        return []
    binds = len(re.findall(r"\bd\.gallery\b", jsx))
    if binds == 0:
        return [f"το πρωτότυπο έχει {imgs} <img> (+{bg} background) αλλά το port "
                "δεν αναφέρει καθόλου d.gallery — καμία εικόνα πελάτη δεν αποδίδεται"]
    if not re.search(r"<img\b", jsx):
        return ["το d.gallery αναφέρεται αλλά δεν υπάρχει κανένα <img> στο theme"]
    return []


# ------------------------------------------------------------------ συνολικά
def run_all(files: list[dict[str, str]], contract: dict[str, Any],
            source_html: str, allowed_labels: tuple[str, ...] = (),
            avail: dict[str, Any] | None = None) -> dict[str, list[str]]:
    """Όλοι οι guards. Το `avail` είναι η ΠΡΑΓΜΑΤΙΚΗ διαθεσιμότητα δεδομένων του
    επιλεγμένου demo — χωρίς αυτό ο έλεγχος δέσμευσης δεν μπορεί να τρέξει."""
    return {
        "contract": check_contract(files, contract),
        "copy_leak": check_copy_leak(files, source_html, allowed_labels),
        "media": check_media(files, source_html),
        "data_binding": check_data_binding(files, avail or {}),
    }


def summarize(results: dict[str, list[str]]) -> str:
    lines = []
    for name, probs in results.items():
        for p in probs:
            lines.append(f"[{name}] {p}")
    return "\n".join(lines)


# ------------------------------------------------- 4. data binding validity
#
# Μετρήθηκε σε τρία themes: το συμβόλαιο έλεγε ποια πεδία ΥΠΑΡΧΟΥΝ στο σχήμα,
# όχι ποια είναι ΓΕΜΑΤΑ για το επιλεγμένο demo. Το μοντέλο έδεσε
# `d.services[].price` ενώ το demo είχε 0/4 τιμές, και το μενού μιας ταβέρνας
# αποδόθηκε ως τέσσερα κενά μαύρα κουτιά με σκέτο «€».
#
# Ο έλεγχος γίνεται στα BINDINGS, όχι στην εμφάνιση: «κενός κύκλος = σφάλμα»
# ήταν ακριβώς η ευρετική που παρήγαγε ψευδώς θετικά στο Gymso.

# Πεδία που δεν επιτρέπεται να καλύψουν τη θέση άλλων. Ένα `num: '01'` δεν
# είναι τιμή, τετραγωνικά, δωμάτια, αξιολόγηση ή έτη.
ORDINAL_FIELDS = ("num", "index", "order", "id")
SEMANTIC_SLOTS = ("price", "cost", "amount", "sqm", "area", "bedrooms",
                  "bathrooms", "rating", "years", "duration")


def check_data_binding(files: list[dict[str, str]], avail: dict[str, Any]) -> list[str]:
    """Κανένα content-bearing στοιχείο χωρίς πραγματικά δεδομένα."""
    jsx, _ = _jsx_of(files)
    if not jsx or not avail:
        return []
    problems: list[str] = []
    arrays = avail.get("arrays", {})

    for arr, var in re.findall(r"d\.([a-z]+)[^)]{0,40}?\.map\(\s*\(?\s*([A-Za-z_]\w*)", jsx):
        meta = arrays.get(arr)
        if not meta:
            continue
        for fld in sorted(set(re.findall(rf"\b{var}\.([a-z][A-Za-z0-9_]*)", jsx))):
            info = meta["fields"].get(fld)
            populated = info["populated"] if info else 0
            total = meta["count"]
            # Υπάρχει έλεγχος συνθήκης για το πεδίο;
            guarded = re.search(rf"{var}\.{fld}\s*(?:&&|\?)", jsx) is not None
            if populated == 0:
                problems.append(
                    f"d.{arr}[].{fld}: το demo «{avail['business']}» έχει 0/{total} τιμές — "
                    "το στοιχείο πρέπει να ΜΗΝ αποδίδεται καθόλου")
            elif populated < total and not guarded:
                problems.append(
                    f"d.{arr}[].{fld}: {populated}/{total} γεμάτα και αποδίδεται χωρίς "
                    "συνθήκη — χρειάζεται έλεγχος ανά στοιχείο")

    # Σημασιολογική υποκατάσταση: ordinal σε θέση μετρήσιμου μεγέθους.
    for ordinal in ORDINAL_FIELDS:
        for m in re.finditer(rf"\.{ordinal}\b", jsx):
            window = jsx[max(0, m.start() - 160):m.start() + 60].lower()
            for slot in SEMANTIC_SLOTS:
                if slot in window and f".{slot}" not in window:
                    problems.append(
                        f"σημασιολογική υποκατάσταση: το `.{ordinal}` αποδίδεται σε θέση "
                        f"«{slot}» — ένα πεδίο δεν καλύπτει τη θέση άλλου")
                    break
    return sorted(set(problems))[:12]
