"""Regression matrix for Greek free-text business classification.

Every case mirrors the risky onboarding path: the select is "Άλλο" and the
useful profession exists only in description. Run before every backend deploy.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import premium_generator as pg


CASES = {
    # Food / hospitality
    "Έχω ταβέρνα στον Βύρωνα": "food",
    "Μικρό καφέ και brunch στο Παγκράτι": "cafe",
    "Οικογενειακό ζαχαροπλαστείο": "cafe",
    "Φούρνος και αρτοποιείο": "cafe",
    # Trades
    "Υδραυλικός για βλάβες": "trade",
    "Ηλεκτρολόγος εγκαταστάσεων": "trade",
    "Ελαιοχρωματιστής Αθήνα": "trade",
    "Ψυκτικός και service κλιματιστικών": "trade",
    "Ξυλουργός και επιπλοποιός": "wood",
    "Συνεργείο αυτοκινήτων": "garage",
    "Βουλκανιζατέρ": "garage",
    # Professional services
    "Δικηγορικό γραφείο": "professional",
    "Λογιστής και φοροτεχνικός": "professional",
    "Συμβολαιογράφος": "professional",
    "Πολιτικός μηχανικός": "professional",
    "Αρχιτέκτονας εσωτερικών χώρων": "professional",
    "Μεσιτικό γραφείο": "professional",
    "Ασφαλιστής": "professional",
    # Health
    "Οδοντιατρείο": "dentist",
    "Παιδίατρος": "doctor",
    "Καρδιολόγος": "doctor",
    "Φυσικοθεραπευτής": "doctor",
    "Ψυχολόγος": "doctor",
    "Διαιτολόγος": "doctor",
    "Κτηνίατρος": "doctor",
    # Beauty / wellness
    "Κομμωτήριο": "beauty",
    "Barbershop": "beauty",
    "Νυχάδικο": "beauty",
    "Νύχια": "beauty",
    "νυχια": "beauty",
    "Nixia": "beauty",
    "Nyxia": "beauty",
    "Nuxia": "beauty",
    "Nail salon": "beauty",
    "Μανικιούρ και πεντικιούρ": "beauty",
    "Κέντρο αισθητικής και laser αποτρίχωση": "aesthetics",
    "Κέντρο μασάζ": "massage",
    "Γυμναστήριο και personal training": "gym",
    # Lodging / production
    "Ενοικιαζόμενα δωμάτια": "rooms",
    "Ξενώνας": "rooms",
    "Παραγωγός ελαιολάδου": "farm",
    "Μελισσοκόμος": "farm",
    "Οινοποιείο": "farm",
    # Retail
    "Κατάστημα ρούχων": "retail",
    "Boutique γυναικείων ρούχων": "retail",
    "Ανθοπωλείο": "retail",
    "Κατάστημα υποδημάτων": "retail",
    "Κοσμηματοπωλείο": "retail",
    "Βιβλιοπωλείο": "retail",
}


def main() -> int:
    failures = []
    for description, expected in CASES.items():
        intake = {"type": "Άλλο", "description": description, "city": "Αθήνα"}
        actual = pg._vertical(intake)
        templates = pg.recommend_templates(intake)
        if actual != expected or len(templates) != 5:
            failures.append((description, expected, actual, templates[:3]))

    if failures:
        for description, expected, actual, templates in failures:
            print(f"FAIL {description!r}: expected={expected}, actual={actual}, templates={templates}")
        return 1

    print(f"vertical matrix: {len(CASES)}/{len(CASES)} free-text professions passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
