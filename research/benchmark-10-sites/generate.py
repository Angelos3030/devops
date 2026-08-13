# -*- coding: utf-8 -*-
"""Παράγει τα 10 sites μέσω του ΠΡΑΓΜΑΤΙΚΟΥ pipeline παραγωγής.

Η αλυσίδα αντιγράφει βήμα προς βήμα το `POST /start` → background build →
`GET /clients/{id}/site-data` του `src/meta_oauth.py`:

    qs.parse(prompt)                    # canonical funnel: ελεύθερο κείμενο
    → merge assets/services (όπως _enrich_intake από τη DB)
    → site_copy.enrich_with_copy()      # ΠΡΑΓΜΑΤΙΚΟ AI copy (Haiku), αν υπάρχει κλειδί
    → pg.recommend_templates()          # η επιλογή theme του προϊόντος, όχι δική μου
    → pg.normalize() + unescape         # ό,τι ακριβώς επιστρέφει το site-data endpoint

Το ΜΟΝΟ που αντικαθίσταται είναι η Supabase: γράφουμε το ίδιο JSON σε αρχείο αντί
να το διαβάσουμε από τη βάση. Καμία λογική παραγωγής δεν παρακάμπτεται.

ΠΡΩΤΗ ΓΕΝΙΑ ΜΕΤΡΑΕΙ: δεν ξανατρέχει, δεν διαλέγει, δεν ωραιοποιεί.
"""
from __future__ import annotations

import html as _html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src import premium_generator as pg  # noqa: E402
from src import quick_start as qs  # noqa: E402
from src import site_copy  # noqa: E402

# Ο φάκελος έχει παύλα, άρα δεν είναι importable package — φόρτωση με διαδρομή.
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("bench_businesses", Path(__file__).with_name("businesses.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BUSINESSES = _mod.BUSINESSES

OUT = ROOT / "sites" / "artifacts" / "benchmark"
OUT.mkdir(parents=True, exist_ok=True)


def _unesc(v):
    if isinstance(v, str):
        return _html.unescape(v)
    if isinstance(v, list):
        return [_unesc(x) for x in v]
    if isinstance(v, dict):
        return {k: _unesc(x) for k, x in v.items()}
    return v


def build(entry: dict) -> dict:
    bid, prompt, extra = entry["id"], entry["prompt"], entry["intake"]
    log: list[str] = []

    # 1. Canonical funnel: μόνο το ελεύθερο κείμενο, όπως στο /start.
    parsed = qs.parse(prompt)
    parsed_services = parsed.pop("services", [])
    log.append(f"parse → type={parsed.get('type')!r} city={parsed.get('city')!r} "
               f"name={parsed.get('name')!r} services={len(parsed_services)}")

    # 2. Ό,τι θα είχε συμπληρώσει/ανεβάσει ο πελάτης μετά το preview
    #    (ίδιο σχήμα με _enrich_intake: gallery[], services[{name,description}]).
    intake = {**parsed, **extra}
    intake["description"] = extra.get("description") or parsed.get("description") or prompt
    if not intake.get("services") and parsed_services:
        intake["services"] = parsed_services
        log.append("services: από τον parser (ο πελάτης δεν έδωσε δικές του)")

    # 3. ΠΡΑΓΜΑΤΙΚΟ AI copy — ό,τι τρέχει στην παραγωγή.
    from src import ai
    before = set(intake)
    intake = site_copy.enrich_with_copy(intake)
    added = sorted(set(intake) - before)
    log.append(f"copy: provider={ai.provider()} model={ai.model()} "
               f"available={ai.available()} πρόσθεσε={added or 'τίποτα'}")

    # 4. Επιλογή theme ΑΠΟ ΤΟ ΠΡΟΪΟΝ.
    ranked = pg.recommend_templates(intake)
    chosen = ranked[0]
    log.append(f"vertical={pg._vertical(intake)} ranked={ranked[:5]} → {chosen}")

    # 5. Ίδιο normalize + unescape με το site-data endpoint.
    ctx = pg.normalize(intake)
    data = {k: _unesc(v) for k, v in ctx.items() if not k.startswith("_")}

    payload = {"layout": chosen, "layouts": list(pg.LAYOUTS), "data": data}
    (OUT / f"{bid}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    return {
        "id": bid, "name": extra["name"], "vertical": pg._vertical(intake),
        "profession": pg._profession(intake), "theme": chosen, "ranked": ranked[:5],
        "palette": data.get("PALETTE") or "original",
        "given_photos": len(extra.get("gallery") or []),
        "services": len(data.get("services") or []),
        "log": log,
    }


def main() -> None:
    report = []
    for entry in BUSINESSES:
        try:
            r = build(entry)
        except Exception as e:  # ΚΑΤΑΓΡΑΦΕΤΑΙ, δεν κρύβεται
            r = {"id": entry["id"], "name": entry["intake"]["name"], "CRASH": repr(e)}
        report.append(r)
        print(json.dumps(r, ensure_ascii=False))
    (OUT / "generation-log.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(report)} sites → {OUT}")


if __name__ == "__main__":
    main()
