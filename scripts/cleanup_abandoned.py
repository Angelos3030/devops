#!/usr/bin/env python3
"""
Καθαρισμός εγκαταλελειμμένων πελατών πριν την πληρωμή.

    python scripts/cleanup_abandoned.py                # ΜΟΝΟ αναφορά (dry-run)
    python scripts/cleanup_abandoned.py --delete       # πραγματική διαγραφή
    python scripts/cleanup_abandoned.py --days 45      # άλλο όριο

Γιατί υπάρχει: η ροή «site first» (`POST /start`) δημιουργεί εγγραφή πελάτη με
την πρώτη πρόταση, ΠΡΙΝ από λογαριασμό ή πληρωμή. Οι περισσότεροι επισκέπτες
δεν θα προχωρήσουν ποτέ. Χωρίς λήξη, η βάση γεμίζει με μισοτελειωμένα sites και
προσωπικά δεδομένα που δεν έχουμε λόγο να κρατάμε (GDPR: αποθήκευση μόνο όσο
χρειάζεται).

Είναι ΣΚΟΠΙΜΑ dry-run by default. Η διαγραφή θέλει ρητό --delete.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import db, env  # noqa: E402

# Μετά από τόσες μέρες χωρίς πληρωμή, μια εγγραφή θεωρείται εγκαταλελειμμένη.
DEFAULT_DAYS = 30

# Καταστάσεις που ΔΕΝ αγγίζονται ποτέ — ό,τι δείχνει αληθινή σχέση.
PROTECTED_STATUS = {"active", "paying", "cancelled", "past_due", "internal", "paused"}


def _is_abandoned(row: dict, cutoff: datetime) -> tuple[bool, str]:
    """Τέσσερα φίλτρα, ΟΛΑ πρέπει να ισχύουν. Σε αμφιβολία, κρατάμε."""
    status = (row.get("status") or "").lower()
    if status in PROTECTED_STATUS:
        return False, f"status={status}"
    # Email = πέρασε από ταμείο ή onboarding form. Πιθανός αληθινός άνθρωπος.
    if (row.get("email") or "").strip():
        return False, "έχει email"
    # Τηλέφωνο = συμπλήρωσε φόρμα. Δεν είναι απλή περιήγηση.
    if (row.get("phone") or "").strip():
        return False, "έχει τηλέφωνο"
    created = row.get("created_at") or ""
    try:
        when = datetime.fromisoformat(created.replace("Z", "+00:00"))
    except ValueError:
        return False, "άγνωστη ημερομηνία"
    if when > cutoff:
        return False, f"πρόσφατο ({when:%Y-%m-%d})"
    return True, f"{(datetime.now(timezone.utc) - when).days} ημερών"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    ap.add_argument("--delete", action="store_true", help="πραγματική διαγραφή")
    ap.add_argument("--confirm-staging", action="store_true",
                    help="ρητή επιβεβαίωση — απαιτείται μαζί με --delete")
    args = ap.parse_args()

    env.print_banner()
    # Διπλό guard: σωστό περιβάλλον ΚΑΙ ρητή σημαία. Το ένα χωρίς το άλλο δεν αρκεί —
    # ένα ξεχασμένο export ή ένα cron που ξαναέτρεξε δεν πρέπει να σβήνει πελάτες.
    if args.delete:
        env.require_destructive(args.confirm_staging)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    rows = (db._client().table("clients")
            .select("id,name,business_type,city,phone,email,status,created_at")
            .order("created_at").execute().data or [])

    doomed, kept = [], []
    for row in rows:
        ok, why = _is_abandoned(row, cutoff)
        (doomed if ok else kept).append((row, why))

    print("=" * 66)
    print(f"ΕΓΚΑΤΑΛΕΙΜΜΕΝΟΙ ΠΕΛΑΤΕΣ — όριο {args.days} ημερών")
    print("=" * 66)
    print(f"\nΣύνολο: {len(rows)}   Προς διαγραφή: {len(doomed)}   Διατηρούνται: {len(kept)}\n")

    for row, why in doomed:
        print(f"  ✗ {row['created_at'][:10]}  {str(row.get('name'))[:28]:28} {why}")
        print(f"      {row['id']}")

    if not doomed:
        print("  (τίποτα προς διαγραφή)")
        return 0

    if not args.delete:
        print(f"\nDRY RUN — δεν διαγράφηκε τίποτα.")
        print(f"Για πραγματική διαγραφή:  python scripts/cleanup_abandoned.py --days {args.days} --delete")
        return 0

    print()
    failed = 0
    for row, _ in doomed:
        try:
            db.delete_client(row["id"])
            print(f"  ✓ διαγράφηκε {row['id']}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  ✗ ΑΠΕΤΥΧΕ {row['id']}: {e}")

    print(f"\nΔιαγράφηκαν {len(doomed) - failed} από {len(doomed)}.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
