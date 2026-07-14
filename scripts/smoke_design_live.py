"""LIVE smoke test for the design engine against real Supabase.

Creates a clearly-marked TEST client, generates + stores the 3 design variants,
exercises the approve flow, then DELETES the test client (cascade cleanup).

Prereqs:
  - SUPABASE_URL / SUPABASE_KEY set in .env  (service_role key ideally)
  - Migration applied: db/add_site_variants.sql

Run:  python -m scripts.smoke_design_live
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config as cfg  # noqa: E402

_passed = 0
_failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✓ {name}")
    else:
        _failed += 1
        print(f"  ✗ {name}  {('-> ' + detail) if detail else ''}")


def main() -> int:
    print("=" * 60)
    print("LIVE smoke test — Vitrina design engine + Supabase")
    print("=" * 60)

    if not (cfg.SUPABASE_URL and cfg.SUPABASE_KEY):
        print("\n⏭  SKIP: SUPABASE_URL/SUPABASE_KEY δεν έχουν οριστεί στο .env.")
        print("   Βάλε τα credentials και ξανατρέξε.")
        return 0

    from src import db
    from src import premium_generator as pg

    intake = {
        "name": "ZZ TEST — Ταβέρνα (auto-delete)",
        "type": "ταβέρνα", "city": "Θεσσαλονίκη", "phone": "2310000000",
        "email": "test@example.com",
    }

    cid = None
    try:
        # 1) create client
        cid = db.create_client(intake)
        check("create_client returns id", bool(cid), str(cid))

        # 2) generate + save 3 variants (same path as onboarding)
        recommended = pg.recommend_layout(intake)
        variants = pg.generate_variants(intake)
        for layout, html in variants.items():
            db.save_site_variant(cid, layout, html, recommended=(layout == recommended))
        stored = db.list_site_variants(cid)
        check(f"{len(variants)} variants stored in Supabase", len(stored) == len(variants), str(stored))
        check("exactly one recommended", sum(bool(v["recommended"]) for v in stored) == 1)

        # 3) fetch a preview back
        v = db.get_site_variant(cid, "studio")
        check("get_site_variant returns HTML", bool(v) and "<!DOCTYPE html>" in v["html"])

        # 4) approve flow
        db.set_selected_design(cid, "commerce")
        check("selected_layout persisted", db.get_selected_design(cid) == "commerce")
        sel = [x for x in db.list_site_variants(cid) if x["layout"] == "commerce"][0]
        check("selected variant status=selected", sel["status"] == "selected", str(sel))

    except Exception as e:
        msg = str(e)
        if "getaddrinfo" in msg or "Connection" in msg or "Max retries" in msg:
            print("\n⏭  SKIP: δεν υπάρχει δίκτυο προς Supabase από αυτό το περιβάλλον.")
            print("   Τρέξε το σε μηχάνημα με internet + valid SUPABASE_KEY (service_role).")
            return 0
        check("no exceptions", False, msg)
        if "site_variants" in msg or "selected_layout" in msg or "does not exist" in msg:
            print("\n   ⚠️  Μοιάζει να ΜΗΝ έχει τρέξει η migration.")
            print("      Τρέξε db/add_site_variants.sql στο Supabase SQL Editor.")
    finally:
        # 5) cleanup — delete test client (cascade removes variants)
        if cid:
            try:
                db.delete_client(cid)
                gone = db.list_site_variants(cid)
                check("cleanup: test client + variants deleted", gone == [], str(gone))
            except Exception as e:
                check("cleanup ran", False, str(e))

    print("\n" + "=" * 60)
    print(f"RESULT: {_passed} passed, {_failed} failed")
    print("=" * 60)
    return 1 if _failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
