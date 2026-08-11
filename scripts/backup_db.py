#!/usr/bin/env python3
"""
Λογικό backup & ΔΟΚΙΜΑΣΜΕΝΗ επαναφορά.

    python scripts/backup_db.py --dump                                  # δεδομένα → φάκελο
    python scripts/backup_db.py --dump --verify --confirm-staging       # + απόδειξη επαναφοράς

Γιατί όχι pg_dump: δεν υπάρχει στο μηχάνημα και η έκδοσή του πρέπει να ταιριάζει με
τον server. Δεν το χρειαζόμαστε — **το σχήμα ζει ήδη στο `db/migrations/`**. Άρα
backup = μόνο δεδομένα, επαναφορά = migrations σε άδεια βάση + φόρτωση. Ανεξάρτητο
έκδοσης και επαληθεύσιμο.

Η ΕΠΑΛΗΘΕΥΣΗ ΤΡΕΧΕΙ ΣΕ ΠΡΑΓΜΑΤΙΚΑ ΑΔΕΙΑ ΒΑΣΗ (Docker), όχι σε schema.
Πρώτη προσπάθεια ήταν με προσωρινό schema και απέτυχε: τα migrations 0002/0003/0004
γράφουν ρητά `public.`, οπότε αγνοούν το `search_path` και πειράζουν το αληθινό
schema. Άδεια βάση είναι ο μόνος τρόπος να αποδειχθεί κάτι.

Κύκλος: container postgres:16 → migrations → φόρτωση → σύγκριση πλήθους ανά
πίνακα → **σβήσιμο container**, ακόμα κι αν κάτι αποτύχει.

Χρειάζεται να τρέχει ο Docker daemon. Προσωρινό Supabase project δοκιμάστηκε ως
εναλλακτική και ΔΕΝ γίνεται: το δωρεάν όριο (2 ενεργά) είναι ήδη πιασμένο από
vitrina + vitrina-staging, και είναι ανά χρήστη, όχι ανά οργανισμό.
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

MIGRATIONS = Path("db/migrations")
SKIP_TABLES = {"schema_migrations"}
# Kept in the raw JSON backup for forensic rollback, but intentionally omitted
# when restoring into the canonical schema. They were staging-only drift and no
# runtime code reads them anymore.
WITHDRAWN_TABLES = {"site_variants"}
WITHDRAWN_COLUMNS = {"clients": {"selected_layout"}}


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


def _docker_ready() -> bool:
    """Docker = η καλύτερη απομόνωση: δωρεάν, γρήγορη, χωρίς όρια projects."""
    import subprocess
    try:
        return subprocess.run(["docker", "info"], capture_output=True,
                              timeout=25).returncode == 0
    except Exception:  # noqa: BLE001
        return False


def _throwaway_postgres():
    """Προσωρινός Postgres σε container. Επιστρέφει (dsn, teardown)."""
    import secrets, subprocess, time
    import psycopg2

    name = f"vitrina-restore-{secrets.token_hex(4)}"
    port = 55000 + secrets.randbelow(2000)
    pw = secrets.token_hex(12)
    print(f"    container {name} @ {port}")
    subprocess.run(["docker", "run", "-d", "--rm", "--name", name,
                    "-e", f"POSTGRES_PASSWORD={pw}",
                    "-p", f"{port}:5432", "postgres:16-alpine"],
                   capture_output=True, check=True, timeout=600)

    def teardown():
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=60)
        print(f"    {name} σβήστηκε")

    dsn = f"postgresql://postgres:{pw}@127.0.0.1:{port}/postgres"
    for _ in range(45):
        try:
            psycopg2.connect(dsn, connect_timeout=3).close()
            return dsn, teardown
        except Exception:  # noqa: BLE001
            time.sleep(1.5)
    teardown()
    sys.exit("⛔ Ο προσωρινός Postgres δεν σηκώθηκε.")


def _restore_and_compare(dsn, src, manifest, teardown) -> int:
    """Migrations σε ΑΔΕΙΑ βάση, φόρτωση backup, σύγκριση, καθάρισμα."""
    import psycopg2
    ok, bad = [], []
    conn = None
    try:
        conn = psycopg2.connect(dsn); conn.autocommit = False
        with conn.cursor() as cur:
            # Τα migrations δίνουν GRANT σε ρόλους που φτιάχνει το Supabase, όχι ο
            # Postgres. Χωρίς αυτούς η επαναφορά σε καθαρή βάση σκάει με
            # «role "anon" does not exist» — δηλαδή δεν θα μπορούσαμε να
            # ανακτήσουμε πουθενά αλλού. Τους δημιουργούμε ρητά.
            print("[2] Ρόλοι & επεκτάσεις που περιμένει το Supabase")
            cur.execute("""
                DO $$ BEGIN
                  CREATE ROLE anon            NOLOGIN NOINHERIT;
                  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
                DO $$ BEGIN
                  CREATE ROLE authenticated   NOLOGIN NOINHERIT;
                  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
                DO $$ BEGIN
                  CREATE ROLE service_role    NOLOGIN NOINHERIT BYPASSRLS;
                  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
                CREATE EXTENSION IF NOT EXISTS pgcrypto;
                CREATE SCHEMA IF NOT EXISTS auth;
                CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid
                  LANGUAGE sql STABLE AS $$ SELECT NULL::uuid $$;
                CREATE OR REPLACE FUNCTION auth.role() RETURNS text
                  LANGUAGE sql STABLE AS $$ SELECT NULL::text $$;
            """)
            conn.commit()
            print("    ✓ anon, authenticated, service_role, auth.uid()")

            print("[3] Migrations σε άδεια βάση")
            for path in sorted(MIGRATIONS.glob("*.sql")):
                try:
                    cur.execute(path.read_text(encoding="utf-8")); conn.commit()
                    print(f"    ✓ {path.name}")
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    bad.append(f"migration {path.name}: {str(e).splitlines()[0][:70]}")
                    print(f"    ✗ {path.name}")

            print("[4] Φόρτωση backup")
            for table in manifest["order"]:
                if table in WITHDRAWN_TABLES:
                    print(f"    ⊘ {table} (αποσυρμένο, διατηρείται μόνο στο raw backup)")
                    continue
                rows = json.loads((src / f"{table}.json").read_text(encoding="utf-8"))
                if not rows:
                    continue
                cols = [c for c in rows[0].keys()
                        if c not in WITHDRAWN_COLUMNS.get(table, set())]
                collist = ",".join(f'"{c}"' for c in cols)
                marks = ",".join(["%s"] * len(cols))
                try:
                    for row in rows:
                        cur.execute(
                            # ON CONFLICT: κάποια migrations σπέρνουν πίνακες
                            # αναφοράς (capability_definitions, plan_capabilities).
                            # Χωρίς αυτό η επαναφορά σκάει σε διπλό κλειδί ενώ τα
                            # δεδομένα είναι ήδη σωστά.
                            f'INSERT INTO public."{table}" ({collist}) VALUES ({marks})'
                            f' ON CONFLICT DO NOTHING',
                            [json.dumps(row[c]) if isinstance(row[c], (dict, list)) else row[c]
                             for c in cols])
                    conn.commit()
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    bad.append(f"{table}: {str(e).splitlines()[0][:70]}")

            print("\n[4] Σύγκριση πλήθους γραμμών")
            for table, expected in manifest["tables"].items():
                if table in WITHDRAWN_TABLES:
                    print(f"    ⊘ {table:26} αποσυρμένο (raw archive: {expected})")
                    continue
                try:
                    cur.execute(f'SELECT count(*) FROM public."{table}"')
                    got = cur.fetchone()[0]
                except Exception:  # noqa: BLE001
                    conn.rollback(); bad.append(f"{table}: δεν διαβάστηκε"); continue
                mark = "✓" if got == expected else "✗"
                print(f"    {mark} {table:26} {got:>5} / {expected}")
                (ok if got == expected else bad).append(
                    table if got == expected else f"{table}: {got} αντί για {expected}")
    finally:
        if conn is not None:
            conn.close()
        print("\n[5] Καθαρισμός")
        teardown()

    print("\n" + "=" * 60)
    print(f"ΠΙΝΑΚΕΣ ΟΚ: {len(ok)}   ΠΡΟΒΛΗΜΑΤΑ: {len(bad)}")
    if bad:
        print("\n❌ " + "\n   ".join(bad))
        return 1
    print("\n✅ Το backup επαναφέρθηκε σε ΑΔΕΙΑ βάση και ταιριάζει γραμμή προς γραμμή.")
    return 0


def verify_restore(src: Path) -> int:
    """Απόδειξη ότι το backup επαναφέρεται — σε πραγματικά άδεια βάση.

    Schema-level απομόνωση δεν αρκεί: τα migrations 0002/0003/0004 γράφουν ρητά
    `public.` και αγνοούν το search_path.
    """
    env.require("staging")
    manifest = json.loads((src / "manifest.json").read_text(encoding="utf-8"))

    if not _docker_ready():
        sys.exit("⛔ Χρειάζεται Docker για την επαλήθευση — δεν τρέχει ο daemon.\n"
                 "   Ξεκίνα το Docker Desktop και ξανατρέξε.\n"
                 "   (Εναλλακτικά προσωρινό Supabase project, αλλά οι δωρεάν\n"
                 "    θέσεις είναι εξαντλημένες: vitrina + vitrina-staging.)")

    print("\n[1] Προσωρινός Postgres σε container")
    dsn, teardown = _throwaway_postgres()
    return _restore_and_compare(dsn, src, manifest, teardown)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--verify", "--verify-restore", dest="verify_restore",
                    action="store_true")
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
