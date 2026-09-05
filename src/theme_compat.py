# -*- coding: utf-8 -*-
"""Συμβατότητα theme ↔ επάγγελμα.

Δύο ερωτήματα, μία πηγή αλήθειας:

  · ποιο είναι το ΚΥΡΙΟ επάγγελμα ενός theme
  · σε ποια άλλα επαγγέλματα έχει **δοκιμαστεί** και στέκει

Τίποτα εδώ δεν προκύπτει από οπτική εντύπωση. Οι λίστες βγαίνουν από το
`_TEMPLATES_BY_VERTICAL` — τη χαρτογράφηση που ήδη χρησιμοποιεί η παραγωγή —
και συμπληρώνονται μόνο για themes που έλειπαν εντελώς από αυτήν, με vertical
που επαληθεύτηκε με QA στα δεδομένα του συγκεκριμένου επαγγέλματος.
"""
from __future__ import annotations

from typing import Any

# Themes που δεν υπήρχαν σε κανένα vertical του backend. Το vertical προκύπτει
# από την ταυτότητα του ίδιου του theme και ΕΧΕΙ ΕΛΕΓΧΘΕΙ με το demo business
# αυτού του vertical (research/theme-library/qa.json).
ORPHAN_PRIMARY = {
    "klassy-cafe": "cafe", "frost-bakery": "bakery", "vex-counter": "cafe",
    "barber-shop": "beauty", "billys-barber": "beauty", "thomson-stylist": "beauty",
    "gymso-fitness": "gym", "pulse": "gym",
    "medic-care": "doctor",
    "villa-agency": "realestate", "coast": "rooms",
    "moso-interior": "wood",
    "clean-work": "trade", "dispatch": "trade", "freight-lane": "logistics",
    "blue-onepage": "professional", "airspace-office": "professional",
    "educenter-campus": "education",
}

# Συγγενικά επαγγέλματα: ένα theme κομμωτηρίου στέκει σε κουρείο και σε
# ινστιτούτο αισθητικής — ίδιο μοντέλο περιεχομένου (υπηρεσίες, τιμές,
# ραντεβού, χαρτοφυλάκιο), όχι απλώς παρόμοιο ύφος.
KIN = {
    "beauty": ("beauty", "aesthetics", "massage"),
    "aesthetics": ("aesthetics", "beauty", "massage"),
    "massage": ("massage", "aesthetics", "beauty"),
    "food": ("food", "cafe", "bakery"),
    "cafe": ("cafe", "bakery", "food"),
    "bakery": ("bakery", "cafe", "food"),
    "dentist": ("dentist", "doctor"),
    "doctor": ("doctor", "dentist"),
    "pharmacy": ("pharmacy",),
    "trade": ("trade", "wood", "garage"),
    "wood": ("wood", "trade"),
    "garage": ("garage", "trade"),
    "rooms": ("rooms",),
    "realestate": ("realestate",),
    "retail": ("retail",),
    "gym": ("gym",),
    "professional": ("professional",),
    "education": ("education",),
    "logistics": ("logistics",),
    "farm": ("farm",),
    "pet": ("pet", "retail"),
}

# Από πόσα verticals και πάνω ένα theme θεωρείται πραγματικά γενικού σκοπού.
# Στα 5 έμπαινε και το clinic-triage, που είναι σαφώς ιατρικό και θα χανόταν
# από το φίλτρο «Υγεία». Στα 8 μένουν μόνο όσα το backend χρησιμοποιεί σχεδόν
# παντού.
GENERIC_MIN = 8


def build(by_vertical: dict[str, Any]) -> dict[str, dict]:
    """Χάρτης theme -> {primary, compatible, generic}."""
    seen: dict[str, list[str]] = {}
    for vert, keys in by_vertical.items():
        for k in keys:
            seen.setdefault(k, []).append(vert)

    out: dict[str, dict] = {}
    for k, verts in seen.items():
        # Κύριο = εκεί που κατατάσσεται ψηλότερα· ισοβαθμία → αλφαβητικά,
        # ώστε το αποτέλεσμα να είναι αναπαραγώγιμο.
        primary = min(verts, key=lambda v: (list(by_vertical[v]).index(k), v))
        out[k] = {"primary": primary, "compatible": sorted(set(verts)),
                  "generic": len(verts) >= GENERIC_MIN}
    for k, v in ORPHAN_PRIMARY.items():
        if k in out:
            continue
        out[k] = {"primary": v, "compatible": sorted(set(KIN.get(v, (v,)))), "generic": False}
    return out


def tier(entry: dict, vertical: str) -> int:
    """0 = ακριβές επάγγελμα · 1 = ελεγμένο συγγενικό · 2 = γενικού σκοπού ·
    3 = άσχετο (ΔΕΝ προτείνεται)."""
    if entry["primary"] == vertical:
        return 0
    if vertical in entry["compatible"]:
        return 1
    if entry["generic"]:
        return 2
    return 3


def rank(keys: list[str], compat: dict[str, dict], vertical: str,
         allow_generic: bool = True) -> list[str]:
    """Κατάταξη Α→Γ, με αποκλεισμό των άσχετων. Σταθερή σειρά μέσα σε κάθε
    βαθμίδα: κρατά τη σειρά εισόδου, που είναι η υπάρχουσα κατάταξη."""
    max_tier = 2 if allow_generic else 1
    ranked = []
    for t in range(max_tier + 1):
        ranked += [k for k in keys
                   if k in compat and tier(compat[k], vertical) == t]
    return ranked
