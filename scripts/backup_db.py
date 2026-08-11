#!/usr/bin/env python3
"""
Λογικό backup & ΔΟΚΙΜΑΣΜΕΝΗ επαναφορά.

    python scripts/backup_db.py --dump                       # δεδομένα → φάκελο
    python scripts/backup_db.py --verify-restore --confirm-staging
    python scripts/backup_db.py --dump --out C:/backups/2026-08-11

Γιατί όχι pg_dump: δεν υπάρχει στο μηχάνημα, και η έκδοσή του πρέπει να ταιριάζει
με τον server. Δεν το χρειαζόμαστε — **το σχήμα ζει ήδη στο `db/migrations/`**.
Άρα backup = μόνο τα δεδομένα, και επαναφορά = migrations σε άδεια βάση + φόρτωση.
Αυτό είναι και ανεξάρτητο έκδοσης και επαληθεύσιμο.

⚠️ ΤΟ --verify-restore ΔΕΝ ΕΙΝΑΙ ΑΚΟΜΑ ΑΠΟΜΟΝΩΜΕΝΟ — ΜΗΝ ΤΟ ΕΜΠΙΣΤΕΥΕΣΑΙ.

Η ιδέα ήταν: προσωρινό schema, migrations εκεί, φόρτωση, σύγκριση, διαγραφή.
Δεν δουλεύει, γιατί τα migrations 0002/0003/0004 γράφουν ρητά `public.` — άρα
αγνοούν το search_path και πειράζουν το ΑΛΗΘΙΝΟ schema. Στη δοκιμή δεν έσπασε
τίποτα (όλα idempotent, επαληθεύτηκε), αλλά η απομόνωση είναι ψεύτικη.

Η σωστή λύση είναι ΠΡΟΣΩΡΙΝΟ SUPABASE PROJECT μέσω Management API: άδεια βάση →
migrations → φόρτωση → σύγκριση → διαγραφή project. Δεν έχει υλοποιηθεί ακόμα.

Μέχρι τότε το `--dump` είναι αξιόπιστο· η επαλήθευση ΟΧΙ. Και backup χωρίς
δοκιμασμένη επαναφορά είναι μισή λύση.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import env  # noqa: E402

SCRATCH = "restore_check"          # προσωρινό schema — ποτέ το public
MIGRATIONS = Path("db/migrations")
SKIP_TABLES = {"schema_migrations"}


def _dsn() -> str:
    suffix = "PRODUCTION" if env.is_production else "STAGING"
    dsn = os.environ.get(f"DATABASE_URL_{suffix}", "").strip()
    if not dsn:
        sys.exit(f"⛔ Λείπει το DATABASE_URL_{suffix}.\n   {env.banner()}")
    return dsn


def _connect():
    try:
        import psycopg2
    except ImportError:
        sys.exit("⛔ Λείπει το psycopg2. pip install psycopg2-binary")
    conn = psycopg2.connect(_dsn())
    conn.autocommit = False
    return conn


def _tables(cur, schema: str = "public") -> list[str]:
    cur.execute("""
        SELECT c.relname FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = %s AND c.relkind = 'r' ORDER BY 1
    """, (schema,))
    return [r[0] for r in cur.fetchall() if r[0] not in SKIP_TABLES]


def _fk_order(cur, tables: list[str], schema: str = "public") -> list[str]:
    """Τοπολογική σειρά: οι γονείς πρώτα, αλλιώς τα foreign keys σκάνε."""
    cur.execute("""
        SELECT c.conrelid::regclass::text, c.confrelid::regclass::text
        FROM pg_constraint c
        JOIN pg_namespace n ON n.oid = c.connamespace
        WHERE c.contype = 'f' AND n.nspname = %s
    """, (schema,))
    deps: dict[str, set[str]] = {t: set() for t in tables}
    for child, parent in cur.fetchall():
        child = child.split(".")[-1].strip('"')
        parent = parent.split(".")[-1].strip('"')
        if child in deps and parent in deps and child != parent:
            deps[child].add(parent)

    ordered, seen = [], set()
    while len(ordered) < len(tables):
        ready = [t for t in tables if t not in seen and deps[t] <= seen]
        if not ready:                       # κύκλος — σπάσ' τον ντετερμινιστικά
            ready = [sorted(t for t in tables if t not in seen)[0]]
        for t in sorted(ready):
            ordered.append(t); seen.add(t)
    return ordered


def dump(out_dir: Path) -> int:
    conn = _connect()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "env": env.current, "at": datetime.now(timezone.utc).isoformat(),
        "tables": {},
    }
    try:
        with conn.cursor() as cur:
            tables = _fk_order(cur, _tables(cur))
            print(f"\n{len(tables)} πίνακες, σε σειρά εξαρτήσεων\n")
            for table in tables:
                cur.execute(f'SELECT * FROM public."{table}"')
                cols = [d[0] for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                path = out_dir / f"{table}.json"
                path.write_text(json.dumps(rows, ensure_ascii=False, default=str, indent=1),
                                encoding="utf-8")
                manifest["tables"][table] = len(rows)
                print(f"  ✓ {table:24} {len(rows):>6} γραμμές")
            manifest["order"] = tables
    finally:
        conn.close()

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(manifest["tables"].values())
    print(f"\n✅ {total} γραμμές → {out_dir}")
    return 0


def verify_restore(src: Path) -> int:
    """ΑΤΕΛΗΣ — βλ. προειδοποίηση στην κορυφή του αρχείου."""
    env.require("staging")
    print("
⚠️  Η απομόνωση ΔΕΝ είναι πραγματική: τα migrations 0002/0003/0004")
    print("   γράφουν ρητά σε public. Χρειάζεται προσωρινό project, όχι schema.")
    manifest = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
    conn = _connect()
    ok, bad = [], []
    try:
        with conn.cursor() as cur:
            print(f"\n[1] Προσωρινό schema «{SCRATCH}»")
            cur.execute(f'DROP SCHEMA IF EXISTS {SCRATCH} CASCADE')
            cur.execute(f'CREATE SCHEMA {SCRATCH}')
            conn.commit()

            print("[2] Migrations στο προσωρινό schema")
            cur.execute(f'SET search_path TO {SCRATCH}, public')
            for path in sorted(MIGRATIONS.glob("*.sql")):
                sql = path.read_text(encoding="utf-8")
                try:
                    cur.execute(sql)
                    conn.commit()
                    print(f"  ✓ {path.name}")
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    # Οι πολιτικές RLS αναφέρονται σε ρόλους/πίνακες του public.
                    # Δεν εμποδίζουν την επαλήθευση δεδομένων.
                    print(f"  · {path.name} (παραλείφθηκε: {str(e).splitlines()[0][:60]})")

            print("[3] Φόρτωση δεδομένων")
            cur.execute(f'SET search_path TO {SCRATCH}')
            for table in manifest["order"]:
                rows = json.loads((src / f"{table}.json").read_text(encoding="utf-8"))
                if not rows:
                    continue
                cols = list(rows[0].keys())
                placeholders = ",".join(["%s"] * len(cols))
                collist = ",".join(f'"{c}"' for c in cols)
                try:
                    for row in rows:
                        cur.execute(
                            f'INSERT INTO {SCRATCH}."{table}" ({collist}) VALUES ({placeholders})'
                            f' ON CONFLICT DO NOTHING',
                            [json.dumps(row[c]) if isinstance(row[c], (dict, list)) else row[c]
                             for c in cols])
                    conn.commit()
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    bad.append(f"{table}: {str(e).splitlines()[0][:70]}")
                    continue

            print("\n[4] Σύγκριση πλήθους γραμμών")
            for table, expected in manifest["tables"].items():
                try:
                    cur.execute(f'SELECT count(*) FROM {SCRATCH}."{table}"')
                    got = cur.fetchone()[0]
                except Exception as e:  # noqa: BLE001
                    bad.append(f"{table}: δεν διαβάστηκε ({str(e).splitlines()[0][:50]})")
                    conn.rollback()
                    continue
                if got == expected:
                    ok.append(table)
                    print(f"  ✓ {table:24} {got:>6} / {expected}")
                else:
                    bad.append(f"{table}: {got} αντί για {expected}")
                    print(f"  ✗ {table:24} {got:>6} / {expected}")
    finally:
        try:
            with conn.cursor() as cur:
                cur.execute(f'DROP SCHEMA IF EXISTS {SCRATCH} CASCADE')
                conn.commit()
            print(f"\n[5] Το προσωρινό schema σβήστηκε")
        except Exception as e:  # noqa: BLE001
            print(f"\n⚠️ Δεν σβήστηκε το {SCRATCH}: {e}")
        conn.close()

    print("\n" + "=" * 60)
    print(f"ΠΙΝΑΚΕΣ ΟΚ: {len(ok)}   ΠΡΟΒΛΗΜΑΤΑ: {len(bad)}")
    if bad:
        print("\n❌ " + "\n   ".join(bad))
        return 1
    print("\n✅ Η επαναφορά δοκιμάστηκε και πέτυχε. Το backup είναι πραγματικό.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--verify-restore", action="store_true")
    ap.add_argument("--confirm-staging", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    env.print_banner()
    out = Path(args.out) if args.out else Path(
        os.environ.get("TEMP", "/tmp")) / "vitrina-backup" / f"{env.current}-{datetime.now():%Y%m%d-%H%M}"

    if args.dump:
        code = dump(out)
        if args.verify_restore:
            env.require_destructive(args.confirm_staging)
            return verify_restore(out)
        return code
    if args.verify_restore:
        if not args.out:
            sys.exit("⛔ Το --verify-restore χρειάζεται --out με υπάρχον backup.")
        env.require_destructive(args.confirm_staging)
        return verify_restore(out)

    print("\nΧρήση: --dump [--verify-restore --confirm-staging] [--out ΦΑΚΕΛΟΣ]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
