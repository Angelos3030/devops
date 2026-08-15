#!/usr/bin/env python3
"""One-off, staging-only cleanup for the stray `public`-schema checkpoint
rows documented in ADR-0004 (`PostgresSaver` has no schema parameter — the
ADR-0002/0003 pilot runs, before the `search_path` fix landed, wrote their
checkpoint tables to `public` instead of an isolated schema).

Not run automatically — this is destructive (DELETE), so it goes through
`env.require_destructive()`: staging only, and requires an explicit
`--confirm-staging` flag. Nothing here can reach production (no
PRODUCTION_* credential is read anywhere in this file).

Identifies rows by `thread_id` prefix, not a blanket wipe of `public`:
only rows belonging to the known pilot thread_id patterns
(`tenant-*::lead-*`, `e2e-*`, `<uuid>::*`) from the checkpoint tables
(`checkpoints`, `checkpoint_blobs`, `checkpoint_writes`) are candidates,
and the script prints every matching row before deleting anything, with a
second explicit y/N prompt.

Usage (direct script path — this directory has a hyphen in its name, so it
is not importable via `python -m`, same convention as pg_spike.py):
    VITRINA_ENV=staging python research/langgraph-poc/lead-scoring/cleanup_stray_public_checkpoints.py --confirm-staging
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, ".")

from src import env  # noqa: E402

# Any thread_id matching one of these LIKE patterns in `public` is a known
# stray from the pre-search_path-fix pilot runs, not real production data
# (there is no production data for this workflow yet at all).
_STRAY_PATTERNS = ["tenant-%::%", "e2e-%", "%::e2e-%"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-staging", action="store_true")
    args = parser.parse_args()

    env.require_destructive(args.confirm_staging)
    env.print_banner()

    import psycopg2

    conn = psycopg2.connect(os.environ.get("DATABASE_URL_STAGING", ""))
    conn.autocommit = False
    cur = conn.cursor()

    total_found = 0
    for table in ("checkpoints", "checkpoint_blobs", "checkpoint_writes"):
        cur.execute(f"""
            SELECT DISTINCT thread_id FROM public.{table}
            WHERE thread_id LIKE ANY (%s)
        """, ([p for p in _STRAY_PATTERNS],))
        rows = cur.fetchall()
        print(f"{table}: {len(rows)} distinct stray thread_id(s)")
        for r in rows[:20]:
            print(f"  {r[0]}")
        total_found += len(rows)

    if total_found == 0:
        print("Nothing to clean up.")
        conn.close()
        return

    answer = input(f"\nDelete rows for these thread_id patterns from public.* checkpoint "
                    f"tables? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted, nothing deleted.")
        conn.close()
        return

    for table in ("checkpoint_writes", "checkpoint_blobs", "checkpoints"):
        cur.execute(f"DELETE FROM public.{table} WHERE thread_id LIKE ANY (%s)",
                    ([p for p in _STRAY_PATTERNS],))
        print(f"  deleted {cur.rowcount} rows from public.{table}")
    conn.commit()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
