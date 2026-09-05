"""Οι τελικές πύλες, μετρημένες — όχι δηλωμένες.

Τρέχει πάνω στο ΠΑΓΩΜΕΝΟ σύνολο και ελέγχει τέσσερα πράγματα που το σκορ από
μόνο του δεν αποδεικνύει:

  1. ΕΠΑΝΑΛΗΨΙΜΟΤΗΤΑ  — ίδια είσοδος, ίδια απάντηση, τρεις φορές.
  2. ΣΥΜΦΩΝΙΑ         — η ετικέτα που βλέπει ο πελάτης και το vertical που
                         διάλεξε τα themes είναι το ΙΔΙΟ.
  3. ΑΝΕΞΑΡΤΗΣΙΑ ΑΠΟ AI — πόσες αποφάσεις εξαρτώνται ακόμη από το μοντέλο.
  4. ΑΚΕΡΑΙΟΤΗΤΑ      — το σύνολο δεν έχει πειραχθεί.

Χρήση:  python research/recommendation-audit/gates.py
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("VITRINA_ENV", "staging")
sys.path.insert(0, str(HERE.parents[1]))

from src import premium_generator as pg  # noqa: E402
from src import quick_start as qs           # noqa: E402

raw = (HERE / "dataset.json").read_bytes()
digest = hashlib.sha256(raw).hexdigest()
expected = (HERE / "dataset.sha256").read_text(encoding="utf-8").split()[0]
if digest != expected:
    sys.exit(f"ΑΚΥΡΟ: το σύνολο άλλαξε\n  {digest}\n  {expected}")
queries = json.loads(raw.decode("utf-8"))["queries"]
print(f"  ακεραιότητα συνόλου: ok ({len(queries)} ερωτήματα)")


def intake_of(q: dict) -> dict:
    # Ίδια κατασκευή με το measure.py — ό,τι βλέπει και η παραγωγή.
    text = q["text"]
    return {"name": qs._guess_name(text), "type": qs._guess_trade(text),
            "city": qs._guess_city(text), "description": text, "services": []}


# ── 1+2. Τρία περάσματα· ετικέτα και themes από την ΙΔΙΑ απόφαση ───────────
runs: list[list[tuple[str, tuple[str, ...]]]] = []
ai_needed: list[dict] = []
for pass_no in range(3):
    pg._AI_VERTICAL_CACHE.clear()          # καθαρή αφετηρία σε κάθε πέρασμα
    out = []
    for q in queries:
        intake = intake_of(q)
        vertical, label = pg.vertical_of(intake)
        themes = pg.recommend_templates(intake, limit=12, vertical=vertical)
        out.append((vertical, tuple(themes)))
        if pass_no == 0 and pg._decide(pg._signals(intake)) is None \
                and pg._decide(pg._signals(intake, fold=True)) is None:
            ai_needed.append({"id": q["id"], "text": q["text"],
                              "style": q["style"], "decided": vertical})
    runs.append(out)

drift = [queries[i]["id"] for i in range(len(queries))
         if not (runs[0][i] == runs[1][i] == runs[2][i])]
print(f"  επαναληψιμότητα: {len(queries) - len(drift)}/{len(queries)}"
      f"  {'ok' if not drift else 'ΑΠΟΚΛΙΣΗ ' + ', '.join(drift[:8])}")

# Συμφωνία: η ετικέτα προέρχεται από το ίδιο vertical που έδωσε τα themes.
disagree = []
for q in queries:
    intake = intake_of(q)
    vertical, label = pg.vertical_of(intake)
    if pg.VERTICAL_LABEL_EL.get(vertical, vertical) != label:
        disagree.append(q["id"])
print(f"  συμφωνία ετικέτας/κατάταξης: "
      f"{'ok' if not disagree else 'ΔΙΑΦΩΝΙΑ ' + ', '.join(disagree[:8])}")

# ── 3. Πόσο ακόμη εξαρτιόμαστε από το μοντέλο ─────────────────────────────
print(f"  αποφάσεις που φτάνουν στο AI: {len(ai_needed)}/{len(queries)}"
      f" ({100 * len(ai_needed) / len(queries):.1f}%)")
for r in ai_needed:
    print(f"      [{r['style']:<18}] {r['text'][:64]:<66}-> {r['decided']}")

(HERE / "gates.json").write_text(json.dumps({
    "dataset_sha256": digest,
    "queries": len(queries),
    "repeatability_drift": drift,
    "label_ranking_disagreement": disagree,
    "ai_dependent": ai_needed,
}, ensure_ascii=False, indent=2), encoding="utf-8")

sys.exit(1 if (drift or disagree) else 0)
