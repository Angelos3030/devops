#!/usr/bin/env python3
"""
Αποτύπωμα σχήματος — και σύγκριση περιβαλλόντων.

    python scripts/schema_snapshot.py --env production --out db/snapshots/production.json
    python scripts/schema_snapshot.py --env staging    --out db/snapshots/staging.json
    python scripts/schema_snapshot.py --diff db/snapshots/production.json db/snapshots/staging.json

Γιατί υπάρχει: βρέθηκαν ΔΥΟ ανεξάρτητα συστήματα migrations — τα versioned
αρχεία του repo (staging) και το ιστορικό του Supabase (παραγωγή). Το staging
είχε 27 πίνακες, η παραγωγή 12. Χωρίς μετρήσιμη σύγκριση, το «staging είναι
αντίγραφο της παραγωγής» ήταν ευχή.

Το ίδιο SQL τρέχει και στα δύο περιβάλλοντα ώστε τα αποτυπώματα να συγκρίνονται.
Η παραγωγή διαβάζεται ΜΟΝΟ μέσω Management API (read-only) — δεν υπάρχουν
production credentials τοπικά, εκ κατασκευής.

Χρησιμοποιείται και ως parity gate στο CI: μη μηδενική έξοδος σημαίνει απόκλιση.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

PROD_REF = "rmhgkwscchyjzjkxezuf"

# Ένα ερώτημα ανά κατηγορία. Ταξινομημένα ώστε το αποτύπωμα να είναι ντετερμινιστικό.
QUERIES = {
    "columns": """
        SELECT table_name, column_name, data_type, is_nullable,
               coalesce(column_default, '') AS column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, column_name
    """,
    "constraints": """
        SELECT c.conrelid::regclass::text AS table_name, c.conname,
               pg_get_constraintdef(c.oid) AS definition
        FROM pg_constraint c
        JOIN pg_namespace n ON n.oid = c.connamespace
        WHERE n.nspname = 'public'
        ORDER BY 1, 2
    """,
    "indexes": """
        SELECT tablename AS table_name, indexname, indexdef
        FROM pg_indexes WHERE schemaname = 'public'
        ORDER BY 1, 2
    """,
    # Οι functions δεν ήταν στο αποτύπωμα και το baseline βγήκε χωρίς αυτές.
    # Η παραγωγή έχει το claim_client_site() (RPC για το ownership των sites) —
    # καθαρό staging από το baseline θα έσπαγε στο claim χωρίς να το δείξει
    # καμία σύγκριση. Ό,τι δεν μετριέται, αποκλίνει.
    "functions": """
        SELECT p.proname AS table_name,
               pg_get_function_identity_arguments(p.oid) AS args,
               pg_get_functiondef(p.oid) AS definition
        FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = 'public' AND p.prokind IN ('f', 'p')
          -- Οι functions των extensions (pgcrypto, uuid-ossp) μπαίνουν στο public
          -- σε καθαρό Postgres αλλά σε ξεχωριστό schema στο Supabase. Δεν είναι
          -- δικό μας σχήμα — αν μετρηθούν, κάθε σύγκριση βγάζει ψεύτικες αποκλίσεις.
          AND NOT EXISTS (SELECT 1 FROM pg_depend d
                          WHERE d.objid = p.oid AND d.deptype = 'e')
        ORDER BY 1, 2
    """,
    "triggers": """
        SELECT c.relname AS table_name, t.tgname,
               pg_get_triggerdef(t.oid) AS definition
        FROM pg_trigger t
        JOIN pg_class c ON c.oid = t.tgrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND NOT t.tgisinternal
        ORDER BY 1, 2
    """,
    "rls": """
        SELECT c.relname AS table_name, c.relrowsecurity AS enabled
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r'
        ORDER BY 1
    """,
    "policies": """
        SELECT tablename AS table_name, policyname, cmd,
               coalesce(qual, '') AS using_expr, coalesce(with_check, '') AS check_expr
        FROM pg_policies WHERE schemaname = 'public'
        ORDER BY 1, 2
    """,
}


def _fetch_production(sql: str) -> list[dict]:
    import urllib.request
    token = os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
    if not token:
        sys.exit("⛔ Λείπει το SUPABASE_ACCESS_TOKEN για ανάγνωση παραγωγής.")
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PROD_REF}/database/query",
        method="POST", data=json.dumps({"query": sql}).encode(),
        # Χωρίς User-Agent το Cloudflare του Supabase απαντά 403 «error code 1010».
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "vitrina-schema/1.0"})
    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode() or "[]")


def _fetch_staging(sql: str, dsn_override: str = "") -> list[dict]:
    import psycopg2
    dsn = dsn_override or os.environ.get("DATABASE_URL_STAGING", "").strip()
    if not dsn:
        sys.exit("⛔ Λείπει το DATABASE_URL_STAGING.")
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def snapshot(where: str, dsn: str = "") -> dict:
    """`dsn` επιτρέπει αποτύπωμα οποιασδήποτε βάσης — π.χ. προσωρινού container
    στον οποίο εφαρμόστηκε το baseline, για να αποδειχθεί ότι το αναπαράγει."""
    fetch = (_fetch_production if where == "production"
             else (lambda sql: _fetch_staging(sql, dsn)))
    out: dict = {"env": where}
    for key, sql in QUERIES.items():
        rows = fetch(sql)
        # Το regclass μπορεί να επιστρέψει «public.x» ή «"x"» — κανονικοποιούμε
        # ώστε τα δύο περιβάλλοντα να συγκρίνονται σε ίσους όρους.
        for row in rows:
            if "table_name" in row and isinstance(row["table_name"], str):
                row["table_name"] = row["table_name"].split(".")[-1].strip('"')
        out[key] = rows
        print(f"  {key:12} {len(rows):>5} εγγραφές")
    out["tables"] = sorted({r["table_name"] for r in out["columns"]})
    return out


def _key(kind: str, row: dict) -> str:
    if kind == "columns":
        return f'{row["table_name"]}.{row["column_name"]}'
    if kind in ("constraints",):
        return f'{row["table_name"]}.{row["conname"]}'
    if kind == "indexes":
        return f'{row["table_name"]}.{row["indexname"]}'
    if kind == "functions":
        return f'{row["table_name"]}({row["args"]})'
    if kind == "triggers":
        return f'{row["table_name"]}.{row["tgname"]}'
    if kind == "policies":
        return f'{row["table_name"]}.{row["policyname"]}'
    return row["table_name"]


def diff(a: dict, b: dict) -> int:
    name_a, name_b = a.get("env", "A"), b.get("env", "B")
    print("=" * 68)
    print(f"ΣΥΓΚΡΙΣΗ  {name_a}  ↔  {name_b}")
    print("=" * 68)

    only_a = sorted(set(a["tables"]) - set(b["tables"]))
    only_b = sorted(set(b["tables"]) - set(a["tables"]))
    print(f"\nΠίνακες: {name_a} {len(a['tables'])}   {name_b} {len(b['tables'])}")
    if only_a:
        print(f"\n  Μόνο στο {name_a}:")
        for t in only_a:
            print(f"    · {t}")
    if only_b:
        print(f"\n  Μόνο στο {name_b}:")
        for t in only_b:
            print(f"    · {t}")

    differences = len(only_a) + len(only_b)
    shared = set(a["tables"]) & set(b["tables"])

    for kind in ("columns", "constraints", "indexes", "policies", "triggers", "functions"):
        if kind not in a or kind not in b:
            continue  # παλιό αποτύπωμα, πριν μπουν functions/triggers
        # Μόνο για κοινούς πίνακες — αλλιώς επαναλαμβάνουμε ό,τι είπαμε παραπάνω.
        # Οι functions δεν ανήκουν σε πίνακα, οπότε συγκρίνονται όλες.
        keep = (lambda r: True) if kind == "functions" else (lambda r: r["table_name"] in shared)
        ma = {_key(kind, r): r for r in a[kind] if keep(r)}
        mb = {_key(kind, r): r for r in b[kind] if keep(r)}
        missing = sorted(set(ma) - set(mb))
        extra = sorted(set(mb) - set(ma))
        changed = sorted(k for k in set(ma) & set(mb) if ma[k] != mb[k])
        if not (missing or extra or changed):
            continue
        print(f"\n[{kind}] σε κοινούς πίνακες")
        for k in missing:
            print(f"    − λείπει από {name_b}: {k}")
        for k in extra:
            print(f"    + μόνο στο {name_b}: {k}")
        for k in changed:
            print(f"    ≠ διαφέρει: {k}")
        differences += len(missing) + len(extra) + len(changed)

    rls_a = {r["table_name"]: r["enabled"] for r in a["rls"]}
    rls_b = {r["table_name"]: r["enabled"] for r in b["rls"]}
    rls_diff = [t for t in sorted(shared) if rls_a.get(t) != rls_b.get(t)]
    if rls_diff:
        print("\n[RLS] διαφορετική κατάσταση")
        for t in rls_diff:
            print(f"    ≠ {t}: {name_a}={rls_a.get(t)}  {name_b}={rls_b.get(t)}")
        differences += len(rls_diff)

    print("\n" + "=" * 68)
    if differences:
        print(f"❌ {differences} αποκλίσεις")
        return 1
    print("✅ Τα σχήματα ταυτίζονται")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", choices=["production", "staging"])
    ap.add_argument("--out", default="")
    ap.add_argument("--diff", nargs=2, metavar=("A", "B"))
    ap.add_argument("--dsn", default="", help="αποτύπωμα αυθαίρετης βάσης")
    args = ap.parse_args()

    if args.diff:
        a = json.loads(Path(args.diff[0]).read_text(encoding="utf-8"))
        b = json.loads(Path(args.diff[1]).read_text(encoding="utf-8"))
        return diff(a, b)

    if not args.env:
        print("Χρήση: --env production|staging [--out ΑΡΧΕΙΟ]  |  --diff A B")
        return 0

    print(f"\nΑποτύπωμα «{args.env}»")
    snap = snapshot(args.env, args.dsn)
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snap, ensure_ascii=False, indent=1, default=str),
                        encoding="utf-8")
        print(f"\n✅ {len(snap['tables'])} πίνακες → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
