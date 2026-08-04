#!/usr/bin/env python3
"""
Δοκιμαστική δημοσίευση στη Σελίδα ενός πελάτη.

    python scripts/publish_test.py --client <id>                    # ΜΟΝΟ δείχνει τι θα σταλεί
    python scripts/publish_test.py --client <id> --text "Γεια σου κόσμε"
    python scripts/publish_test.py --client <id> --image https://… --network instagram
    python scripts/publish_test.py --client <id> --for-real         # ΔΗΜΟΣΙΕΥΕΙ ΑΛΗΘΙΝΑ

Χωρίς `--for-real` δεν φεύγει τίποτα προς τη Meta. Η δημοσίευση είναι δημόσια
και δεν ξεγίνεται από εδώ — αν κάνεις λάθος, θα πρέπει να τη σβήσεις με το χέρι
από τη σελίδα.

Τρέχει τοπικά με τα κλειδιά του .env, χωρίς να χρειάζεται login στο dashboard.
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import db, publisher  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True, help="client_id (uuid)")
    ap.add_argument("--text", default="Δοκιμή από τη Vitrina 👋")
    ap.add_argument("--image", default=None, help="δημόσιο URL εικόνας")
    ap.add_argument("--network", choices=["facebook", "instagram", "both"], default="facebook")
    ap.add_argument("--for-real", action="store_true", help="ΔΗΜΟΣΙΕΥΣΕ στ' αλήθεια")
    a = ap.parse_args()

    creds = db.get_social_creds(a.client)
    if not creds:
        print("❌ Αυτός ο πελάτης δεν έχει συνδεδεμένη Σελίδα.")
        print("   Τρέξε πρώτα τη ροή σύνδεσης:")
        print(f"   https://api.getvitrina.gr/connect/start?client_id={a.client}")
        return 1

    print(f"Σελίδα     : {creds['page_id']}")
    print(f"Instagram  : {creds.get('ig_user_id') or '— (δεν συνδέθηκε)'}")
    print(f"Δίκτυο     : {a.network}")
    print(f"Κείμενο    : {a.text}")
    print(f"Εικόνα     : {a.image or '— (μόνο κείμενο· το Instagram θα απορρίψει)'}\n")

    targets = ["facebook", "instagram"] if a.network == "both" else [a.network]
    res = publisher.publish(a.client, a.text, a.image, targets, dry_run=not a.for_real)
    print(json.dumps(res, ensure_ascii=False, indent=2))

    if not a.for_real:
        print("\n⚪ ΔΟΚΙΜΗ — δεν στάλθηκε τίποτα. Πρόσθεσε --for-real για αληθινή δημοσίευση.")
        return 0

    failed = [k for k, v in res["results"].items() if not v.get("ok")]
    if failed:
        print(f"\n❌ Απέτυχαν: {', '.join(failed)}")
        return 1
    print("\n✅ Δημοσιεύτηκε.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
