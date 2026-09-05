#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Τρέχει το σύνολο αξιολόγησης στον ΣΗΜΕΡΙΝΟ αγωγό προτάσεων. Read-only.

    python research/recommendation-audit/run_baseline.py

Γράφει `results.json` και `failures.md`. Δεν αλλάζει τίποτα στο προϊόν.

ΠΩΣ ΧΤΙΖΕΤΑΙ ΤΟ INTAKE. Ίδια διαδρομή με την παραγωγή, ντετερμινιστικά: το
`/start` καλεί `quick_start.parse`, που έχει AI αλλά ΚΑΙ ντετερμινιστικό
fallback (`_guess_trade` / `_guess_name` / `_guess_city`). Εδώ χρησιμοποιείται
μόνο το ντετερμινιστικό μέρος, ώστε το baseline να είναι αναπαραγώγιμο και να
μετράει τον ΑΓΩΓΟ ΚΑΤΑΤΑΞΗΣ, όχι τη διάθεση ενός μοντέλου.

ΤΙ ΣΗΜΑΙΝΕΙ «ΣΥΝΑΦΕΣ». Όχι «μπορεί να αποδώσει τα δεδομένα». Κρίνεται από τη
ΔΗΛΩΜΕΝΗ σχεδιαστική πρόθεση του καταλόγου (`sites/lib/templates/index.js`):

  0 ακριβές  : `primary` == το επάγγελμα
  1 συγγενικό: το επάγγελμα είναι στα δηλωμένα `verticals`
  2 γενικό   : `generic: true`
  3 άσχετο   : τίποτα από τα παραπάνω

Μετράμε ως ΣΥΝΑΦΕΣ μόνο τις βαθμίδες 0 και 1. Η βαθμίδα 2 είναι ακριβώς το
«τεχνικά συμβατό» που το brief απαγορεύει να περνά για συνάφεια.

ΓΙΑΤΙ Ο ΚΑΤΑΛΟΓΟΣ ΚΑΙ ΟΧΙ ΤΟ BACKEND. Το `theme_compat` παράγει το `primary`
μηχανικά — «όπου κατατάσσεται ψηλότερα» — οπότε βαθμολογούσαμε το σύστημα με
το ίδιο του το κλειδί απαντήσεων. Πρώτη μέτρηση με αυτό έβγαλε 75% καταστροφικά,
που ήταν παραδοχή δική μου, όχι εύρημα. Ο κατάλογος δηλώνει πρόθεση σχεδίασης
και είναι ανεξάρτητο τεκμήριο. Η βαθμίδα του backend κρατιέται δίπλα, ως
`backend_tiers`, ακριβώς για να φαίνεται πού διαφωνούν τα δύο.
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("VITRINA_ENV", "staging")

from src import premium_generator as pg          # noqa: E402
from src import quick_start as qs                # noqa: E402
from src import theme_compat as tc               # noqa: E402

# ── Ανεξάρτητες οικογένειες. Διασταύρωση ανάμεσά τους = καταστροφικό. ───────
FAMILY = {
    "food": "ΦΑΓΗΤΟ", "cafe": "ΦΑΓΗΤΟ", "bakery": "ΦΑΓΗΤΟ",
    "beauty": "ΟΜΟΡΦΙΑ", "aesthetics": "ΟΜΟΡΦΙΑ", "massage": "ΟΜΟΡΦΙΑ",
    "dentist": "ΥΓΕΙΑ", "doctor": "ΥΓΕΙΑ", "pharmacy": "ΥΓΕΙΑ",
    "trade": "ΤΕΧΝΙΚΑ", "wood": "ΤΕΧΝΙΚΑ", "garage": "ΤΕΧΝΙΚΑ",
    "professional": "ΓΡΑΦΕΙΟ", "realestate": "ΓΡΑΦΕΙΟ",
    "gym": "ΓΥΜΝΑΣΤΗΡΙΟ", "rooms": "ΦΙΛΟΞΕΝΙΑ",
    "retail": "ΛΙΑΝΙΚΗ", "pet": "ΚΑΤΟΙΚΙΔΙΑ", "farm": "ΠΑΡΑΓΩΓΗ",
}

COMPAT = tc.build(pg._TEMPLATES_BY_VERTICAL)

# ── Σχεδιαστική ταυτότητα, από τον ΚΑΤΑΛΟΓΟ ────────────────────────────────
# Το `primary` του `theme_compat` παράγεται ΜΗΧΑΝΙΚΑ («όπου κατατάσσεται
# ψηλότερα στο backend»), οπότε ένα theme σε έξι verticals παίρνει σχεδόν
# αυθαίρετο primary. Κρίνοντας μ' αυτό, το `cinematic` έβγαινε «καταστροφικό»
# σε κομμωτήριο επειδή τυχαίνει να κατατάσσεται πρώτο στο φαγητό — και το
# ποσοστό εκτοξευόταν στο 75%, δηλαδή μετρούσε τη δική μου παραδοχή.
#
# Το `sites/lib/templates/index.js` δηλώνει ΣΧΕΔΙΑΣΤΙΚΗ πρόθεση: `primary`,
# `verticals[]`, `generic`, `category`. Αυτό είναι το τεκμήριο που ζητά το
# brief («theme metadata, catalog categories, intended verticals»).
def _catalog() -> dict[str, dict]:
    import re
    idx = io.open(ROOT / "sites" / "lib" / "templates" / "index.js",
                  encoding="utf-8").read()
    out: dict[str, dict] = {}
    for m in re.finditer(r"^\s*'?([a-z0-9-]+)'?:\s*\{([^\n]*)\},?\s*$", idx, re.M):
        key, body = m.group(1), m.group(2)
        if "primary:" not in body:
            continue
        p = re.search(r"primary: '([a-z]+)'", body)
        v = re.search(r"verticals: (\[[^\]]*\])", body)
        g = re.search(r"generic: (true|false)", body)
        c = re.search(r"category: '([^']*)'", body)
        out[key] = {
            "primary": p.group(1) if p else None,
            "verticals": json.loads(v.group(1).replace("'", '"')) if v else [],
            "generic": (g.group(1) == "true") if g else False,
            "category": c.group(1) if c else "",
        }
    return out


CATALOG = _catalog()


def intake_of(text: str) -> dict:
    """Ό,τι φτιάχνει το /start χωρίς AI — ίδια πεδία, ίδια βάρη."""
    return {
        "name": qs._guess_name(text),
        "type": qs._guess_trade(text),
        "city": qs._guess_city(text),
        "description": text,
        "services": [],
    }


def judge(theme: str, vertical: str) -> dict:
    """Συνάφεια με βάση τη ΔΗΛΩΜΕΝΗ σχεδιαστική πρόθεση του καταλόγου.

      0 ακριβές      : το theme φτιάχτηκε γι' αυτό το επάγγελμα
      1 συγγενικό    : το επάγγελμα είναι στα δηλωμένα `verticals` του
      2 γενικό       : `generic: true` — ταιριάζει παντού, ανήκει πουθενά
      3 άσχετο       : τίποτα από τα παραπάνω

    Καταστροφικό = ούτε γενικό, ούτε δηλωμένο για το επάγγελμα, ΚΑΙ ανήκει σε
    άλλη οικογένεια. Αυτό είναι το «κομμωτήριο παίρνει theme εστιατορίου».
    """
    meta = CATALOG.get(theme)
    if not meta:
        return {"tier": 3, "primary": "?", "category": "?", "catastrophic": True,
                "backend_tier": 3}
    entry = COMPAT.get(theme)
    backend_tier = tc.tier(entry, vertical) if entry else 3

    if meta["primary"] == vertical:
        t = 0
    elif vertical in meta["verticals"]:
        t = 1
    elif meta["generic"]:
        t = 2
    else:
        t = 3

    fam_q, fam_t = FAMILY.get(vertical), FAMILY.get(meta["primary"])
    catastrophic = bool(t == 3 and fam_q and fam_t and fam_q != fam_t)
    return {"tier": t, "primary": meta["primary"], "category": meta["category"],
            "catastrophic": catastrophic, "backend_tier": backend_tier}


def main() -> None:
    data = json.loads(io.open(HERE / "dataset.json", encoding="utf-8").read())
    queries = data["queries"]
    rows = []

    for q in queries:
        intake = intake_of(q["text"])
        detected = pg._vertical(intake)
        themes = pg.recommend_templates(intake, limit=12)
        verdicts = [judge(t, detected) for t in themes]

        expected = {q["expected_vertical"], *q.get("also_acceptable", [])}
        rows.append({
            **q,
            "detected_vertical": detected,
            "vertical_ok": detected in expected,
            "parsed_type": intake["type"],
            "themes": themes,
            "tiers": [v["tier"] for v in verdicts],
            "primaries": [v["primary"] for v in verdicts],
            "categories": [v["category"] for v in verdicts],
            "backend_tiers": [v["backend_tier"] for v in verdicts],
            "catastrophic": [t for t, v in zip(themes, verdicts) if v["catastrophic"]],
        })

    # ── Μετρικές ────────────────────────────────────────────────────────────
    def rel(row, n):
        """Πόσα από τα πρώτα n είναι ΣΥΝΑΦΗ (βαθμίδα 0 ή 1)."""
        head = row["tiers"][:n]
        return sum(1 for t in head if t <= 1), len(head)

    total = len(rows)
    vert_ok = sum(r["vertical_ok"] for r in rows)

    # «Προφανή» = ό,τι δεν είναι διφορούμενο. Ο στόχος 98% αφορά αυτά.
    obvious = [r for r in rows if not r.get("also_acceptable")]
    obvious_ok = sum(r["vertical_ok"] for r in obvious)

    metrics = {
        "queries": total,
        "verticals_tested": sorted({r["expected_vertical"] for r in rows}),
        "vertical_accuracy": round(100 * vert_ok / total, 1),
        "vertical_accuracy_unambiguous": round(100 * obvious_ok / len(obvious), 1),
    }
    for n in (1, 3, 5, 12):
        got = sum(rel(r, n)[0] for r in rows)
        cap = sum(rel(r, n)[1] for r in rows)
        metrics[f"top{n}_relevance"] = round(100 * got / cap, 1) if cap else 0.0
        # Πλήρως καθαρά: ΟΛΑ τα πρώτα n συναφή.
        clean = sum(1 for r in rows if rel(r, n)[0] == rel(r, n)[1] and rel(r, n)[1])
        metrics[f"top{n}_all_relevant_rate"] = round(100 * clean / total, 1)

    all_slots = sum(len(r["tiers"]) for r in rows)
    metrics["irrelevant_rate"] = round(
        100 * sum(sum(1 for t in r["tiers"] if t == 3) for r in rows) / all_slots, 2)
    metrics["generic_share_top3"] = round(
        100 * sum(sum(1 for t in r["tiers"][:3] if t == 2) for r in rows)
        / sum(len(r["tiers"][:3]) for r in rows), 1)
    metrics["catastrophic_rate"] = round(
        100 * sum(1 for r in rows if r["catastrophic"]) / total, 2)
    metrics["catastrophic_top3_rate"] = round(
        100 * sum(1 for r in rows if any(t in r["catastrophic"] for t in r["themes"][:3]))
        / total, 2)

    # Ποικιλία: πόσα διαφορετικά #1 δίνει το σύστημα συνολικά.
    metrics["distinct_top1"] = len({r["themes"][0] for r in rows if r["themes"]})
    metrics["distinct_themes_used"] = len({t for r in rows for t in r["themes"]})
    dupes = sum(1 for r in rows if len(set(r["themes"])) != len(r["themes"]))
    metrics["rows_with_duplicate_themes"] = dupes

    # Ανά μορφή εισόδου — εδώ φαίνεται η υποβάθμιση.
    by_style = {}
    for style in sorted({r["style"] for r in rows}):
        sub = [r for r in rows if r["style"] == style]
        by_style[style] = {
            "n": len(sub),
            "vertical_accuracy": round(100 * sum(x["vertical_ok"] for x in sub) / len(sub), 1),
            "top3_relevance": round(
                100 * sum(rel(x, 3)[0] for x in sub) / sum(rel(x, 3)[1] for x in sub), 1),
            "catastrophic_rate": round(
                100 * sum(1 for x in sub if x["catastrophic"]) / len(sub), 1),
        }

    by_vertical = {}
    for v in sorted({r["expected_vertical"] for r in rows}):
        sub = [r for r in rows if r["expected_vertical"] == v]
        by_vertical[v] = {
            "n": len(sub),
            "vertical_accuracy": round(100 * sum(x["vertical_ok"] for x in sub) / len(sub), 1),
            "top3_relevance": round(
                100 * sum(rel(x, 3)[0] for x in sub) / sum(rel(x, 3)[1] for x in sub), 1),
            "catastrophic": sum(1 for x in sub if x["catastrophic"]),
            "misdetected_as": dict(Counter(
                x["detected_vertical"] for x in sub if not x["vertical_ok"])),
        }

    # Επηρεάζει η τοποθεσία το επάγγελμα;
    pairs = defaultdict(dict)
    for r in rows:
        if r["style"] in ("clean", "location_noise"):
            pairs[r["business"]][r["style"]] = r["detected_vertical"]
    moved = [b for b, d in pairs.items()
             if len(d) == 2 and d["clean"] != d["location_noise"]]
    metrics["location_changed_vertical"] = len(moved)
    metrics["location_changed_examples"] = moved[:8]

    out = {"metrics": metrics, "by_style": by_style, "by_vertical": by_vertical,
           "rows": rows}
    io.open(HERE / "results.json", "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))

    # ── Έξοδος ──────────────────────────────────────────────────────────────
    m = metrics
    print(f"  ερωτήματα: {m['queries']}  ·  verticals: {len(m['verticals_tested'])}")
    print(f"\n  ΑΝΙΧΝΕΥΣΗ ΕΠΑΓΓΕΛΜΑΤΟΣ   {m['vertical_accuracy']}%"
          f"   (χωρίς διφορούμενα: {m['vertical_accuracy_unambiguous']}%)")
    print(f"\n  ΣΥΝΑΦΕΙΑ (βαθμίδα 0-1, το «γενικό» ΔΕΝ μετράει)")
    for n in (1, 3, 5, 12):
        print(f"    top-{n:<3} {m[f'top{n}_relevance']:>6}%   "
              f"πλήρως καθαρά: {m[f'top{n}_all_relevant_rate']}%")
    print(f"\n  άσχετα (βαθμίδα 3)          {m['irrelevant_rate']}%")
    print(f"  γενικού σκοπού στο top-3    {m['generic_share_top3']}%")
    print(f"  ΚΑΤΑΣΤΡΟΦΙΚΑ (οπουδήποτε)   {m['catastrophic_rate']}%")
    print(f"  ΚΑΤΑΣΤΡΟΦΙΚΑ στο top-3      {m['catastrophic_top3_rate']}%")
    print(f"\n  ποικιλία: {m['distinct_top1']} διαφορετικά #1 · "
          f"{m['distinct_themes_used']} themes σε χρήση · "
          f"διπλότυπα σε σειρά: {m['rows_with_duplicate_themes']}")
    print(f"  η τοποθεσία άλλαξε το επάγγελμα σε {m['location_changed_vertical']} επιχειρήσεις")

    print(f"\n  {'μορφή εισόδου':<20}{'n':>4}{'επάγγελμα':>11}{'top-3':>8}{'καταστρ.':>10}")
    print("  " + "-" * 55)
    for s, d in sorted(by_style.items(), key=lambda kv: kv[1]["vertical_accuracy"]):
        print(f"  {s:<20}{d['n']:>4}{d['vertical_accuracy']:>10}%{d['top3_relevance']:>7}%"
              f"{d['catastrophic_rate']:>9}%")

    print(f"\n  {'επάγγελμα':<15}{'n':>4}{'ανίχνευση':>11}{'top-3':>8}{'καταστρ.':>9}  λάθος ως")
    print("  " + "-" * 72)
    for v, d in sorted(by_vertical.items(), key=lambda kv: kv[1]["vertical_accuracy"]):
        wrong = ", ".join(f"{k}×{n}" for k, n in sorted(
            d["misdetected_as"].items(), key=lambda kv: -kv[1])[:3])
        print(f"  {v:<15}{d['n']:>4}{d['vertical_accuracy']:>10}%{d['top3_relevance']:>7}%"
              f"{d['catastrophic']:>8}   {wrong}")
    print(f"\n  -> {(HERE / 'results.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
