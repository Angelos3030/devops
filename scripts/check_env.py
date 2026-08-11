#!/usr/bin/env python3
"""
Έλεγχος περιβάλλοντος — τρέξ' το ΠΡΙΝ από οτιδήποτε άλλο σε νέο environment.

    VITRINA_ENV=dev python scripts/check_env.py

Απαντά σε τρία ερωτήματα:
  1. Συνδέομαι;
  2. Είμαι όντως εκεί που νομίζω — ή κοιτάω κατά λάθος την παραγωγή;
  3. Υπάρχουν όλα όσα χρειάζεται ο κώδικας (πίνακες, bucket);

Το (2) είναι ο λόγος που υπάρχει το αρχείο. Μια staging βάση που δείχνει στην
παραγωγή δεν είναι staging — είναι παραγωγή με άλλο όνομα.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import env  # noqa: E402

# Πίνακες που περιμένει ο κώδικας — αν λείπει κάποιος, τα migrations δεν έτρεξαν.
TABLES = ("clients", "site_content", "sites", "client_assets",
          "client_site_claims", "domains", "schema_migrations")
WITHDRAWN_TABLES = ("site_variants",)
BUCKET = "client-assets"

ok, bad = [], []


def check(good: bool, label: str, detail: str = "") -> None:
    (ok if good else bad).append(label)
    print(f"  {'✓' if good else '✗'} {label}{f'  — {detail}' if detail else ''}")


def main() -> int:
    print("=" * 62)
    print(env.banner())
    print("=" * 62)

    url, key = env.supabase(required=False)
    if not url or not key:
        print("\n⛔ Δεν υπάρχουν credentials για αυτό το περιβάλλον.")
        print(f"   Χρειάζεται SUPABASE_URL_{'PRODUCTION' if env.is_production else 'STAGING'} + KEY.")
        return 1

    # --- Απομόνωση: το staging ΔΕΝ πρέπει να δείχνει στο ίδιο project με την παραγωγή
    print("\n[απομόνωση]")
    prod_url = os.environ.get("SUPABASE_URL_PRODUCTION", "") or os.environ.get("SUPABASE_URL", "")
    if not env.is_production and prod_url:
        check(url.strip() != prod_url.strip(),
              "η βάση ΔΕΝ είναι η παραγωγή",
              "ΙΔΙΟ URL ΜΕ ΤΗΝ ΠΑΡΑΓΩΓΗ" if url.strip() == prod_url.strip() else "")
    else:
        check(True, "δεν υπάρχουν production credentials εδώ για να συγκριθούν")
    check(url.startswith("https://"), "HTTPS", url.split("//")[-1][:34])

    # --- Σύνδεση & σχήμα
    print("\n[σύνδεση & σχήμα]")
    try:
        from supabase import create_client
        sb = create_client(url, key)
    except Exception as e:  # noqa: BLE001
        check(False, "δημιουργία client", str(e)[:80])
        return 1

    for table in TABLES:
        try:
            sb.table(table).select("*").limit(1).execute()
            check(True, f"πίνακας {table}")
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            check(False, f"πίνακας {table}",
                  "δεν υπάρχει — τρέξε migrate.py" if "does not exist" in msg else msg[:70])

    if not env.is_production:
        for table in WITHDRAWN_TABLES:
            try:
                sb.table(table).select("*").limit(1).execute()
                check(False, f"ο αποσυρμένος πίνακας {table} απουσιάζει",
                      "υπάρχει ακόμη — το staging δεν είναι canonical")
            except Exception as e:  # noqa: BLE001
                msg = str(e).lower()
                missing = any(marker in msg for marker in (
                    "does not exist", "could not find", "schema cache", "pgrst205"))
                check(missing, f"ο αποσυρμένος πίνακας {table} απουσιάζει",
                      "απρόσμενο API σφάλμα" if not missing else "")

    # --- Storage
    print("\n[storage]")
    try:
        buckets = [b.name if hasattr(b, "name") else b.get("name") for b in sb.storage.list_buckets()]
        check(BUCKET in buckets, f"bucket «{BUCKET}»",
              f"βρέθηκαν: {', '.join(buckets) or 'κανένα'}" if BUCKET not in buckets else "")
    except Exception as e:  # noqa: BLE001
        check(False, "λίστα buckets", str(e)[:80])

    # --- Πλήθος δεδομένων: το staging πρέπει να είναι μικρό
    print("\n[δεδομένα]")
    try:
        rows = sb.table("clients").select("id", count="exact").limit(1).execute()
        n = rows.count if rows.count is not None else len(rows.data)
        if env.is_production:
            check(True, f"{n} πελάτες (παραγωγή)")
        else:
            check(n < 100, f"{n} πελάτες",
                  "ΠΟΛΛΟΙ για staging — μήπως δείχνει στην παραγωγή;" if n >= 100 else "")
    except Exception as e:  # noqa: BLE001
        check(False, "μέτρηση πελατών", str(e)[:70])

    print("\n" + "=" * 62)
    print(f"ΠΕΡΑΣΑΝ: {len(ok)}   ΕΣΠΑΣΑΝ: {len(bad)}")
    if bad:
        print("\n❌ " + "\n   ".join(bad))
        return 1
    print("\n✅ Το περιβάλλον είναι έτοιμο.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
