#!/usr/bin/env python3
"""Παράγει το δομικό αποτύπωμα του baseline — ΑΠΟ ΤΟ ΙΔΙΟ ΤΟ 0000.

    python scripts/make_baseline_fingerprint.py

ΓΙΑΤΙ ΟΧΙ ΑΠΟ ΤΗΝ ΠΑΡΑΓΩΓΗ. Το αποτύπωμα είναι η ΑΠΑΙΤΗΣΗ που πρέπει να
ικανοποιεί μια βάση για να θεωρηθεί ότι «έχει ήδη το baseline». Αν το
παρήγαγα διαβάζοντας την παραγωγή, θα επαλήθευα την παραγωγή με τον εαυτό της
— κάθε λάθος της θα γινόταν αυτομάτως «σωστό». Παράγεται λοιπόν εκτελώντας το
0000 σε ΚΕΝΗ βάση και καταγράφοντας τι έφτιαξε.

ΤΙ ΜΠΑΙΝΕΙ ΜΕΣΑ: πίνακες, στήλες (τύπος + nullability), primary keys, unique
constraints, foreign keys. Δηλαδή ό,τι χρειάζονται τα ΕΠΟΜΕΝΑ migrations για
να τρέξουν.

ΤΙ ΔΕΝ ΜΠΑΙΝΕΙ: defaults στηλών και μη-μοναδικά index. Μια βάση σε παραγωγή
μπορεί κάλλιστα να έχει αποκτήσει επιπλέον index ή αλλαγμένο default χωρίς
αυτό να εμποδίζει κανένα migration. Το αποτύπωμα ελέγχει ΥΠΟΣΥΝΟΛΟ: ό,τι
απαιτείται πρέπει να υπάρχει· ό,τι παραπάνω είναι αποδεκτό.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "db" / "migrations" / "0000_production_baseline.sql"
OUT = ROOT / "db" / "baseline_fingerprint.json"

Q_COLUMNS = """
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns WHERE table_schema='public'
ORDER BY 1,2"""

Q_CONSTRAINTS = """
SELECT rel.relname, con.contype::text, con.conname, pg_get_constraintdef(con.oid)
FROM pg_constraint con
JOIN pg_class rel ON rel.oid=con.conrelid
JOIN pg_namespace n ON n.oid=rel.relnamespace
WHERE n.nspname='public' AND con.contype IN ('p','u','f')
ORDER BY 1,3"""


def build() -> dict:
    name = f"vitrina-fp-{secrets.token_hex(4)}"
    password = secrets.token_urlsafe(16)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    subprocess.run(
        ["docker", "run", "-d", "--rm", "--name", name,
         "-e", f"POSTGRES_PASSWORD={password}", "-e", "POSTGRES_DB=vitrina",
         "-p", f"{port}:5432", "postgres:17-alpine"],
        capture_output=True, check=True)
    dsn = f"postgresql://postgres:{password}@127.0.0.1:{port}/vitrina"
    try:
        for _ in range(90):
            try:
                psycopg2.connect(dsn, connect_timeout=2).close()
                break
            except psycopg2.OperationalError:
                time.sleep(0.5)
        else:
            raise RuntimeError("η Postgres δεν σηκώθηκε")

        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(BASELINE.read_text(encoding="utf-8"))
                cur.execute(Q_COLUMNS)
                columns = {f"{t}.{c}": f"{d}|{n}" for t, c, d, n in cur.fetchall()}
                cur.execute(Q_CONSTRAINTS)
                pks: dict[str, str] = {}
                uniques: dict[str, str] = {}
                fks: dict[str, str] = {}
                for table, kind, conname, definition in cur.fetchall():
                    target = {"p": pks, "u": uniques, "f": fks}[kind]
                    target[f"{table}:{conname}"] = definition
        finally:
            conn.close()
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)

    return {
        "version": "0000",
        "source_file": BASELINE.name,
        "source_checksum": hashlib.sha256(
            BASELINE.read_bytes()).hexdigest()[:16],
        "tables": sorted({k.split(".")[0] for k in columns}),
        "columns": columns,
        "primary_keys": pks,
        "unique_constraints": uniques,
        "foreign_keys": fks,
    }


def main() -> int:
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True,
                       timeout=25)
    except Exception:  # noqa: BLE001
        print("⛔ Χρειάζεται Docker/Podman daemon.")
        return 1
    fp = build()
    OUT.write_text(json.dumps(fp, ensure_ascii=False, indent=2, sort_keys=True)
                   + "\n", encoding="utf-8")
    print(f"✅ {OUT.relative_to(ROOT)}")
    print(f"   {len(fp['tables'])} πίνακες · {len(fp['columns'])} στήλες · "
          f"{len(fp['primary_keys'])} PK · {len(fp['unique_constraints'])} unique · "
          f"{len(fp['foreign_keys'])} FK")
    print(f"   checksum του 0000: {fp['source_checksum']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
