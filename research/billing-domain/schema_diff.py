"""Σύγκριση σχήματος: ΚΑΘΑΡΗ βάση από migrations vs STAGING.

Συγκρίνει ό,τι μπορεί να αποκλίνει σιωπηλά: στήλες, περιορισμούς, index,
συναρτήσεις (ΚΑΙ το σώμα τους), RLS και δικαιώματα.

Χρήση:
  python research/billing-domain/schema_diff.py <dsn-καθαρής>
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()
HERE = pathlib.Path(__file__).resolve().parent

FRESH = sys.argv[1] if len(sys.argv) > 1 else \
    "postgresql://postgres:migtest@127.0.0.1:55432/vitrina"
STAGING = os.environ["DATABASE_URL_STAGING"]

# Ο editor είναι το επίμαχο υποσύνολο, αλλά κοιτάμε και τα domain_orders του 0006.
TABLES = ("site_revisions", "site_content", "domain_orders")
FUNCS = ("editor_commit", "editor_undo")

Q = {
    "στήλες": """
        SELECT table_name, column_name, data_type, is_nullable,
               COALESCE(column_default,'')
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name = ANY(%s)
        ORDER BY 1,2""",
    "περιορισμοί": """
        SELECT rel.relname, con.conname, pg_get_constraintdef(con.oid)
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_namespace n ON n.oid = rel.relnamespace
        WHERE n.nspname='public' AND rel.relname = ANY(%s)
        ORDER BY 1,2""",
    "index": """
        SELECT tablename, indexname, indexdef
        FROM pg_indexes
        WHERE schemaname='public' AND tablename = ANY(%s)
        ORDER BY 1,2""",
    "RLS": """
        SELECT rel.relname, rel.relrowsecurity, rel.relforcerowsecurity
        FROM pg_class rel JOIN pg_namespace n ON n.oid=rel.relnamespace
        WHERE n.nspname='public' AND rel.relname = ANY(%s)
        ORDER BY 1""",
    "policies": """
        SELECT tablename, policyname, permissive, roles::text, cmd,
               COALESCE(qual,''), COALESCE(with_check,'')
        FROM pg_policies WHERE schemaname='public' AND tablename = ANY(%s)
        ORDER BY 1,2""",
    "δικαιώματα πινάκων": """
        SELECT table_name, grantee, privilege_type
        FROM information_schema.role_table_grants
        WHERE table_schema='public' AND table_name = ANY(%s)
        ORDER BY 1,2,3""",
}


def fetch(dsn: str, sql: str, params) -> list[tuple]:
    c = psycopg2.connect(dsn)
    try:
        with c.cursor() as cur:
            cur.execute(sql, params)
            return [tuple(str(x) for x in row) for row in cur.fetchall()]
    finally:
        c.close()


def funcs(dsn: str) -> dict[str, str]:
    """Ονόματα + ΚΑΝΟΝΙΚΟΠΟΙΗΜΕΝΟ σώμα. Το σώμα είναι που κρύβει τα σφάλματα:
    δύο βάσεις μπορεί να έχουν την ίδια υπογραφή και άλλη λογική."""
    c = psycopg2.connect(dsn)
    try:
        with c.cursor() as cur:
            cur.execute("""
                SELECT p.proname, pg_get_function_identity_arguments(p.oid),
                       pg_get_functiondef(p.oid)
                FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
                WHERE n.nspname='public' AND p.proname = ANY(%s)
                ORDER BY 1,2""", (list(FUNCS),))
            out = {}
            for name, args, body in cur.fetchall():
                norm = " ".join(body.split())
                out[f"{name}({args})"] = hashlib.sha256(
                    norm.encode()).hexdigest()[:16]
            return out
    finally:
        c.close()


def func_grants(dsn: str) -> list[tuple]:
    c = psycopg2.connect(dsn)
    try:
        with c.cursor() as cur:
            cur.execute("""
                SELECT p.proname, r.rolname,
                       has_function_privilege(r.rolname, p.oid, 'EXECUTE')
                FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
                CROSS JOIN (SELECT rolname FROM pg_roles
                            WHERE rolname IN ('anon','authenticated',
                                              'service_role','PUBLIC')) r
                WHERE n.nspname='public' AND p.proname = ANY(%s)
                ORDER BY 1,2""", (list(FUNCS),))
            return [tuple(str(x) for x in row) for row in cur.fetchall()]
    finally:
        c.close()


print(f"  ΚΑΘΑΡΗ : {FRESH.split('@')[-1]}")
print(f"  STAGING: {STAGING.split('@')[-1].split('/')[0]}\n")

diffs: dict[str, dict] = {}
for label, sql in Q.items():
    a = fetch(FRESH, sql, (list(TABLES),))
    b = fetch(STAGING, sql, (list(TABLES),))
    only_fresh = [r for r in a if r not in b]
    only_stg = [r for r in b if r not in a]
    ok = not only_fresh and not only_stg
    print(f"  {'✓' if ok else '✗'} {label:<22}"
          f"καθαρή={len(a):<4} staging={len(b):<4}"
          f"{'' if ok else f'  ΔΙΑΦΟΡΕΣ: +{len(only_fresh)} / -{len(only_stg)}'}")
    if not ok:
        diffs[label] = {"μόνο_στην_καθαρή": only_fresh, "μόνο_στο_staging": only_stg}
        for r in only_fresh[:6]:
            print(f"       + καθαρή : {r}")
        for r in only_stg[:6]:
            print(f"       - staging: {r}")

fa, fb = funcs(FRESH), funcs(STAGING)
same = fa == fb
print(f"  {'✓' if same else '✗'} {'συναρτήσεις (σώμα)':<22}"
      f"καθαρή={len(fa):<4} staging={len(fb):<4}")
for k in sorted(set(fa) | set(fb)):
    if fa.get(k) != fb.get(k):
        print(f"       ! {k}: καθαρή={fa.get(k)} staging={fb.get(k)}")
        diffs.setdefault("συναρτήσεις", {})[k] = {"καθαρή": fa.get(k),
                                                  "staging": fb.get(k)}

ga, gb = func_grants(FRESH), func_grants(STAGING)
gsame = ga == gb
print(f"  {'✓' if gsame else '✗'} {'δικαιώματα συναρτ.':<22}"
      f"καθαρή={len(ga):<4} staging={len(gb):<4}")
if not gsame:
    for r in [x for x in ga if x not in gb][:8]:
        print(f"       + καθαρή : {r}")
    for r in [x for x in gb if x not in ga][:8]:
        print(f"       - staging: {r}")
    diffs["δικαιώματα_συναρτήσεων"] = {
        "μόνο_στην_καθαρή": [x for x in ga if x not in gb],
        "μόνο_στο_staging": [x for x in gb if x not in ga]}

import json
(HERE / "schema_diff.json").write_text(
    json.dumps(diffs, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  {'ΤΑΥΤΟΣΗΜΑ' if not diffs else f'{len(diffs)} κατηγορίες με διαφορές'}")
sys.exit(0 if not diffs else 1)
