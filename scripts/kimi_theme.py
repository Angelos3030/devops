#!/usr/bin/env python3
"""ORIGINAL_VITRINA_THEME_BENCHMARK — ένα πρωτότυπο theme από το Kimi.

    python scripts/kimi_theme.py --component AegisDental --key aegis-dental \
        --vertical dentist --model kimi-k2.7-code

Δεν είναι port. Δεν υπάρχει πηγαίο template. Το ερώτημα του πειράματος είναι
αν ένα μοντέλο μπορεί να ΣΧΕΔΙΑΣΕΙ πρωτότυπο master theme αντί να ψάχνουμε
templates τρίτων με τα προβλήματα άδειας και προέλευσης που φέρνουν.

Ό,τι προστατεύει τον port worker ισχύει αυτούσιο εδώ: ίδιο συμβόλαιο δεδομένων,
ίδιοι έλεγχοι διαδρομής/μεγέθους, ίδια απαγόρευση `use client` και `!important`,
ίδια σημασιολογική αντιστοίχιση demo. Αλλάζει μόνο η πηγή της ιδέας.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.port_worker import (  # noqa: E402
    ALLOWED_PREFIXES, MAX_FILE_BYTES, _register, demo_for,
)
from src.port_guards import run_all, summarize  # noqa: E402
from src.vitrina_contract import (  # noqa: E402
    as_prompt, availability, availability_prompt, extract,
)

BASE_URL = "https://api.moonshot.ai/v1"
OUT = ROOT / "research" / "kimi-benchmark"


def _load_key() -> str:
    """Το κλειδί ζει ΜΟΝΟ στο .env — ποτέ σε argument, log ή commit."""
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^KIMI_API_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("⛔ Λείπει το KIMI_API_KEY από το .env")


SYSTEM = """You are a senior product designer AND front-end engineer.

You are NOT porting an existing template. You are DESIGNING an original premium
website from first principles, then implementing it.

Originality is the point: do not reproduce a known template layout. Make
deliberate typographic, spatial and colour decisions and commit to them.

TRUTH CONTRACT — absolute. You MUST NOT invent: testimonials, reviews, ratings,
star counts, years of experience, patient/customer numbers, awards,
certifications, prices, discounts, guarantees, partner logos, team members,
statistics, credentials, before/after results. If a section would need such
data, DO NOT BUILD IT. Omitting is correct; inventing is a contract violation.

Return ONLY a JSON object:
{"files": [{"path": "...", "content": "..."}],
 "design_rationale": "...", "interactions": ["..."], "deviations": [{"what":"","why":""}]}"""


def brief(component: str, contract: dict, biz: str) -> str:
    schema_arrays = {k: v.get("item_keys", [])
                     for k, v in contract["fields"].items() if v["type"] == "array"}
    return f"""{as_prompt(contract, component)}

{availability_prompt(availability(biz), schema_arrays)}

=== ΤΙ ΣΧΕΔΙΑΖΕΙΣ ===

Ένα premium site για ΕΛΛΗΝΙΚΟ ΟΔΟΝΤΙΑΤΡΕΙΟ. Κοινό: ασθενείς που διαλέγουν
οδοντίατρο για την οικογένειά τους. Ο στόχος είναι εμπιστοσύνη και ηρεμία —
όχι «κλινική ψυχρότητα» και όχι φθηνή διαφημιστική εντύπωση.

Πρώτο viewport: όνομα ιατρείου, τι κάνει, πού βρίσκεται, ΜΙΑ καθαρή ενέργεια.

=== ΑΡΧΙΤΕΚΤΟΝΙΚΟΣ ΠΕΡΙΟΡΙΣΜΟΣ (ΜΗ ΔΙΑΠΡΑΓΜΑΤΕΥΣΙΜΟΣ) ===

React SERVER component. ΑΠΑΓΟΡΕΥΟΝΤΑΙ: 'use client', hooks, onClick, useState,
useEffect, εξωτερικές βιβλιοθήκες, <script>. ΜΗΔΕΝ JavaScript.

Αυτό ΔΕΝ σημαίνει στατική σελίδα. Όλα τα παρακάτω γίνονται με καθαρό CSS και
είναι ΚΑΛΥΤΕΡΑ από τις αντίστοιχες υλοποιήσεις με JS:

  slider      → `scroll-snap-type: x mandatory` σε container με `overflow-x: auto`.
                Δίνει ΦΥΣΙΚΟ swipe με momentum στο κινητό, κύλιση με πληκτρολόγιο
                όταν εστιάζεται, μηδέν layout shift, μηδέν JS. Άφησε το επόμενο
                slide να «ξεμυτίζει» σκόπιμα (partial next slide).
  reveal       → `animation-timeline: view()` με `animation-range`. Καθαρά CSS
                scroll-driven animations.
  mobile menu  → <details>/<summary>. Ανοίγει και κλείνει χωρίς JS.
  sticky header→ `position: sticky`.
  hover/focus  → `:hover`, `:focus-visible`, `transition`.

ΥΠΟΧΡΕΩΤΙΚΟ: `@media (prefers-reduced-motion: reduce)` που μηδενίζει animations
και scroll-behavior. Χωρίς αυτό η δουλειά απορρίπτεται.

=== ΚΙΝΗΣΗ — ΠΟΙΟΤΗΤΑ, ΟΧΙ ΠΟΣΟΤΗΤΑ ===

Διακριτική, ομαλή, σκόπιμη. ΟΧΙ: κίνηση σε κάθε στοιχείο, αναπηδήσεις,
scroll hijacking, υπερβολικό parallax, animations που καθυστερούν χρήσιμο
περιεχόμενο ή βλάπτουν την αναγνωσιμότητα. Καμία κίνηση δεν επιτρέπεται να
προκαλέσει layout shift ή υπερχείλιση.

=== ΤΡΕΙΣ ΣΚΟΠΙΜΕΣ ΣΥΝΘΕΣΕΙΣ ===

1440 · 768 · 390. Το 390 ΔΕΝ είναι σμίκρυνση του desktop: ανασυνθέτεις το hero,
κρατάς την τυπογραφία δυνατή, μετασχηματίζεις την πλοήγηση, διαλέγεις άλλα crop,
κάνεις τον slider touch-first, τα CTA φιλικά στον αντίχειρα (≥44px), και
αφαιρείς διακοσμητικά που εμποδίζουν. Το mobile πρέπει να αντέχει να δειχτεί
ΜΟΝΟ ΤΟΥ σε πελάτη.

=== ΧΡΩΜΑ ===

Οι ένδεκα ρόλοι --vt-* δηλώνονται ΜΙΑ φορά στο `.root` και χρησιμοποιούνται
παντού. Κανένα hex εκτός του `.root`. ΠΟΤΕ `!important`.
Ζεύγη που πρέπει να περνούν 4.5:1 — ink/surface, ink-soft/surface,
ink/surface-2, ink-soft/surface-2, on-accent/accent, accent-ink/surface,
accent-ink/surface-2, on-deep/surface-deep, accent-on-deep/surface-deep.

=== ΚΟΙΝΑ COMPONENTS ===

Χρησιμοποίησέ τα, μην τα ξαναγράψεις. Το prop `dark` του FindUs και του Brand
επιλέγει σκούρα παλέτα: πρέπει να ΤΑΙΡΙΑΖΕΙ με την επιφάνεια όπου το βάζεις.
Σκούρα ενότητα → με `dark`. Φωτεινή ενότητα → χωρίς αυτό.

=== SLIDER ===

Μόνο αν τα ΠΡΑΓΜΑΤΙΚΑ δεδομένα το στηρίζουν. Το `d.gallery` έχει 6 αληθινά
στοιχεία με image/title/sub — αυτό είναι επαρκής βάση. ΜΗΝ φτιάξεις ψεύτικα
slides για να υπάρχει carousel."""


def ask(key: str, model: str, system: str, user: str, max_tokens: int) -> tuple[str, dict]:
    payload = json.dumps({
        # temperature=1 ΥΠΟΧΡΕΩΤΙΚΑ: το kimi-k2.7-code απορρίπτει οτιδήποτε άλλο
        # με «invalid temperature: only 1 is allowed for this model».
        "model": model, "temperature": 1, "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                data = json.load(r)
            return data["choices"][0]["message"]["content"], data.get("usage", {})
        except urllib.error.HTTPError as exc:
            # ΤΟ ΣΩΜΑ, όχι μόνο ο κωδικός. Ένα σκέτο «HTTP 400» έκρυψε επί τρία
            # λεπτά ότι το μοντέλο απαιτεί temperature=1.
            body = exc.read().decode("utf-8", "replace")[:300]
            last = f"HTTP {exc.code}: {body}"
            if exc.code < 500:
                raise SystemExit(f"⛔ Το Kimi απέρριψε το αίτημα — {last}")
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, KeyError) as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise SystemExit(f"⛔ Το Kimi δεν απάντησε: {str(last)[:200]}")


def validate(files: list[dict], component: str) -> list[dict]:
    """Ίδιοι έλεγχοι με τον port worker. Η πηγή της ιδέας δεν αλλάζει τα όρια."""
    clean = []
    for f in files:
        norm = f.get("path", "").replace("\\", "/").lstrip("./")
        content = f.get("content", "")
        if not any(norm.startswith(p) for p in ALLOWED_PREFIXES):
            raise SystemExit(f"⛔ Διαδρομή εκτός allowlist: {norm}")
        resolved = (ROOT / norm).resolve()
        if not str(resolved).startswith(str(ROOT.resolve())):
            raise SystemExit(f"⛔ Διαδρομή δραπετεύει από το repo: {norm}")
        if resolved.exists() and component not in resolved.name:
            raise SystemExit(f"⛔ Απόπειρα αλλαγής ξένου αρχείου: {norm}")
        if len(content.encode("utf-8")) > MAX_FILE_BYTES:
            raise SystemExit(f"⛔ {norm}: υπερβαίνει το όριο μεγέθους")
        for banned, why in (("'use client'", "server component"),
                            ('"use client"', "server component"),
                            ("!important", "σπάει το colour spine")):
            if banned in content:
                raise SystemExit(f"⛔ {norm}: {banned} — {why}")
        clean.append({"path": norm, "content": content})
    return clean


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--component", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--vertical", required=True)
    ap.add_argument("--model", default="kimi-k2.7-code")
    ap.add_argument("--label", default="")
    ap.add_argument("--desc", default="")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    key = _load_key()
    contract = extract()
    biz = demo_for({"verticals": [args.vertical]})   # fail-closed + σημασιολογικός
    print(f"vertical={args.vertical} → demo={biz} · model={args.model}")

    base = brief(args.component, contract, biz)
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0}
    files: list[dict] = []
    payload: dict = {}

    for step, keep, extra in (
        ("JSX", ".jsx", f"Επίστρεψε ΜΟΝΟ το sites/lib/templates/{args.component}.jsx. "
                        "Σημασιολογικό HTML, ένα h1, class names μέσω του `s` import."),
        ("CSS", ".css", f"Επίστρεψε ΜΟΝΟ το sites/lib/templates/{args.component}.module.css. "
                        "Στιλίζει ΑΚΡΙΒΩΣ τα class names του JSX που ακολουθεί."),
    ):
        prompt = base + f"\n\n=== ΒΗΜΑ: {step} ===\n{extra}"
        if step == "CSS":
            prompt += "\n\n=== ΤΟ JSX ΠΟΥ ΜΟΛΙΣ ΕΓΡΑΨΕΣ ===\n" + files[0]["content"]
        raw, usage = ask(key, args.model, SYSTEM, prompt, 32000)
        (OUT / f"kimi-{step}.json").write_text(raw, encoding="utf-8")
        for k in usage_total:
            usage_total[k] += usage.get(k, 0)
        data = json.loads(raw)
        got = [f for f in data.get("files", []) if f.get("path", "").endswith(keep)]
        if not got:
            raise SystemExit(f"⛔ Το βήμα {step} δεν επέστρεψε αρχείο {keep}")
        files = validate(got, args.component) + [f for f in files
                                                 if not f["path"].endswith(keep)]
        payload.setdefault("design_rationale", data.get("design_rationale", ""))
        payload.setdefault("interactions", []).extend(data.get("interactions", []))
        payload.setdefault("deviations", []).extend(data.get("deviations", []))
        print(f"  {step}: {len(got[0]['content'])} χαρακτήρες")

    guards = run_all(files, contract, "", (), availability(biz))
    payload["guards"] = guards
    if any(guards.values()):
        print("⛔ guards:", summarize(guards)[:400])

    for f in files:
        p = ROOT / f["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f["content"], encoding="utf-8")
        print("  γράφτηκε", f["path"])

    payload["registered"] = _register({
        "theme_key": args.key, "component": args.component,
        "verticals": [args.vertical],
        "label": args.label or args.component,
        "desc": args.desc or "Πρωτότυπο master theme — benchmark Kimi.",
    })
    payload["usage"] = usage_total
    payload["model"] = args.model
    payload["demo_business"] = biz
    (OUT / "result.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
    print(json.dumps({"guards": guards, "usage": usage_total,
                      "registered": payload["registered"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
