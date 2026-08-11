#!/usr/bin/env python3
"""
Παράγει baseline migration από το ΠΡΑΓΜΑΤΙΚΟ σχήμα της παραγωγής.

    python scripts/schema_snapshot.py --env production --out db/snapshots/production.json
    python scripts/make_baseline.py

Γιατί: βρέθηκαν δύο ανεξάρτητα συστήματα migrations και το staging είχε αποκλίνει
(28 πίνακες έναντι 12). Η λύση δεν είναι να γίνει η παραγωγή «πηγή αλήθειας» —
τότε κάθε χειροκίνητη αλλαγή νομιμοποιείται. Η λύση είναι **ένα** baseline που
αναπαριστά πιστά ό,τι υπάρχει σήμερα, και από εκεί και πέρα μία ακολουθία.

ΔΕΝ εφαρμόζει τίποτα. Γράφει αρχείο για ανθρώπινο έλεγχο.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SNAPSHOT = Path("db/snapshots/production.json")
OUT = Path("db/migrations/baseline/0000_production_baseline.sql")

# Τα πρώτα που πρέπει να υπάρχουν για να στηθούν τα foreign keys.
ROOT_TABLES = ("clients",)


def _fk_order(tables: list[str], constraints: list[dict]) -> list[str]:
    deps: dict[str, set[str]] = {t: set() for t in tables}
    for c in constraints:
        definition = c["definition"]
        if not definition.startswith("FOREIGN KEY"):
            continue
        child = c["table_name"]
        after = definition.split("REFERENCES", 1)[1].strip()
        parent = after.split("(")[0].strip().split(".")[-1].strip('"')
        if child in deps and parent in deps and child != parent:
            deps[child].add(parent)
    ordered, seen = [], set()
    for root in ROOT_TABLES:
        if root in deps:
            ordered.append(root); seen.add(root)
    while len(ordered) < len(tables):
        ready = sorted(t for t in tables if t not in seen and deps[t] <= seen)
        if not ready:
            ready = [sorted(t for t in tables if t not in seen)[0]]
        for t in ready:
            ordered.append(t); seen.add(t)
    return ordered


def main() -> int:
    if not SNAPSHOT.exists():
        sys.exit(f"⛔ Λείπει το {SNAPSHOT}. Τρέξε πρώτα το schema_snapshot.py --env production")
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    cols_by_table: dict[str, list[dict]] = defaultdict(list)
    for row in snap["columns"]:
        cols_by_table[row["table_name"]].append(row)

    cons_by_table: dict[str, list[dict]] = defaultdict(list)
    for row in snap["constraints"]:
        cons_by_table[row["table_name"]].append(row)

    idx_by_table: dict[str, list[dict]] = defaultdict(list)
    for row in snap["indexes"]:
        idx_by_table[row["table_name"]].append(row)

    rls = {r["table_name"]: r["enabled"] for r in snap["rls"]}
    order = _fk_order(snap["tables"], snap["constraints"])

    out: list[str] = [
        "-- 0000 — BASELINE ΠΑΡΑΓΩΓΗΣ",
        "--",
        "-- Παράχθηκε αυτόματα από το πραγματικό σχήμα της παραγωγής",
        "-- (scripts/make_baseline.py από db/snapshots/production.json).",
        "--",
        "-- ΓΙΑΤΙ: υπήρχαν δύο ανεξάρτητα συστήματα migrations — τα versioned αρχεία",
        "-- του repo και το ιστορικό του Supabase. Το staging είχε αποκλίνει σε 28",
        "-- πίνακες έναντι 12, ΚΑΙ η παραγωγή είχε index που δεν υπήρχε πουθενά στα",
        "-- αρχεία μας. Αυτό το αρχείο είναι το σημείο μηδέν της ενιαίας ακολουθίας.",
        "--",
        "-- ΔΕΝ εφαρμόζεται στην παραγωγή: η παραγωγή ΕΧΕΙ ήδη αυτό το σχήμα. Χρησιμεύει",
        "-- για να στηθεί καθαρό staging και για τη δοκιμή επαναφοράς.",
        "--",
        "-- Ασφαλές να ξανατρέξει (IF NOT EXISTS παντού).",
        "",
        "-- Ρόλοι που περιμένει το Supabase. Σε καθαρό Postgres δεν υπάρχουν και τα",
        "-- GRANT σκάνε — αυτό εμπόδιζε την ανάκτηση εκτός Supabase.",
        "DO $$ BEGIN CREATE ROLE anon          NOLOGIN NOINHERIT;",
        "  EXCEPTION WHEN duplicate_object THEN NULL; END $$;",
        "DO $$ BEGIN CREATE ROLE authenticated NOLOGIN NOINHERIT;",
        "  EXCEPTION WHEN duplicate_object THEN NULL; END $$;",
        "DO $$ BEGIN CREATE ROLE service_role  NOLOGIN NOINHERIT BYPASSRLS;",
        "  EXCEPTION WHEN duplicate_object THEN NULL; END $$;",
        'CREATE EXTENSION IF NOT EXISTS pgcrypto;',
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        "",
    ]

    for table in order:
        cols = cols_by_table[table]
        if not cols:
            continue
        out.append(f"-- ─── {table} " + "─" * max(0, 56 - len(table)))
        lines = []
        for c in cols:
            piece = f'  "{c["column_name"]}" {c["data_type"]}'
            if c["column_default"]:
                piece += f' DEFAULT {c["column_default"]}'
            if c["is_nullable"] == "NO":
                piece += " NOT NULL"
            lines.append(piece)
        out.append(f'CREATE TABLE IF NOT EXISTS "{table}" (')
        out.append(",\n".join(lines))
        out.append(");")
        out.append("")

    out.append("-- ─── Περιορισμοί " + "─" * 48)
    out.append("-- Τα PRIMARY KEY/UNIQUE δημιουργούνται εδώ ώστε η σειρά των πινάκων")
    out.append("-- να μην εμποδίζει τα foreign keys.")
    for table in order:
        for c in sorted(cons_by_table[table], key=lambda r: r["conname"]):
            out.append(
                f'DO $$ BEGIN ALTER TABLE "{table}" ADD CONSTRAINT "{c["conname"]}" '
                f'{c["definition"]};\n'
                f"  EXCEPTION WHEN duplicate_object THEN NULL;"
                f" WHEN duplicate_table THEN NULL; END $$;")
    out.append("")

    out.append("-- ─── Ευρετήρια " + "─" * 50)
    for table in order:
        for i in sorted(idx_by_table[table], key=lambda r: r["indexname"]):
            definition = i["indexdef"]
            # Τα ευρετήρια των PK/UNIQUE δημιουργούνται μαζί με τον περιορισμό.
            if any(c["conname"] == i["indexname"] for c in cons_by_table[table]):
                continue
            definition = definition.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ", 1)
            definition = definition.replace("CREATE UNIQUE INDEX ",
                                            "CREATE UNIQUE INDEX IF NOT EXISTS ", 1)
            out.append(definition + ";")
    out.append("")

    out.append("-- ─── Row Level Security " + "─" * 41)
    for table in order:
        if rls.get(table):
            out.append(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;')
    out.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out), encoding="utf-8")

    print(f"\n✅ {OUT}")
    print(f"   {len(snap['tables'])} πίνακες · {len(snap['constraints'])} περιορισμοί ·"
          f" {len(snap['indexes'])} ευρετήρια · RLS σε {sum(1 for v in rls.values() if v)}")
    print("\n⚠️  ΔΕΝ εφαρμόστηκε πουθενά. Έλεγξέ το πριν χρησιμοποιηθεί.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
