"""Ποιο migration αντέχει δεύτερη εκτέλεση και ποιο όχι.

Το `migrate.py` δεν ξανατρέχει ό,τι είναι καταγεγραμμένο, οπότε αυτό δεν είναι
καθημερινό μονοπάτι. Γίνεται όμως κρίσιμο σε δύο περιπτώσεις:
  · συμφιλίωση checksum μετά από διόρθωση αρχείου,
  · ανάκτηση όπου κάποιος τρέχει ξανά «για σιγουριά».

Μετράμε ανά αρχείο, σε βάση που έχει ήδη ολόκληρη την αλυσίδα.
"""
from __future__ import annotations

import pathlib
import sys

import psycopg2

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from tests.test_migration_chain import (  # noqa: E402
    LEGACY_SHAPE, MIGRATIONS, Postgres, apply_all, docker_ok, migration_files)

if not docker_ok():
    sys.exit("⛔ χρειάζεται Docker/Podman")

with Postgres() as dsn:
    apply_all(dsn, after_version={"0003": LEGACY_SHAPE})
    print("  αλυσίδα εφαρμοσμένη· τώρα κάθε αρχείο ΞΑΝΑ, χωριστά\n")
    for path in migration_files():
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(path.read_text(encoding="utf-8"))
            print(f"  ✓ {path.name}")
        except Exception as e:  # noqa: BLE001
            first = str(e).strip().splitlines()[0]
            print(f"  ✗ {path.name}\n      {first}")
        finally:
            conn.close()
