#!/usr/bin/env python3
"""
Migrations runner — μία βάση, μία σειρά, μία καταγραφή.

    python scripts/migrate.py --status                       # τι έχει τρέξει
    VITRINA_ENV=staging    python scripts/migrate.py --apply
    VITRINA_ENV=production python scripts/migrate.py --apply --confirm-production

Γιατί υπάρχει: τα SQL έτρεχαν χειροκίνητα στο Supabase SQL Editor, χωρίς σειρά
και χωρίς καταγραφή. Δεν μπορούσε να στηθεί δεύτερη βάση με βεβαιότητα ότι
είναι ίδια — άρα το staging δεν θα ήταν αντίγραφο, θα ήταν εικασία.

ΚΑΝΟΝΑΣ ΣΧΗΜΑΤΟΣ: μόνο προσθετικές αλλαγές ανά έκδοση. Για καταστροφική αλλαγή
(μετονομασία/διαγραφή στήλης) ακολουθούμε expand → migrate data → contract σε
ΞΕΧΩΡΙΣΤΑ releases:

    release N     0007_add_new_column.sql        (expand — γράφουν και τα δύο)
    release N+1   0008_backfill_new_column.sql   (migrate data)
    release N+2   0009_drop_old_column.sql       (contract — αφού ο παλιός
                                                  κώδικας δεν τρέχει πουθενά)

Έτσι το rollback του κώδικα είναι πάντα ασφαλές: η παλιά έκδοση βρίσκει το
σχήμα που περιμένει.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import env  # noqa: E402

MIGRATIONS = Path("db/migrations")
NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")

TRACKING = """
CREATE TABLE IF NOT EXISTS schema_migrations (
  version     text PRIMARY KEY,
  filename    text NOT NULL,
  checksum    text NOT NULL,
  applied_at  timestamptz NOT NULL DEFAULT now()
);
"""


def _dsn() -> str:
    """Postgres connection string του τρέχοντος περιβάλλοντος.

    Χωριστό όνομα ανά περιβάλλον, όπως και τα υπόλοιπα credentials — ώστε ένα
    λάθος flag να μη βρίσκει καν στοιχεία σύνδεσης για την παραγωγή."""
    suffix = "PRODUCTION" if env.is_production else "STAGING"
    dsn = os.environ.get(f"DATABASE_URL_{suffix}", "").strip()
    if not dsn:
        sys.exit(
            f"⛔ Λείπει το DATABASE_URL_{suffix}.\n"
            f"   Supabase → Project Settings → Database → Connection string (URI).\n"
            f"   {env.banner()}"
        )
    return dsn


def _files() -> list[Path]:
    if not MIGRATIONS.is_dir():
        sys.exit(f"⛔ Δεν βρέθηκε ο φάκελος {MIGRATIONS}")
    out = []
    for path in sorted(MIGRATIONS.iterdir()):
        if path.suffix != ".sql":
            continue
        if not NAME_RE.match(path.name):
            sys.exit(f"⛔ Λάθος όνομα: {path.name}\n   Μορφή: 0007_short_description.sql")
        out.append(path)
    versions = [NAME_RE.match(p.name).group(1) for p in out]
    if len(set(versions)) != len(versions):
        sys.exit("⛔ Διπλός αριθμός έκδοσης στο db/migrations/")
    return out


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="τι έχει τρέξει (default)")
    ap.add_argument("--apply", action="store_true", help="εφάρμοσε ό,τι λείπει")
    ap.add_argument("--confirm-production", action="store_true",
                    help="απαιτείται για --apply στην παραγωγή")
    args = ap.parse_args()

    env.print_banner()

    if args.apply and env.is_production and not args.confirm_production:
        sys.exit("⛔ Migration στην ΠΑΡΑΓΩΓΗ χωρίς επιβεβαίωση.\n"
                 "   Πρόσθεσε --confirm-production. Και τρέξ' το πρώτα σε staging.")

    try:
        import psycopg2
    except ImportError:
        sys.exit("⛔ Λείπει το psycopg2. pip install psycopg2-binary")

    files = _files()
    conn = psycopg2.connect(_dsn())
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(TRACKING)
            conn.commit()
            cur.execute("SELECT version, checksum FROM schema_migrations")
            done = dict(cur.fetchall())

        print(f"\n{len(files)} migrations στο δίσκο, {len(done)} εφαρμοσμένα\n")
        pending = []
        for path in files:
            version = NAME_RE.match(path.name).group(1)
            checksum = _checksum(path)
            if version in done:
                changed = done[version] != checksum
                mark = "⚠️  ΑΛΛΑΞΕ" if changed else "✓"
                print(f"  {mark} {path.name}")
                if changed:
                    print(f"      Το αρχείο άλλαξε μετά την εφαρμογή. Τα migrations είναι")
                    print(f"      αμετάβλητα — φτιάξε ΝΕΟ αρχείο αντί να πειράξεις αυτό.")
            else:
                print(f"  · {path.name}  (εκκρεμεί)")
                pending.append((version, path, checksum))

        if not pending:
            print("\n✅ Η βάση είναι ενημερωμένη.")
            return 0
        if not args.apply:
            print(f"\n{len(pending)} εκκρεμούν. Για εφαρμογή:  --apply")
            return 0

        print()
        for version, path, checksum in pending:
            sql = path.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                try:
                    cur.execute(sql)
                    cur.execute(
                        "INSERT INTO schema_migrations (version, filename, checksum) "
                        "VALUES (%s, %s, %s)", (version, path.name, checksum))
                    conn.commit()
                    print(f"  ✓ {path.name}")
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    print(f"  ✗ {path.name}\n      {e}")
                    print("\n⛔ Σταμάτησα. Οι επόμενες δεν έτρεξαν.")
                    return 1
        print(f"\n✅ Εφαρμόστηκαν {len(pending)}.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
