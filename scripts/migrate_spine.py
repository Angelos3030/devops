#!/usr/bin/env python3
"""Μετάβαση των έξι themes του port-worker στο κοινό συμβόλαιο χρώματος.

    python scripts/migrate_spine.py            # εφαρμογή
    python scripts/migrate_spine.py --check    # μόνο έλεγχος, χωρίς εγγραφή

ΤΟ ΠΡΟΒΛΗΜΑ. Έξι themes ήρθαν από τον port-worker με δική τους ιδιωτική
παλέτα (`--rose`, `--indigo`, `--forest`…) και μηδέν `var(--vt-*)`. Ο πελάτης
που τα διάλεγε έβλεπε το dropdown «Χρωματική παλέτα» να μην κάνει τίποτα:
μετρήθηκε 0/11 ρόλοι δηλωμένοι, 0 χρήσεις.

Η ΜΕΤΑΒΑΣΗ ΔΕΝ ΑΛΛΑΖΕΙ ΚΑΝΕΝΑ ΧΡΩΜΑ. Κάθε ρόλος του spine δηλώνεται με την
ΑΚΡΙΒΩΣ σημερινή τιμή του theme, και τα ιδιωτικά ονόματα δείχνουν πλέον στους
ρόλους. Στο `original` το αποτέλεσμα είναι pixel-ίδιο εξ ορισμού· όταν ο
πελάτης διαλέξει παλέτα, το `.scope[data-palette]` ξαναγράφει τους ρόλους στο
ίδιο στοιχείο και τα ιδιωτικά ονόματα ακολουθούν.

ΤΙ ΔΕΝ ΜΕΤΑΦΕΡΕΤΑΙ. Δευτερεύουσες τρίχινες γραμμές που έχουν δική τους
απόχρωση (π.χ. τρία διαφορετικά borders στο EleganceSalon) μένουν ως έχουν:
αν τα ισοπέδωνα σε έναν ρόλο, θα άλλαζε το default — που είναι το μόνο
αδιαπραγμάτευτο κριτήριο εδώ.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "sites" / "lib" / "templates"

# Οι έντεκα ρόλοι, με τη σειρά που τους δηλώνει το theme.module.css.
ROLES = ("surface", "surface-2", "surface-deep", "ink", "ink-soft", "on-deep",
         "accent", "on-accent", "accent-ink", "accent-on-deep", "line")


def spine(**vals: str) -> str:
    missing = [r for r in ROLES if r.replace("-", "_") not in vals]
    assert not missing, f"λείπουν ρόλοι: {missing}"
    return "".join(f"--vt-{r}:{vals[r.replace('-', '_')]};" for r in ROLES)


# ── ανά theme: (αρχείο, δηλώσεις spine, αντικαταστάσεις) ────────────────────
# Κάθε αντικατάσταση είναι (παλιό, νέο, πλήθος). Το πλήθος επαληθεύεται.
PLAN: dict[str, tuple[str, str, list[tuple[str, str, int]]]] = {

    "EleganceSalon": (
        "EleganceSalon.module.css",
        spine(surface="#fff9f7", surface_2="#f5e1df", surface_deep="#21191c",
              ink="#20191c", ink_soft="#6f6264", on_deep="#ffffff",
              accent="#d94969", on_accent="#ffffff", accent_ink="#d94969",
              accent_on_deep="#e88ba0", line="#dfd1cf"),
        [
            ("--rose:#d94969", "--rose:var(--vt-accent)", 1),
            ("--ink:#20191c", "--ink:var(--vt-ink)", 1),
            ("--paper:#fff9f7", "--paper:var(--vt-surface)", 1),
            ("--blush:#f5e1df", "--blush:var(--vt-surface-2)", 1),
            ("border-bottom:1px solid #dfd1cf", "border-bottom:1px solid var(--vt-line)", 1),
            ("color:#6f6264", "color:var(--vt-ink-soft)", 1),
            ("background:#21191c;color:white", "background:var(--vt-surface-deep);color:var(--vt-on-deep)", 1),
            ("background:var(--rose);color:white!important", "background:var(--vt-accent);color:var(--vt-on-accent)!important", 1),
            ("background:var(--rose);color:white", "background:var(--vt-accent);color:var(--vt-on-accent)", 1),
            # δύο σημεία χρησιμοποιούν το accent ΩΣ ΚΕΙΜΕΝΟ πάνω σε ανοιχτό
            ("color:var(--rose)", "color:var(--vt-accent-ink)", 2),
        ],
    ),

    "BigspringAdvisory": (
        "BigspringAdvisory.module.css",
        spine(surface="#ffffff", surface_2="#e8f0ff", surface_deep="#28377f",
              ink="#151827", ink_soft="#5b6073", on_deep="#ffffff",
              accent="#28377f", on_accent="#ffffff", accent_ink="#28377f",
              accent_on_deep="#c9f36a", line="#b8bdd3"),
        [
            ("--indigo:#28377f", "--indigo:var(--vt-accent)", 1),
            ("--lime:#c9f36a", "--lime:var(--vt-accent-on-deep)", 1),
            ("--sky:#e8f0ff", "--sky:var(--vt-surface-2)", 1),
            ("--ink:#151827", "--ink:var(--vt-ink)", 1),
            ("--paper:#fff", "--paper:var(--vt-surface)", 1),
            ("#5b6073", "var(--vt-ink-soft)", 2),
            ("#b8bdd3", "var(--vt-line)", 5),
        ],
    ),

    "NovenaCare": (
        "NovenaCare.module.css",
        spine(surface="#fbfcfa", surface_2="#d9f1ef", surface_deep="#142b3b",
              ink="#24313a", ink_soft="#5e6b72", on_deep="#ffffff",
              accent="#176b87", on_accent="#ffffff", accent_ink="#176b87",
              accent_on_deep="#d9f1ef", line="#dce6e4"),
        [
            ("--blue:#176b87", "--blue:var(--vt-accent)", 1),
            ("--aqua:#d9f1ef", "--aqua:var(--vt-surface-2)", 1),
            ("--navy:#142b3b", "--navy:var(--vt-surface-deep)", 1),
            ("--paper:#fbfcfa", "--paper:var(--vt-surface)", 1),
            ("--ink:#24313a", "--ink:var(--vt-ink)", 1),
            ("#5e6b72", "var(--vt-ink-soft)", 2),
            ("#dce6e4", "var(--vt-line)", 2),
        ],
    ),

    "GreckoTable": (
        "GreckoTable.module.css",
        spine(surface="#f3ead7", surface_2="#ffffff", surface_deep="#174d3b",
              ink="#201d18", ink_soft="#655d50", on_deep="#f3ead7",
              accent="#b62f27", on_accent="#ffffff", accent_ink="#b62f27",
              accent_on_deep="#f3ead7", line="#9d927f"),
        [
            ("--red:#b62f27", "--red:var(--vt-accent)", 1),
            ("--cream:#f3ead7", "--cream:var(--vt-surface)", 1),
            ("--green:#174d3b", "--green:var(--vt-surface-deep)", 1),
            ("--ink:#201d18", "--ink:var(--vt-ink)", 1),
            ("#655d50", "var(--vt-ink-soft)", 2),
            ("#9d927f", "var(--vt-line)", 3),
        ],
    ),

    "ConstraBuild": (
        "ConstraBuild.module.css",
        spine(surface="#f5f4ef", surface_2="#ffffff", surface_deep="#171717",
              ink="#171717", ink_soft="#5e6061", on_deep="#f5f4ef",
              accent="#f2bd18", on_accent="#171717", accent_ink="#3c4145",
              accent_on_deep="#f2bd18", line="#d2d0c7"),
        [
            ("--yellow: #f2bd18", "--yellow: var(--vt-accent)", 1),
            ("--black: #171717", "--black: var(--vt-ink)", 1),
            ("--steel: #3c4145", "--steel: var(--vt-accent-ink)", 1),
            ("--paper: #f5f4ef", "--paper: var(--vt-surface)", 1),
            ("#5e6061", "var(--vt-ink-soft)", 2),
            ("#d2d0c7", "var(--vt-line)", 2),
        ],
    ),

    "PropertyAtlas": (
        "PropertyAtlas.module.css",
        spine(surface="#f7f4ec", surface_2="#c8edda", surface_deep="#173d35",
              ink="#16211e", ink_soft="#6c756f", on_deep="#f7f4ec",
              accent="#e96135", on_accent="#ffffff", accent_ink="#173d35",
              accent_on_deep="#c8edda", line="#c7d2ce"),
        [
            ("--forest: #173d35", "--forest: var(--vt-surface-deep)", 1),
            ("--mint: #c8edda", "--mint: var(--vt-surface-2)", 1),
            ("--paper: #f7f4ec", "--paper: var(--vt-surface)", 1),
            ("--orange: #e96135", "--orange: var(--vt-accent)", 1),
            ("--ink: #16211e", "--ink: var(--vt-ink)", 1),
            ("#6c756f", "var(--vt-ink-soft)", 2),
            ("#c7d2ce", "var(--vt-line)", 2),
        ],
    ),
}

MARK = "/* spine */"


def main() -> None:
    check = "--check" in sys.argv
    for name, (fname, decls, subs) in PLAN.items():
        p = T / fname
        s = io.open(p, encoding="utf-8").read()
        if MARK in s:
            print(f"  ↷ {name}: έχει ήδη μεταφερθεί")
            continue

        # 1. οι ρόλοι μπαίνουν στην ΑΡΧΗ του .root, με τα σημερινά χρώματα
        i = s.find(".root{")
        j = s.find(".root {")
        start = i if i != -1 else j
        assert start != -1, f"{name}: δεν βρέθηκε .root"
        brace = s.index("{", start) + 1
        s = s[:brace] + MARK + decls + s[brace:]

        # 2. τα ιδιωτικά ονόματα δείχνουν στους ρόλους
        for old, new, n in subs:
            got = s.count(old)
            assert got == n, f"{name}: «{old[:40]}» βρέθηκε {got}×, περίμενα {n}"
            s = s.replace(old, new, n)

        if not check:
            io.open(p, "w", encoding="utf-8").write(s)
        print(f"  ✓ {name:<20} {len(subs)} αντικαταστάσεις + 11 ρόλοι")

    print("\n" + ("έλεγχος μόνο — καμία εγγραφή" if check else "γράφτηκαν"))


if __name__ == "__main__":
    main()
