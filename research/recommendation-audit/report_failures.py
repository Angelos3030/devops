#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Αναγνώσιμη αναφορά αποτυχιών από το `results.json`. Read-only.

    python research/recommendation-audit/report_failures.py

Γράφει `failures.md`. Για κάθε ύποπτο ερώτημα: τι γράφτηκε, τι ανιχνεύθηκε, τι
έπρεπε, τα 12 themes με την κατηγορία τους, και γιατί το αποτέλεσμα είναι
αμφισβητήσιμο.
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

GROUPS = {
    "ΚΟΜΜΩΤΗΡΙΟ / ΟΜΟΡΦΙΑ": ("beauty", "aesthetics", "massage"),
    "ΕΣΤΙΑΣΗ": ("food", "cafe", "bakery"),
    "ΥΓΕΙΑ": ("dentist", "doctor", "pharmacy"),
    "ΤΕΧΝΙΚΑ ΕΠΑΓΓΕΛΜΑΤΑ": ("trade", "wood", "garage"),
    "ΕΠΑΓΓΕΛΜΑΤΙΚΕΣ ΥΠΗΡΕΣΙΕΣ": ("professional", "realestate"),
}
TIER_NAME = {0: "ακριβές", 1: "συγγενικό", 2: "γενικό", 3: "ΑΣΧΕΤΟ"}


def why(r: dict) -> str:
    """Μια πρόταση: γιατί αυτό το αποτέλεσμα είναι αμφισβητήσιμο."""
    bits = []
    if not r["vertical_ok"]:
        bits.append(
            f"ανιχνεύθηκε **{r['detected_vertical']}** αντί για "
            f"**{r['expected_vertical']}** — όλες οι προτάσεις χτίζονται πάνω "
            f"σε λάθος επάγγελμα")
    if r["catastrophic"]:
        bits.append(f"προτείνονται themes άλλης οικογένειας: "
                    f"{', '.join(r['catastrophic'][:4])}")
    bad = [t for t, tier in zip(r["themes"][:3], r["tiers"][:3]) if tier >= 2]
    if bad and r["vertical_ok"]:
        bits.append(f"στο top-3 μπαίνουν μη ειδικά themes: {', '.join(bad)}")
    if not r["parsed_type"]:
        bits.append("ο ντετερμινιστικός parser δεν αναγνώρισε επάγγελμα "
                    "(`type` κενό) — το vertical βγήκε μόνο από την περιγραφή")
    return " · ".join(bits) or "—"


def block(r: dict) -> str:
    lines = [
        f"#### `{r['id']}` · {r['style']}",
        "",
        f"- **ΕΙΣΟΔΟΣ:** «{r['text']}»",
        f"- **ΑΝΙΧΝΕΥΘΗΚΕ:** `{r['detected_vertical']}`"
        f"{'' if r['vertical_ok'] else '  ✗'}",
        f"- **ΑΝΑΜΕΝΟΜΕΝΟ:** `{r['expected_vertical']}`"
        + (f" (δεκτό και: {', '.join(r['also_acceptable'])})"
           if r.get("also_acceptable") else ""),
        f"- **parser `type`:** {r['parsed_type'] or '—(κενό)'}",
        "",
        "| # | theme | κατηγορία | primary | βαθμίδα |",
        "|---|---|---|---|---|",
    ]
    for i, (t, tier, prim, cat) in enumerate(
            zip(r["themes"], r["tiers"], r["primaries"], r["categories"]), 1):
        flag = " ⚠" if t in r["catastrophic"] else ""
        lines.append(f"| {i} | `{t}`{flag} | {cat} | {prim} | {TIER_NAME[tier]} |")
    lines += ["", f"**ΓΙΑΤΙ ΕΙΝΑΙ ΑΜΦΙΣΒΗΤΗΣΙΜΟ:** {why(r)}", ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads(io.open(HERE / "results.json", encoding="utf-8").read())
    rows = data["rows"]
    suspect = [r for r in rows
               if not r["vertical_ok"] or r["catastrophic"]
               or any(t >= 2 for t in r["tiers"][:3])]

    # Χειρότερα: πρώτα όσα έχουν ΚΑΙ λάθος επάγγελμα ΚΑΙ καταστροφικά themes.
    def severity(r):
        return (not r["vertical_ok"]) * 2 + bool(r["catastrophic"]) * 3 + \
               sum(1 for t in r["tiers"][:3] if t >= 2)
    worst = sorted(suspect, key=severity, reverse=True)[:20]

    out = [
        "# Αποτυχίες και ύποπτα αποτελέσματα",
        "",
        f"Από **{len(rows)}** ερωτήματα, **{len(suspect)}** χρειάζονται ματιά.",
        "",
        "Βαθμίδες: **ακριβές** = το theme φτιάχτηκε γι' αυτό το επάγγελμα · "
        "**συγγενικό** = δηλωμένο στα `verticals` του · **γενικό** = "
        "`generic: true` · **ΑΣΧΕΤΟ** = τίποτα από τα δύο. ⚠ = άλλη οικογένεια.",
        "",
        "---",
        "",
        "## Τα 20 χειρότερα",
        "",
    ]
    for r in worst:
        out.append(block(r))

    out += ["---", "", "## Ανά ομάδα επαγγελμάτων", ""]
    for name, verts in GROUPS.items():
        grp = [r for r in rows if r["expected_vertical"] in verts]
        bad = [r for r in grp if not r["vertical_ok"] or r["catastrophic"]]
        acc = 100 * sum(r["vertical_ok"] for r in grp) / len(grp)
        out += [
            f"### {name}",
            "",
            f"{len(grp)} ερωτήματα · ανίχνευση **{acc:.1f}%** · "
            f"προβληματικά **{len(bad)}**",
            "",
        ]
        if not bad:
            out += ["Καμία αποτυχία.", ""]
            continue
        wrong = Counter(r["detected_vertical"] for r in bad if not r["vertical_ok"])
        if wrong:
            out += ["Πού πηγαίνει λάθος: "
                    + ", ".join(f"`{k}` ×{n}" for k, n in wrong.most_common()), ""]
        out += ["| είσοδος | ανιχνεύθηκε | έπρεπε | top-3 |", "|---|---|---|---|"]
        for r in bad[:14]:
            top3 = ", ".join(f"`{t}`" for t in r["themes"][:3])
            out.append(f"| «{r['text'][:52]}» | `{r['detected_vertical']}` | "
                       f"`{r['expected_vertical']}` | {top3} |")
        out.append("")

    path = HERE / "failures.md"
    io.open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"  ύποπτα: {len(suspect)}/{len(rows)}")
    print(f"  -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
