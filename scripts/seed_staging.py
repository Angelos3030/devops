#!/usr/bin/env python3
"""
Seed & reset του staging — ντετερμινιστικά συνθετικά δεδομένα για τα E2E.

    VITRINA_ENV=staging python scripts/seed_staging.py --seed  --confirm-staging
    VITRINA_ENV=staging python scripts/seed_staging.py --reset --confirm-staging

Κάθε test run ξεκινά από γνωστή κατάσταση και την αφήνει καθαρή. Τα UUID είναι
σταθερά ώστε τα tests να μη μαντεύουν — γράφεις `QA_CLIENTS["taverna"]` και ξέρεις
τι θα βρεις.

ΑΣΦΑΛΕΙΑ — τρία επίπεδα, γιατί αυτό το script ΣΒΗΝΕΙ:
  1. `env.require_destructive()`  — μόνο staging, μόνο με --confirm-staging
  2. Το reset αγγίζει ΜΟΝΟ ό,τι έχει το πρόθεμα `qa-` στο email ή σταθερό QA uuid
  3. Πριν σβήσει, μετράει: αν βρει πελάτες εκτός QA πάνω από ένα όριο, σταματά —
     είναι ένδειξη ότι δείχνει σε λάθος βάση
"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import db, env  # noqa: E402

QA_PREFIX = "qa-"
# Σταθερά UUID: τα tests αναφέρονται σε αυτά ονομαστικά.
QA_CLIENTS = {
    "taverna": {
        "id": "aaaa0001-0000-4000-8000-000000000001",
        "name": "Ταβέρνα Δοκιμή", "business_type": "Ταβέρνα", "city": "Γέρακας",
        "phone": "2100000001", "email": "qa-taverna@vitrina.test",
        "address": "Λ. Μαραθώνος 1",
    },
    "cafe": {
        "id": "aaaa0002-0000-4000-8000-000000000002",
        "name": "Καφετέρια Δοκιμή", "business_type": "Καφετέρια", "city": "Χαλάνδρι",
        "phone": "2100000002", "email": "qa-cafe@vitrina.test",
        "address": "Ηρώδου Αττικού 2",
    },
    "dentist": {
        "id": "aaaa0003-0000-4000-8000-000000000003",
        "name": "Οδοντιατρείο Δοκιμή", "business_type": "Οδοντιατρείο", "city": "Μαρούσι",
        "phone": "2100000003", "email": "qa-dentist@vitrina.test",
        "address": "Κηφισίας 3",
    },
    "salon": {
        "id": "aaaa0004-0000-4000-8000-000000000004",
        "name": "Κομμωτήριο Δοκιμή", "business_type": "Κομμωτήριο", "city": "Γλυφάδα",
        "phone": "2100000004", "email": "qa-salon@vitrina.test",
        "address": "Γρηγορίου Λαμπράκη 4",
    },
    "plumber": {
        "id": "aaaa0005-0000-4000-8000-000000000005",
        "name": "Υδραυλικός Δοκιμή", "business_type": "Υδραυλικός", "city": "Πειραιάς",
        "phone": "2100000005", "email": "qa-plumber@vitrina.test",
        "address": "Ακτή Μιαούλη 5",
    },
}

# Ένας πελάτης χωρίς τίποτα — για τα empty states, που είναι η αρχή #8.
QA_EMPTY = {
    "id": "aaaa0006-0000-4000-8000-000000000006",
    "name": "Κενός Δοκιμή", "business_type": "Άλλο", "city": "Αθήνα",
    "email": "qa-empty@vitrina.test",
}

CONTENT = {
    "taverna": {"tagline": "Σπιτικό φαγητό κάθε μέρα", "hours": "Δευτ.–Κυρ. 12:00–00:00",
                "services": [{"name": "Μεζέδες", "description": "Φρέσκοι, καθημερινά"},
                             {"name": "Ψητά", "description": "Στα κάρβουνα"}]},
    "cafe": {"tagline": "Καφές που αξίζει", "hours": "Καθημερινά 07:00–22:00",
             "services": [{"name": "Espresso bar", "description": "Φρεσκοκαβουρδισμένος"}]},
    "dentist": {"tagline": "Ήρεμη οδοντιατρική φροντίδα", "hours": "Δευτ.–Παρ. 09:00–20:00",
                "services": [{"name": "Προληπτικός έλεγχος", "description": "Τακτικός καθαρισμός"},
                             {"name": "Αισθητική", "description": "Λεύκανση"},
                             {"name": "Εμφυτεύματα", "description": "Μόνιμη αποκατάσταση"}]},
    "salon": {"tagline": "Το στιλ σου, η δουλειά μας", "hours": "Τρ.–Σάβ. 09:00–20:00",
              "services": [{"name": "Κούρεμα", "description": "Ανδρικό & γυναικείο"}]},
    "plumber": {"tagline": "24 ώρες, όλη την Αττική", "hours": "24/7",
                "services": [{"name": "Αποφράξεις", "description": "Άμεση επέμβαση"}]},
}

# Αν βρεθούν τόσοι μη-QA πελάτες, κάτι δεν πάει καλά: μάλλον δείχνουμε αλλού.
SANITY_LIMIT = 50


def _all_qa_ids() -> list[str]:
    return [c["id"] for c in QA_CLIENTS.values()] + [QA_EMPTY["id"]]


def _sanity() -> None:
    """Τελευταία γραμμή άμυνας πριν σβήσουμε οτιδήποτε."""
    rows = db._client().table("clients").select("id,email").execute().data or []
    qa_ids = set(_all_qa_ids())
    foreign = [r for r in rows
               if r["id"] not in qa_ids and not (r.get("email") or "").startswith(QA_PREFIX)]
    if len(foreign) > SANITY_LIMIT:
        sys.exit(
            f"⛔ Βρέθηκαν {len(foreign)} πελάτες που ΔΕΝ είναι QA.\n"
            f"   Αυτό δεν μοιάζει με staging. Σταματώ πριν σβήσω κάτι αληθινό.\n"
            f"   {env.banner()}"
        )
    print(f"  (μη-QA πελάτες στη βάση: {len(foreign)} — εντός ορίου)")


def reset() -> int:
    print("\n[reset] Σβήνω μόνο QA δεδομένα")
    _sanity()
    gone = 0
    for cid in _all_qa_ids():
        try:
            db.delete_client(cid)
            gone += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ! {cid}: {e}")
    # Ό,τι έμεινε με πρόθεμα qa- (π.χ. από αποτυχημένο test)
    rows = db._client().table("clients").select("id,email").execute().data or []
    for r in rows:
        if (r.get("email") or "").startswith(QA_PREFIX):
            try:
                db.delete_client(r["id"])
                gone += 1
            except Exception:  # noqa: BLE001
                pass
    print(f"  ✓ καθαρίστηκαν {gone}")
    return 0


def seed() -> int:
    print("\n[seed] Δημιουργώ συνθετικούς πελάτες")
    reset()
    made = 0
    for key, row in list(QA_CLIENTS.items()) + [("empty", QA_EMPTY)]:
        try:
            db._client().table("clients").insert({**row, "status": "active", "plan": "site"}).execute()
            if key in CONTENT:
                db.save_site_content(row["id"], CONTENT[key])
            print(f"  ✓ {key:9} {row['id']}")
            made += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {key}: {str(e)[:90]}")
    print(f"\n  {made} πελάτες έτοιμοι.")
    print("  Χρήστες: τα emails qa-*@vitrina.test — φτιάξ' τους στο Supabase Auth")
    print("  με κωδικό (admin API) ώστε τα E2E να συνδέονται χωρίς magic link.")
    return 0 if made else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--confirm-staging", action="store_true")
    args = ap.parse_args()

    env.print_banner()
    if not (args.seed or args.reset):
        print("\nΧρήση: --seed ή --reset (και --confirm-staging)")
        return 0
    env.require_destructive(args.confirm_staging)
    return seed() if args.seed else reset()


if __name__ == "__main__":
    raise SystemExit(main())
