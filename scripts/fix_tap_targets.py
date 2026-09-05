#!/usr/bin/env python3
"""Δίνει ≥44×44px περιοχή αφής, ΧΩΡΙΣ να μεγαλώσει κανένα ορατό κουτί.

    python scripts/fix_tap_targets.py --check
    python scripts/fix_tap_targets.py

Πηγή: research/tap-classification.json (τι πράγματι απέτυχε, σε 390/360/320).

ΤΙ ΔΕΝ ΚΑΝΕΙ. Δεν αλλάζει γραμματοσειρές, χρώματα, σύνθεση ή desktop. Ο στόχος
δεν είναι «κάθε κουμπί 44px ψηλό» — είναι να μη χάνει ο χρήστης το πάτημα.

ΤΕΧΝΙΚΗ. Ένα αόρατο ψευδο-στοιχείο απλώνει την περιοχή αφής γύρω από το
χειριστήριο. Δεν ζωγραφίζει τίποτα, δεν πιάνει χώρο στη ροή, άρα η διάταξη
μένει ακριβώς ίδια — σε αντίθεση με `min-height`, που θα μεγάλωνε ορατά κουτιά.

Για στοιχεία `display:inline` το ψευδο-στοιχείο δεν αρκεί (δεν τοποθετείται
αξιόπιστα σε σπασμένη γραμμή), οπότε μπαίνει κατακόρυφο padding με αντίθετο
margin: η περιοχή αφής μεγαλώνει, η ροή του κειμένου δεν κουνιέται.

ΣΥΓΚΡΟΥΣΕΙΣ. Το `::after` χρησιμοποιείται μόνο αν είναι ελεύθερο· αλλιώς
`::before`. Αν και τα δύο είναι πιασμένα, το στοιχείο ΔΕΝ αγγίζεται και
αναφέρεται — καλύτερα ένα γνωστό κενό παρά σβησμένη διακόσμηση.
"""
from __future__ import annotations

import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "sites" / "lib" / "templates"
DATA = ROOT / "research" / "tap-classification.json"
MARK = "ΠΕΡΙΟΧΗ ΑΦΗΣ 44px"
BREAK = 780  # ίδιο σημείο θραύσης με τα themes


def selector_from(path: str) -> tuple[str, str] | None:
    """«nav.CafeCollection_patNav > a» -> (CafeCollection, '.patNav > a')."""
    parts = path.split(" > ")
    # Το `theme_scope` είναι το κοινό περίβλημα ΟΛΩΝ των themes — δεν
    # ταυτοποιεί αρχείο και δεν χρησιμεύει ως άγκυρα.
    classed = [(i, m.group(1), m.group(2))
               for i, p in enumerate(parts)
               if (m := re.match(r"[a-z0-9]+\.([A-Za-z0-9]+)_(.+)$", p))
               and m.group(1) != "theme"]
    if not classed:
        return None
    file = classed[0][1]
    # Άγκυρα: η ΠΛΗΣΙΕΣΤΕΡΗ κλάση στο στοιχείο. Χωρίς αυτό, διαδρομές που
    # τελειώνουν σε «div > a» έδιναν selector που ταίριαζε παντού και
    # παραλείπονταν — 51 από τους 100.
    anchor_i, _, anchor_cls = classed[-1]
    sel = ["." + anchor_cls]
    for seg in parts[anchor_i + 1:]:
        m = re.match(r"([a-z0-9]+)\.[A-Za-z0-9]+_(.+)$", seg)
        sel.append("." + m.group(2) if m else seg.split(".")[0])
    return file, " > ".join(sel)


def main() -> None:
    check = "--check" in sys.argv
    rows = [r for r in json.loads(io.open(DATA, encoding="utf-8").read()) if not r.get("err")]

    groups: dict[tuple[str, str], dict] = {}
    skipped: list[str] = []
    for r in rows:
        got = selector_from(r["path"])
        if not got:
            skipped.append(f"{r['theme']}  {r['path']}")
            continue
        file, sel = got
        g = groups.setdefault((file, sel), {
            "inline": True, "after": False, "before": False,
            "h": 99, "w": 999, "themes": set(), "roles": set(), "ex": r["text"]})
        g["inline"] &= (r["display"] == "inline")
        g["after"] |= bool(r.get("afterUsed"))
        g["before"] |= bool(r.get("beforeUsed"))
        g["h"] = min(g["h"], r["h"])
        g["w"] = min(g["w"], r["w"])
        g["themes"].add(r["theme"])
        g["roles"].add(r["role"])

    per_file: dict[str, list[str]] = defaultdict(list)
    stats = defaultdict(int)
    blocked: list[str] = []

    for (file, sel), g in sorted(groups.items()):
        why = (f"{', '.join(sorted(g['roles']))} · {g['h']}px ύψος"
               + (f", {g['w']}px πλάτος" if g["w"] < 44 else "")
               + f" · {len(g['themes'])} theme(s)"
               + (f" · «{g['ex']}»" if g["ex"] else ""))
        if g["inline"]:
            stats["inline"] += 1
            per_file[file].append(
                f"  /* {why} — inline: κατακόρυφο padding με αντίθετο margin,\n"
                f"     ώστε η περιοχή αφής να μεγαλώσει χωρίς να κουνηθεί η γραμμή. */\n"
                f"  {sel} {{ padding-block: 12px; margin-block: -12px; }}")
            continue
        pseudo = "::after" if not g["after"] else ("::before" if not g["before"] else None)
        if pseudo is None:
            blocked.append(f"{file} {sel} — και τα δύο ψευδο-στοιχεία πιασμένα")
            continue
        # ΚΑΤΕΥΘΥΝΣΗ. Το λογότυπο κάθεται συνήθως ΠΑΝΩ από τη σειρά πλοήγησης,
        # με ελάχιστο κενό ανάμεσα: μετρήθηκε λογότυπο που τελειώνει στο 87 και
        # σύνδεσμοι που ξεκινούν στο 88. Κεντραρισμένη επέκταση 44px κατέβαινε
        # στο 91,5 και ΕΚΛΕΒΕ το πάτημα από τέσσερις συνδέσμους. Πάνω από το
        # λογότυπο υπάρχει χώρος· από κάτω όχι.
        is_brand = bool(re.search(r"logo|brand|monogram", sel, re.I))
        box = ("left: 50%; bottom: 0; transform: translateX(-50%);" if is_brand
               else "left: 50%; top: 50%; transform: translate(-50%, -50%);")
        stats["προς τα πάνω" if is_brand else "κεντραρισμένο"] += 1
        # `:not(:empty)` — ΚΕΝΟΣ σύνδεσμος δεν παίρνει περιοχή αφής.
        # Χωρίς τηλέφωνο ο σύνδεσμος αποδίδεται με πλάτος 0· η επέκταση του
        # έδινε κουτί 44px που έβγαινε εκτός οθόνης και δημιουργούσε οριζόντια
        # κύλιση σε πέντε themes — ελάττωμα που εμφανιζόταν μόνο με ελλιπή
        # στοιχεία, δηλαδή ακριβώς στον νέο πελάτη.
        sel = sel + ":not(:empty)" if not sel.endswith(")") else sel
        per_file[file].append(
            f"  /* {why} */\n"
            f"  {sel} {{ position: relative; }}\n"
            f"  {sel}{pseudo} {{\n"
            f"    content: ''; position: absolute; z-index: 0;\n"
            f"    {box}\n"
            f"    width: 100%; min-width: 44px; height: 100%; min-height: 44px;\n"
            f"  }}")

    total = 0
    for file, rules in sorted(per_file.items()):
        path = TPL / f"{file}.module.css"
        if not path.exists():
            blocked.append(f"δεν βρέθηκε {path.name}")
            continue
        css = io.open(path, encoding="utf-8").read()
        if MARK in css:
            # Ξαναγράφεται, δεν συσσωρεύεται: το εργαλείο πρέπει να τρέχει
            # ξανά μετά από κάθε νέα μέτρηση χωρίς να αφήνει παλιούς κανόνες.
            css = css[:css.index("\n\n/* " + MARK)].rstrip("\n") + "\n"
        block = (f"\n\n/* {MARK} — αόρατη επέκταση, μόνο σε κινητό.\n"
                 f"   Μετρήθηκε σε 390/360/320. Καμία αλλαγή σε τυπογραφία, χρώμα,\n"
                 f"   σύνθεση ή desktop: το ψευδο-στοιχείο δεν ζωγραφίζει και δεν\n"
                 f"   πιάνει χώρο στη ροή. */\n"
                 f"@media (max-width: {BREAK}px) {{\n" + "\n".join(rules) + "\n}\n")
        total += len(rules)
        print(f"  {'~' if not check else '='} {path.name:<26} {len(rules)} κανόνες")
        if not check:
            io.open(path, "w", encoding="utf-8").write(css.rstrip("\n") + block)

    print(f"\n  αρχεία {len(per_file)} · κανόνες {total}")
    print("  τεχνική: " + " · ".join(f"{k} {v}" for k, v in sorted(stats.items())))
    if skipped:
        print(f"\n  ΠΑΡΑΛΕΙΦΘΗΚΑΝ (πολύ γενικός selector): {len(skipped)}")
        for s in sorted(set(skipped))[:8]:
            print("   ", s)
    if blocked:
        print(f"\n  ΜΠΛΟΚΑΡΙΣΤΗΚΑΝ: {len(blocked)}")
        for s in blocked[:8]:
            print("   ", s)
    if check:
        print("\n(έλεγχος μόνο)")


if __name__ == "__main__":
    main()
