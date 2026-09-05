#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Διάγνωση αιτίων: πού αποφασίζεται το επάγγελμα και πόσο σταθερά. Read-only.

    python research/recommendation-audit/diagnose.py

Χωρίζει τα ερωτήματα σε δύο κόσμους:

  ΛΕΞΕΙΣ : τα σήματα-κλειδιά αποφάσισαν  -> ντετερμινιστικό
  AI     : δεν υπήρχε σήμα, μίλησε το μοντέλο -> ΜΗ ντετερμινιστικό

Το `_vertical` πέφτει σιωπηλά στο `_vertical_by_ai` όταν κανένα σήμα δεν φτάνει
το κατώφλι. Χωρίς αυτόν τον διαχωρισμό, «η ανίχνευση είναι 83%» κρύβει ότι ένα
κομμάτι της απαντιέται από μοντέλο και μπορεί να αλλάξει από εκτέλεση σε
εκτέλεση.
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("VITRINA_ENV", "staging")

from src import premium_generator as pg   # noqa: E402
from src import quick_start as qs         # noqa: E402


def intake_of(text: str) -> dict:
    return {"name": qs._guess_name(text), "type": qs._guess_trade(text),
            "city": qs._guess_city(text), "description": text, "services": []}


def decide(text: str) -> tuple[str, str, dict]:
    """(πηγή απόφασης, vertical, σήματα) — χωρίς να καλέσει AI δεύτερη φορά."""
    intake = intake_of(text)
    scores = pg._signals(intake)
    if scores:
        order = {v: i for i, (v, _) in enumerate(pg._VERTICAL_RULES)}
        best = max(scores.items(), key=lambda kv: (kv[1], -order[kv[0]]))
        if best[1] >= pg._MIN_SCORE:
            return "ΛΕΞΕΙΣ", best[0], scores
    return "AI", pg._vertical(intake), scores


def main() -> None:
    data = json.loads(io.open(HERE / "dataset.json", encoding="utf-8").read())
    rows = data["queries"]

    by_source = Counter()
    wrong_by_source = Counter()
    ai_rows = []
    weak_wins = []

    for q in rows:
        src, vert, scores = decide(q["text"])
        ok = vert in {q["expected_vertical"], *q.get("also_acceptable", [])}
        by_source[src] += 1
        if not ok:
            wrong_by_source[src] += 1
        if src == "AI":
            ai_rows.append({**q, "vertical": vert, "ok": ok})
        elif not ok:
            # Ποια λέξη κέρδισε λάθος;
            culprits = []
            norm = pg._normalize_text(q["text"])
            for v, words in pg._VERTICAL_RULES:
                if v != vert:
                    continue
                for w in words:
                    if w in norm:
                        culprits.append((w, "αδύναμο" if w in pg._WEAK_WORDS else "ΙΣΧΥΡΟ"))
            weak_wins.append({**q, "vertical": vert, "culprits": culprits[:3],
                              "scores": scores})

    print(f"  ΠΟΥ ΑΠΟΦΑΣΙΖΕΤΑΙ ΤΟ ΕΠΑΓΓΕΛΜΑ  ({len(rows)} ερωτήματα)\n")
    for src in ("ΛΕΞΕΙΣ", "AI"):
        n = by_source[src]
        bad = wrong_by_source[src]
        acc = 100 * (n - bad) / n if n else 0
        print(f"    {src:<8}{n:>4} ερωτήματα ({100*n/len(rows):.0f}%)   "
              f"ακρίβεια {acc:.1f}%   λάθη {bad}")
    print(f"\n  {by_source['AI']} ερωτήματα ({100*by_source['AI']/len(rows):.0f}%) "
          f"απαντώνται από ΜΟΝΤΕΛΟ — μη ντετερμινιστικά.")

    print(f"\n  ΣΤΥΛ ΠΟΥ ΠΕΦΤΟΥΝ ΣΤΟ AI")
    st = Counter(r["style"] for r in ai_rows)
    for s, n in st.most_common():
        print(f"    {s:<20}{n:>3}")

    print(f"\n  ΛΑΘΟΣ ΑΠΟ ΛΕΞΗ-ΚΛΕΙΔΙ ({len(weak_wins)})")
    print(f"    {'είσοδος':<46}{'βγήκε':<14}λέξη που κέρδισε")
    print("    " + "-" * 88)
    for r in weak_wins[:18]:
        cul = ", ".join(f"«{w}»({k})" for w, k in r["culprits"]) or "—"
        print(f"    {r['text'][:44]:<46}{r['vertical']:<14}{cul}")

    io.open(HERE / "diagnosis.json", "w", encoding="utf-8").write(json.dumps(
        {"by_source": dict(by_source), "wrong_by_source": dict(wrong_by_source),
         "ai_queries": ai_rows, "keyword_failures": weak_wins},
        ensure_ascii=False, indent=1))
    print(f"\n  -> {(HERE / 'diagnosis.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
