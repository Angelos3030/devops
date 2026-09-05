#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Μετράει τον αγωγό προτάσεων στο ΠΑΓΩΜΕΝΟ σύνολο. Τρέχει μετά από κάθε βήμα.

    python research/recommendation-audit/measure.py "όνομα βήματος"

Επαληθεύει πρώτα το checksum του `dataset.json`. Αν το σύνολο αλλάξει, η
μέτρηση σταματά: βελτίωση που προκύπτει από αλλαγή των προσδοκιών δεν είναι
βελτίωση.

Προσθέτει γραμμή στο `steps.json`, ώστε το πριν/μετά να μη γράφεται από μνήμη.
"""
from __future__ import annotations

import hashlib
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
from src import theme_compat as tc        # noqa: E402

FAMILY = {
    "food": "ΦΑΓΗΤΟ", "cafe": "ΦΑΓΗΤΟ", "bakery": "ΦΑΓΗΤΟ",
    "beauty": "ΟΜΟΡΦΙΑ", "aesthetics": "ΟΜΟΡΦΙΑ", "massage": "ΟΜΟΡΦΙΑ",
    "dentist": "ΥΓΕΙΑ", "doctor": "ΥΓΕΙΑ", "pharmacy": "ΥΓΕΙΑ",
    "trade": "ΤΕΧΝΙΚΑ", "wood": "ΤΕΧΝΙΚΑ", "garage": "ΤΕΧΝΙΚΑ",
    "professional": "ΓΡΑΦΕΙΟ", "realestate": "ΓΡΑΦΕΙΟ",
    "gym": "ΓΥΜΝΑΣΤΗΡΙΟ", "rooms": "ΦΙΛΟΞΕΝΙΑ",
    "retail": "ΛΙΑΝΙΚΗ", "pet": "ΚΑΤΟΙΚΙΔΙΑ", "farm": "ΠΑΡΑΓΩΓΗ",
}


def catalog() -> dict[str, dict]:
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
        out[key] = {"primary": p.group(1) if p else None,
                    "verticals": json.loads(v.group(1).replace("'", '"')) if v else [],
                    "generic": (g.group(1) == "true") if g else False,
                    "category": c.group(1) if c else ""}
    return out


CATALOG = catalog()


def intake_of(text: str) -> dict:
    return {"name": qs._guess_name(text), "type": qs._guess_trade(text),
            "city": qs._guess_city(text), "description": text, "services": []}


def judge(theme: str, vertical: str) -> tuple[int, bool]:
    meta = CATALOG.get(theme)
    if not meta:
        return 3, True
    if meta["primary"] == vertical:
        t = 0
    elif vertical in meta["verticals"]:
        t = 1
    elif meta["generic"]:
        t = 2
    else:
        t = 3
    fq, ft = FAMILY.get(vertical), FAMILY.get(meta["primary"])
    return t, bool(t == 3 and fq and ft and fq != ft)


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "χωρίς όνομα"

    raw = io.open(HERE / "dataset.json", "rb").read()
    frozen = io.open(HERE / "dataset.sha256").read().strip()
    if hashlib.sha256(raw).hexdigest() != frozen:
        raise SystemExit("✗ Το dataset.json ΑΛΛΑΞΕ. Το σύνολο είναι παγωμένο· "
                         "βελτίωση από αλλαγή προσδοκιών δεν μετράει.")

    rows = json.loads(raw.decode("utf-8"))["queries"]
    out = []
    for q in rows:
        intake = intake_of(q["text"])
        # Μία απόφαση ανά ερώτημα, όπως πρέπει να κάνει και το /designs.
        vertical, _ = pg.vertical_of(intake)
        themes = pg.recommend_templates(intake, limit=12, vertical=vertical)
        verdicts = [judge(t, vertical) for t in themes]
        expected = {q["expected_vertical"], *q.get("also_acceptable", [])}
        out.append({**q, "detected": vertical, "ok": vertical in expected,
                    "themes": themes, "tiers": [v[0] for v in verdicts],
                    "catastrophic": [t for t, v in zip(themes, verdicts) if v[1]]})

    def acc(sub):
        return round(100 * sum(r["ok"] for r in sub) / len(sub), 1) if sub else 0.0

    def rel(sub, n):
        g = sum(sum(1 for t in r["tiers"][:n] if t <= 1) for r in sub)
        c = sum(len(r["tiers"][:n]) for r in sub)
        return round(100 * g / c, 1) if c else 0.0

    GREEK = ("clean", "natural", "brand", "indirect", "location_noise")
    m = {
        "step": label,
        "queries": len(out),
        "vertical_accuracy": acc(out),
        "vertical_accuracy_unambiguous": acc([r for r in out if not r.get("also_acceptable")]),
        "top1_relevance": rel(out, 1),
        "top3_relevance": rel(out, 3),
        "top12_relevance": rel(out, 12),
        "catastrophic_rate": round(100 * sum(1 for r in out if r["catastrophic"]) / len(out), 2),
        "greek_accuracy": acc([r for r in out if r["style"] in GREEK]),
        "greeklish_accuracy": acc([r for r in out if r["style"].startswith("greeklish")]),
        "typo_accuracy": acc([r for r in out if r["style"] == "typos"]),
        "short_accuracy": acc([r for r in out if r["style"] == "short"]),
        "mixed_accuracy": acc([r for r in out if r["style"] == "mixed"]),
    }

    hist_path = HERE / "steps.json"
    hist = json.loads(io.open(hist_path, encoding="utf-8").read()) if hist_path.exists() else []
    hist.append(m)
    io.open(hist_path, "w", encoding="utf-8").write(json.dumps(hist, ensure_ascii=False, indent=1))
    io.open(HERE / "latest_rows.json", "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))

    prev = hist[-2] if len(hist) > 1 else None
    print(f"  ── {label} ──")
    for k in ("vertical_accuracy", "vertical_accuracy_unambiguous", "top1_relevance",
              "top3_relevance", "top12_relevance", "catastrophic_rate",
              "greek_accuracy", "greeklish_accuracy", "typo_accuracy",
              "short_accuracy", "mixed_accuracy"):
        d = ""
        if prev:
            diff = round(m[k] - prev[k], 2)
            if diff:
                d = f"   ({'+' if diff > 0 else ''}{diff})"
        print(f"    {k:<32}{m[k]:>7}{d}")

    wrong = Counter(f"{r['expected_vertical']}→{r['detected']}"
                    for r in out if not r["ok"])
    if wrong:
        print(f"\n    λάθη ({sum(wrong.values())}): "
              + ", ".join(f"{k}×{n}" for k, n in wrong.most_common(8)))


if __name__ == "__main__":
    main()
