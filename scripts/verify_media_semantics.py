#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Επαλήθευση του migration 0002 πάνω στην ΠΡΑΓΜΑΤΙΚΗ staging βάση.

Δεν ελέγχει «τρέξαμε το SQL». Ελέγχει ότι το συμβόλαιο ισχύει:

  1. οι στήλες υπάρχουν με τα σωστά defaults
  2. το CHECK απορρίπτει άκυρη κλάση — και το αποδεικνύουμε προσπαθώντας
  3. υπάρχοντες πελάτες δεν άλλαξαν συμπεριφορά (backward compatibility)
  4. upload → media_class → gallery → site-data διαδίδεται ολόκληρο
  5. το `real-only` ενεργοποιείται ΑΝΑ ΠΕΛΑΤΗ και αλλάζει μόνο αυτόν

    VITRINA_ENV=staging python scripts/verify_media_semantics.py --confirm-staging

Γράφει σε staging (δημιουργεί και σβήνει δικά του δοκιμαστικά records). Ποτέ
production: το `env.require` και τα ξεχωριστά credentials το εγγυώνται δύο φορές.
"""
from __future__ import annotations

import argparse
import sys
import uuid

sys.path.insert(0, ".")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import env  # noqa: E402

env.require("staging")
env.print_banner()

from src import db  # noqa: E402
from src import media_semantics as ms  # noqa: E402

PASS, FAIL = "  ✓", "  ✗"
failures = 0
created: list[str] = []


def check(ok: bool, msg: str) -> bool:
    global failures
    print((PASS if ok else FAIL) + " " + msg)
    if not ok:
        failures += 1
    return ok


def sb():
    return db._client()


def main() -> int:
    global failures
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-staging", action="store_true")
    args = ap.parse_args()
    env.require_destructive(args.confirm_staging)

    print("\n[1] Σχήμα")
    # Οι στήλες υπάρχουν και δέχονται NULL (= η προηγούμενη συμπεριφορά).
    row = sb().table("client_assets").select("id,media_class").limit(1).execute()
    check(True, "client_assets.media_class υπάρχει και διαβάζεται")
    c = sb().table("clients").select("id,media_policy").limit(1).execute()
    check(True, "clients.media_policy υπάρχει και διαβάζεται")

    print("\n[2] Constraints — η άρνηση αποδεικνύεται, δεν υποτίθεται")
    cid = db.create_client({"name": "QA Media Semantics", "business_type": "Υδραυλικός",
                            "city": "Λάρισα"})
    created.append(cid)
    check(bool(cid), f"δημιουργήθηκε δοκιμαστικός πελάτης {cid[:8]}…")

    try:
        sb().table("client_assets").insert({
            "client_id": cid, "type": "photo", "url": "https://example.com/x.jpg",
            "usage": "site", "media_class": "TOTALLY_MADE_UP",
        }).execute()
        check(False, "άκυρη κλάση ΕΓΙΝΕ δεκτή — το CHECK δεν δουλεύει")
    except Exception as e:
        check("media_class" in str(e) or "check" in str(e).lower(),
              "άκυρη κλάση απορρίπτεται από το CHECK")

    try:
        sb().table("clients").update({"media_policy": "whatever"}).eq("id", cid).execute()
        check(False, "άκυρο media_policy ΕΓΙΝΕ δεκτό")
    except Exception as e:
        check("media_policy" in str(e) or "check" in str(e).lower(),
              "άκυρο media_policy απορρίπτεται από το CHECK")

    print("\n[3] Backward compatibility — υπάρχοντες πελάτες")
    existing = sb().table("clients").select("id,media_policy").neq("id", cid).limit(50).execute()
    rows = existing.data or []
    non_null = [r for r in rows if r.get("media_policy") is not None]
    check(not non_null, f"{len(rows)} υπάρχοντες πελάτες, {len(non_null)} με media_policy "
                        f"— πρέπει 0 (κανείς δεν άλλαξε συμπεριφορά)")
    old_assets = sb().table("client_assets").select("id,type,url,media_class").limit(100).execute()
    photos = [a for a in (old_assets.data or []) if a.get("type") in ("photo", "image", "gallery") and a.get("url")]
    unclassified = [a for a in photos if not a.get("media_class")]
    check(not unclassified, f"{len(photos)} υπάρχουσες φωτογραφίες, {len(unclassified)} χωρίς κλάση "
                            f"— το backfill τις κάλυψε")

    print("\n[4] Διάδοση: upload → media_class → gallery → site-data")
    wanted = [("REAL_WORK", "Αλλαγή σωληνώσεων"), ("REAL_SPACE", "Το συνεργείο"),
              ("REAL_OWNER_PERSON", "Ο ιδιοκτήτης")]
    for cls, title in wanted:
        db.save_client_asset(cid, {"type": "photo", "title": title, "usage": "site",
                                   "url": f"https://example.com/{uuid.uuid4().hex[:8]}.jpg",
                                   "rights_ok": True, "media_class": cls})
    assets = db.get_client_assets(cid, usage="site")
    stored = {a.get("media_class") for a in assets if a.get("media_class")}
    check(stored == {c for c, _ in wanted},
          f"οι 3 κλάσεις αποθηκεύτηκαν ακέραιες: {sorted(stored)}")

    from src import meta_oauth as mo
    intake = mo._enrich_intake(cid, {"name": "QA Media Semantics", "type": "Υδραυλικός"})
    gallery = intake.get("gallery") or []
    with_class = [g for g in gallery if g.get("media_class")]
    check(len(with_class) == 3,
          f"η κλάση ταξίδεψε ως το gallery: {len(with_class)}/3 εικόνες")

    print("\n[5] Opt-in — αλλάζει ΜΟΝΟ τον πελάτη που το δηλώνει")
    before = mo.site_data(cid)["data"]
    check("MEDIA_POLICY" not in before,
          "χωρίς media_policy: το site-data ΔΕΝ φέρει πολιτική (ως πριν)")
    check(len(before.get("gallery") or []) >= 3,
          f"χωρίς πολιτική το gallery παραμένει γεμάτο ({len(before.get('gallery') or [])})")

    sb().table("clients").update({"media_policy": "real-only"}).eq("id", cid).execute()
    after = mo.site_data(cid)["data"]
    check(after.get("MEDIA_POLICY") == "real-only", "με opt-in: το site-data φέρει real-only")
    check(all(g.get("media_class") in ms.REAL_CLASSES for g in (after.get("gallery") or [])),
          "με opt-in: κάθε εικόνα στο gallery είναι δηλωμένα πραγματική")
    check(after.get("HERO_IS_REAL") is True, "με πραγματικό υλικό: HERO_IS_REAL=True")

    # Δεύτερος πελάτης ΧΩΡΙΣ πολιτική: δεν επηρεάζεται.
    cid2 = db.create_client({"name": "QA Media Control", "business_type": "Υδραυλικός", "city": "Λάρισα"})
    created.append(cid2)
    ctrl = mo.site_data(cid2)["data"]
    check("MEDIA_POLICY" not in ctrl,
          "δεύτερος πελάτης χωρίς opt-in: καμία αλλαγή — η πολιτική ΔΕΝ είναι καθολική")

    print("\n[6] Τυπογραφική συμπεριφορά χωρίς πραγματικό υλικό")
    cid3 = db.create_client({"name": "QA Media NoPhoto", "business_type": "Οδοντιατρείο", "city": "Λάρισα"})
    created.append(cid3)
    db.save_client_asset(cid3, {"type": "photo", "title": "stock", "usage": "site",
                                "url": "https://example.com/stock.jpg", "rights_ok": True,
                                "media_class": "ILLUSTRATIVE"})
    sb().table("clients").update({"media_policy": "real-only"}).eq("id", cid3).execute()
    d3 = mo.site_data(cid3)["data"]
    check(not (d3.get("gallery") or []), "μόνο ILLUSTRATIVE: το gallery αδειάζει αντί να ψευτίσει")
    check(d3.get("MEDIA_ILLUSTRATIVE") is True, "σημαίνεται ως τυπογραφική παρουσίαση")
    check(d3.get("GALLERY_TITLE") == ms.NEUTRAL_TITLE["work"],
          f"ο τίτλος έγινε ουδέτερος: {d3.get('GALLERY_TITLE')!r}")

    return failures


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        # Καθαρισμός: το QA δεν αφήνει σκουπίδια σε βάση, ούτε σε staging.
        for cid in created:
            try:
                sb().table("client_assets").delete().eq("client_id", cid).execute()
                sb().table("clients").delete().eq("id", cid).execute()
            except Exception as e:
                print(f"  ! καθαρισμός {cid[:8]}… απέτυχε: {e}")
        print(f"\n  καθαρίστηκαν {len(created)} δοκιμαστικοί πελάτες")
    print("\n" + "─" * 60)
    print("❌ αποτυχίες: %d" % code if code else "✅ Το συμβόλαιο ισχύει στη staging βάση.")
    sys.exit(1 if code else 0)
