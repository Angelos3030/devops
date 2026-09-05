#!/usr/bin/env python3
"""Διόρθωση ρόλων αντίθεσης — themes που χρησιμοποιούν λάθος σημασιολογικό ρόλο.

    python scripts/fix_contrast_roles.py [--check]

ΤΟ ΕΥΡΗΜΑ. Ο φρουρός αντίθεσης (sites/artifacts/contrast-guard.mjs) μέτρησε
6.906 κείμενα σε 58 themes × 6 παλέτες × 2 viewports. Οι ΠΑΛΕΤΕΣ είναι σωστές:
και τα 45 ζεύγη ρόλων του συμβολαίου περνούν WCAG AA. Κάθε αστοχία είναι theme
που ζητάει λάθος ρόλο — π.χ. `--vt-ink` (σκούρο κείμενο για ανοιχτή επιφάνεια)
πάνω σε `--vt-accent` ή σε `--vt-surface-deep`.

Γιατί δεν φαινόταν: στη ΔΙΚΗ ΤΟΥ παλέτα το theme πετύχαινε κατά σύμπτωση —
συχνά επειδή δύο ρόλοι είχαν την ίδια τιμή. Μόλις μπει παλέτα πελάτη, οι δύο
ρόλοι αποκλίνουν και το κείμενο εξαφανίζεται.

ΚΑΘΕ ΔΙΟΡΘΩΣΗ ΚΡΑΤΑΕΙ ΤΟ DEFAULT PIXEL-ΙΔΙΟ. Όπου αλλάζει ρόλος, η τιμή του
ρόλου ορίζεται στο σημερινό κυριολεκτικό χρώμα του theme.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "sites" / "lib" / "templates"

# (αρχείο, [(παλιό, νέο, πλήθος, γιατί)])
FIXES: dict[str, list[tuple[str, str, int, str]]] = {

    # ── ConstraBuild — τρία λάθη, όλα από τη δική μου μετάβαση ────────────
    "ConstraBuild.module.css": [
        # 1. Το --steel είναι ΣΚΟΥΡΗ ΕΠΙΦΑΝΕΙΑ (φόντο hero), όχι accent-ως-κείμενο.
        #    Το είχα χαρτογραφήσει σε accent-ink· με παλέτα mono και τα δύο
        #    γίνονταν #151515 και το κείμενο έπεφτε σε 1:1.
        ("--vt-surface-deep:#171717;", "--vt-surface-deep:#3c4145;", 1,
         "το πραγματικό σκούρο του theme είναι το #3c4145 του hero"),
        ("--vt-on-deep:#f5f4ef;", "--vt-on-deep:#ffffff;", 1,
         "το hero γράφει ήδη λευκό — ο ρόλος παίρνει την ίδια τιμή"),
        ("--steel: var(--vt-accent-ink)", "--steel: var(--vt-surface-deep)", 1,
         "σκούρο φόντο, όχι χρώμα κειμένου"),
        # 2. Λευκό κείμενο σε σκούρο hero -> ο ρόλος που το εγγυάται.
        ("background: var(--steel);\n  color: white;",
         "background: var(--steel);\n  color: var(--vt-on-deep);", 1,
         "ρητός ρόλος αντί για κυριολεκτικό λευκό"),
        # 3. Κείμενο πάνω στο κίτρινο accent: --black (=ink) -> on-accent.
        ("background: var(--yellow);\n  color: var(--black) !important;",
         "background: var(--yellow);\n  color: var(--vt-on-accent) !important;", 1,
         "κείμενο πάνω σε accent θέλει on-accent"),
        # 4. Το kicker του hero είναι κίτρινο ΠΑΝΩ ΣΤΟ ΣΚΟΥΡΟ hero — άρα
        #    accent-on-deep. Ο ίδιος κανόνας βάφει και δύο ενότητες σε ανοιχτό
        #    φόντο, οπότε σπάει στα δύο: καθεμιά παίρνει τον ρόλο της.
        # ΠΡΩΤΗ ΠΡΟΣΠΑΘΕΙΑ ΗΤΑΝ ΛΑΘΟΣ, ΚΑΙ ΤΟ ΕΠΙΑΣΕ Η ΣΥΓΚΡΙΣΗ PIXEL.
        # Είχα σπάσει τον κοινό κανόνα σε δύο, δίνοντας στο `.hero > div p`
        # μόνο `color`. Έχανε έτσι τα font-size / text-transform /
        # letter-spacing του αρχικού και το default άλλαξε 39% στο mobile.
        # Σωστό: ο κοινός κανόνας μένει ΑΘΙΚΤΟΣ, και μπαίνει override αμέσως
        # μετά — μόνο χρώμα, μόνο για το σκούρο hero.
        ("  color: var(--yellow);\n  font-size: 0.7rem;",
         "  color: var(--yellow);\n  font-size: 0.7rem;", 1,
         "(ο κοινός κανόνας επιβεβαιώθηκε ανέπαφος)"),
    ],

    # ── BigspringAdvisory — kicker 11px με accent ως κείμενο ──────────────
    # Το accent είναι ΦΟΝΤΟ κουμπιού. Ως κείμενο 11px πάνω στο surface-2 του
    # hero έδινε 3,76:1 με ροζ. Ο ρόλος accent-ink υπάρχει ακριβώς γι' αυτό
    # και μετρήθηκε 4,56-5,13:1 σε όλες τις παλέτες.
    "BigspringAdvisory.module.css": [
        ("letter-spacing:.18em;color:var(--indigo)",
         "letter-spacing:.18em;color:var(--vt-accent-ink)", 1,
         "kicker: accent -> accent-ink"),
    ],

    # ── NovenaCare — ίδιο μοτίβο ──────────────────────────────────────────
    "NovenaCare.module.css": [
        (".copy>p,.services header p,.approach>div>p{color:var(--blue);",
         ".copy>p,.services header p,.approach>div>p{color:var(--vt-accent-ink);", 1,
         "kicker: accent -> accent-ink"),
    ],
}


# Κανόνες που ΠΡΟΣΤΙΘΕΝΤΑΙ στο τέλος του αρχείου. Προτιμώνται από την
# τροποποίηση υπάρχοντος κανόνα όταν αυτός εξυπηρετεί ΠΟΛΛΑ context: τον
# αφήνουμε ανέπαφο και τον υπερισχύουμε μόνο εκεί που χρειάζεται.
APPEND: dict[str, str] = {
    "ConstraBuild.module.css":
        "\n/* Το kicker του hero κάθεται στο ΣΚΟΥΡΟ .hero. Ο κοινός κανόνας το\n"
        "   βάφει accent, που είναι φτιαγμένο για ανοιχτή επιφάνεια — με παλέτα\n"
        "   mono έπεφτε σε 1:1. Αλλάζει ΜΟΝΟ το χρώμα· μέγεθος, κεφαλαία και\n"
        "   αραίωση μένουν στον κοινό κανόνα. */\n"
        ".hero > div p { color: var(--vt-accent-on-deep); }\n",
}


def main() -> None:
    check = "--check" in sys.argv
    total = 0
    for fname, subs in FIXES.items():
        p = T / fname
        s = io.open(p, encoding="utf-8").read()
        applied = 0
        for old, new, n, why in subs:
            if new in s and old not in s:
                print(f"  ↷ {fname}: ήδη διορθωμένο — {why}")
                continue
            got = s.count(old)
            assert got == n, f"{fname}: «{old[:52]}» βρέθηκε {got}×, περίμενα {n}"
            s = s.replace(old, new, n)
            applied += 1
            print(f"  ✓ {fname:<30} {why}")
        extra = APPEND.get(fname)
        if extra and extra.strip().splitlines()[-1] not in s:
            s = s.rstrip() + "\n" + extra
            applied += 1
            print(f"  ✓ {fname:<30} override στο τέλος του αρχείου")
        if applied and not check:
            io.open(p, "w", encoding="utf-8").write(s)
        total += applied
    print(f"\n{total} διορθώσεις" + (" (έλεγχος μόνο)" if check else ""))


if __name__ == "__main__":
    main()
