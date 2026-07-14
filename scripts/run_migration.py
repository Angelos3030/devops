"""Run a .sql migration file against Supabase Postgres (direct connection).

Needs the DB connection string in .env as SUPABASE_DB_URL (kept out of chat/git):
  Supabase → Project Settings → Database → Connection string → URI
  (Session/pooler both fine; must include the password.)

Usage:
  python -m scripts.run_migration db/add_site_variants.sql
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m scripts.run_migration <path/to/file.sql>")
        return 2
    sql_path = ROOT / sys.argv[1]
    if not sql_path.exists():
        print(f"✗ file not found: {sql_path}")
        return 2

    try:
        import psycopg2
    except Exception:
        print("✗ Λείπει το psycopg2. Τρέξε: pip install psycopg2-binary")
        return 2

    candidates = _candidate_dsns()
    if not candidates:
        print("✗ Χρειάζεται ΕΝΑ από τα δύο στο .env:")
        print("  SUPABASE_DB_URL=<πλήρες connection string>   ή")
        print("  SUPABASE_DB_PASSWORD=<μόνο ο database password>  (χτίζω εγώ το URL)")
        return 2

    sql = sql_path.read_text(encoding="utf-8")
    last_err = None
    for label, dsn in candidates:
        print(f"→ Δοκιμή σύνδεσης ({label}) …")
        try:
            conn = psycopg2.connect(dsn, connect_timeout=12)
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.close()
            print(f"✓ Migration '{sql_path.name}' εφαρμόστηκε ({label}).")
            return 0
        except Exception as e:
            last_err = e
            print(f"  … απέτυχε: {str(e).splitlines()[0]}")
    print(f"✗ Δεν έγινε σύνδεση σε καμία διεύθυνση. Τελευταίο σφάλμα: {last_err}")
    return 1


def _project_ref() -> str:
    """Βγάζει το project ref από το SUPABASE_URL ή το service_role JWT."""
    url = os.environ.get("SUPABASE_URL", "")
    if "//" in url:
        host = url.split("//", 1)[1].split(".", 1)[0]
        if host:
            return host
    import base64
    import json
    key = os.environ.get("SUPABASE_KEY", "")
    try:
        p = key.split(".")[1]
        p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p)).get("ref", "")
    except Exception:
        return ""


def _candidate_dsns() -> list[tuple[str, str]]:
    full = os.environ.get("SUPABASE_DB_URL", "").strip()
    if full:
        return [("SUPABASE_DB_URL", full)]
    pw = os.environ.get("SUPABASE_DB_PASSWORD", "").strip()
    ref = _project_ref()
    if not (pw and ref):
        return []
    from urllib.parse import quote
    pwq = quote(pw, safe="")
    region = os.environ.get("SUPABASE_DB_REGION", "eu-central-1")
    out: list[tuple[str, str]] = []
    # Pooler (IPv4-friendly) — try session (5432) then transaction (6543), aws-0/aws-1
    for aws in ("aws-0", "aws-1"):
        for port in (5432, 6543):
            host = f"{aws}-{region}.pooler.supabase.com"
            out.append((f"pooler {aws}:{port}",
                        f"postgresql://postgres.{ref}:{pwq}@{host}:{port}/postgres"))
    # Direct connection (often IPv6-only)
    out.append(("direct :5432",
                f"postgresql://postgres:{pwq}@db.{ref}.supabase.co:5432/postgres"))
    return out


if __name__ == "__main__":
    raise SystemExit(main())
