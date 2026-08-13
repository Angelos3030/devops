# -*- coding: utf-8 -*-
"""Σημασιολογία εικόνων: τι ΕΙΝΑΙ μια εικόνα και πού επιτρέπεται να μπει.

Το benchmark των 10 sites έδειξε ότι το πρόβλημα δεν ήταν η ποιότητα των stock
φωτογραφιών — ήταν η **θέση** τους. Μια άψογη φωτογραφία ξένου ιατρείου κάτω από
τον τίτλο «Ο χώρος μας» είναι ψέμα· η ίδια φωτογραφία ως ατμόσφαιρα σε hero δεν
είναι. Άρα η εικόνα χρειάζεται τάξη, και κάθε ενότητα χρειάζεται άδεια.

ΚΛΑΣΕΙΣ
    REAL_BUSINESS      Πραγματική φωτογραφία της επιχείρησης, γενική.
    REAL_OWNER_PERSON  Πραγματικό πρόσωπο ιδιοκτήτη/επαγγελματία.
    REAL_WORK          Πραγματική δουλειά/προϊόν του πελάτη.
    REAL_SPACE         Ο πραγματικός χώρος του.
    ILLUSTRATIVE       Νόμιμο stock, σημασμένο ως ενδεικτικό.
    GENERATED          AI/σχεδιασμένο υλικό, σημασμένο ως τέτοιο.

ΚΑΝΟΝΑΣ: καμία ILLUSTRATIVE ή GENERATED εικόνα δεν μπαίνει ποτέ σε ενότητα που
ισχυρίζεται ταυτότητα — πρόσωπο, ομάδα, «ο χώρος μας», «η δουλειά μας»,
πελάτες/ασθενείς. Απουσία πραγματικού υλικού σημαίνει **τυπογραφική
παρουσίαση**, όχι δανεικό πρόσωπο.

Το module είναι καθαρό: δεν ξέρει από themes, δεν γράφει HTML, δεν καλεί δίκτυο.
"""
from __future__ import annotations

from typing import Any, Iterable

REAL_BUSINESS = "REAL_BUSINESS"
REAL_OWNER_PERSON = "REAL_OWNER_PERSON"
REAL_WORK = "REAL_WORK"
REAL_SPACE = "REAL_SPACE"
ILLUSTRATIVE = "ILLUSTRATIVE"
GENERATED = "GENERATED"

CLASSES = (REAL_BUSINESS, REAL_OWNER_PERSON, REAL_WORK, REAL_SPACE, ILLUSTRATIVE, GENERATED)
REAL_CLASSES = frozenset((REAL_BUSINESS, REAL_OWNER_PERSON, REAL_WORK, REAL_SPACE))
BORROWED_CLASSES = frozenset((ILLUSTRATIVE, GENERATED))

# Ποιες κλάσεις δέχεται κάθε ενότητα που εμφανίζει εικόνα.
# Κενό σύνολο = η ενότητα ΔΕΝ παίρνει ποτέ εικόνα (π.χ. μαρτυρίες πελατών: δεν
# υπάρχει τίμιος τρόπος να δείξεις «πελάτη» με stock).
SECTION_POLICY: dict[str, frozenset[str]] = {
    # Ατμόσφαιρα — δεν ισχυρίζεται ταυτότητα, άρα δέχεται και δανεικό υλικό.
    "hero": frozenset((REAL_BUSINESS, REAL_WORK, REAL_SPACE, ILLUSTRATIVE, GENERATED)),
    "atmosphere": frozenset((REAL_BUSINESS, REAL_WORK, REAL_SPACE, ILLUSTRATIVE, GENERATED)),
    "background": frozenset((REAL_BUSINESS, REAL_WORK, REAL_SPACE, ILLUSTRATIVE, GENERATED)),
    # Ισχυρισμοί ταυτότητας — ΜΟΝΟ πραγματικό υλικό.
    "portrait": frozenset((REAL_OWNER_PERSON,)),
    "practitioner": frozenset((REAL_OWNER_PERSON,)),
    "team": frozenset((REAL_OWNER_PERSON,)),
    "work": frozenset((REAL_WORK,)),
    "gallery_work": frozenset((REAL_WORK,)),
    "space": frozenset((REAL_SPACE, REAL_BUSINESS)),
    "storefront": frozenset((REAL_SPACE, REAL_BUSINESS)),
    # Προϊόν: πραγματικό, ή ενδεικτικό ΜΕ σήμανση (το «σημασμένο» επιβάλλεται
    # παρακάτω από το `caption_for`).
    "product": frozenset((REAL_WORK, REAL_BUSINESS, ILLUSTRATIVE)),
    # Δεν υπάρχει τίμια stock εκδοχή αυτών.
    "testimonial": frozenset(),
    "customers": frozenset(),
    "patients": frozenset(),
    "before_after": frozenset((REAL_WORK,)),
}

# Τίτλοι που ΙΣΧΥΡΙΖΟΝΤΑΙ ταυτότητα. Αν η ενότητα γεμίζει με δανεικό υλικό, ο
# τίτλος πρέπει να αλλάξει — όχι η εικόνα να μείνει με ψεύτικη λεζάντα.
IDENTITY_TITLES = {
    "space": ("Ο χώρος μας", "Το κατάστημά μας", "Στον χώρο μας"),
    "work": ("Δουλειές μας", "Έργα μας", "Η δουλειά μας"),
    "team": ("Η ομάδα μας", "Οι άνθρωποί μας"),
    "portrait": ("Ποιος είμαι", "Γνώρισέ με"),
}
NEUTRAL_TITLE = {
    "space": "Πού θα μας βρεις",
    "work": "Τι αναλαμβάνουμε",
    "team": "Πώς δουλεύουμε",
    "portrait": "Λίγα λόγια",
}


class Asset:
    """Μία εικόνα με τη σημασία της. Η κλάση ΔΕΝ μαντεύεται — δηλώνεται."""

    __slots__ = ("url", "media_class", "title", "source")

    def __init__(self, url: str, media_class: str, title: str = "", source: str = "") -> None:
        if media_class not in CLASSES:
            raise ValueError(f"άγνωστη κλάση εικόνας: {media_class!r}")
        self.url, self.media_class, self.title, self.source = url, media_class, title, source

    @property
    def is_real(self) -> bool:
        return self.media_class in REAL_CLASSES

    def to_dict(self) -> dict[str, Any]:
        return {"image": self.url, "title": self.title, "media_class": self.media_class,
                "illustrative": not self.is_real, "source": self.source}

    def __repr__(self) -> str:  # pragma: no cover
        return f"Asset({self.media_class}, {self.title!r})"


def classify_upload(kind: str) -> str:
    """Μετατρέπει την ΕΠΙΛΟΓΗ ΤΟΥ ΧΡΗΣΤΗ σε κλάση.

    Ο χρήστης λέει τι ανεβάζει· δεν το συμπεραίνουμε από το αρχείο. Ένα μοντέλο
    που μαντεύει «αυτό είναι ο χώρος σου» θα κάνει λάθος και το λάθος θα
    δημοσιευτεί ως ισχυρισμός.
    """
    mapping = {
        "space": REAL_SPACE, "χώρος": REAL_SPACE,
        "work": REAL_WORK, "δουλειά": REAL_WORK, "προϊόν": REAL_WORK,
        "person": REAL_OWNER_PERSON, "πρόσωπο": REAL_OWNER_PERSON,
        "business": REAL_BUSINESS, "επιχείρηση": REAL_BUSINESS,
    }
    return mapping.get(str(kind).strip().lower(), REAL_BUSINESS)


def allowed(section: str, asset: Asset) -> bool:
    return asset.media_class in SECTION_POLICY.get(section, frozenset())


def select(section: str, assets: Iterable[Asset], limit: int = 8) -> list[Asset]:
    """Ό,τι επιτρέπεται σε αυτή την ενότητα, με τα πραγματικά πρώτα."""
    ok = [a for a in assets if allowed(section, a)]
    ok.sort(key=lambda a: (not a.is_real,))
    return ok[:limit]


def title_for(section: str, assets: Iterable[Asset], preferred: str = "") -> str:
    """Ο τίτλος ακολουθεί την ΑΛΗΘΕΙΑ του υλικού, όχι το αντίστροφο."""
    chosen = list(assets)
    if chosen and all(a.is_real for a in chosen):
        return preferred or (IDENTITY_TITLES.get(section) or (NEUTRAL_TITLE.get(section, ""),))[0]
    return NEUTRAL_TITLE.get(section, preferred or "")


def caption_for(asset: Asset) -> str:
    """Δανεικό υλικό φέρει πάντα σήμανση δίπλα του, όχι σε υποσέλιδο 10px."""
    if asset.is_real:
        return asset.title
    mark = "Ενδεικτική εικόνα" if asset.media_class == ILLUSTRATIVE else "Εικόνα σχεδιασμένη από εμάς"
    return f"{asset.title} · {mark}".strip(" ·")


def plan(assets: Iterable[Asset], sections: Iterable[str]) -> dict[str, Any]:
    """Τι μπορεί να δείξει τίμια αυτό το site με το υλικό που υπάρχει.

    Επιστρέφει και το `typographic`: όταν καμία ενότητα ταυτότητας δεν μπορεί να
    γεμίσει με πραγματικό υλικό, η σωστή απάντηση είναι τυπογραφική παρουσίαση —
    όχι δανεικό πρόσωπο.
    """
    items = list(assets)
    per_section = {s: select(s, items) for s in sections}
    identity_sections = [s for s in sections if SECTION_POLICY.get(s, frozenset()) <= REAL_CLASSES]
    filled = [s for s in identity_sections if per_section.get(s)]
    return {
        "sections": per_section,
        "real_count": sum(1 for a in items if a.is_real),
        "identity_sections": identity_sections,
        "identity_filled": filled,
        "typographic": not filled,
    }
