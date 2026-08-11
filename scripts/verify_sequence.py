#!/usr/bin/env python3
"""
Αποδεικνύει ότι η canonical ακολουθία παράγει το σχήμα που περιμένουμε.

    python scripts/verify_sequence.py

Οι έλεγχοι τρέχουν σε καθαρή βάση (container), πριν αγγίξουμε οτιδήποτε αληθινό:

  1. Baseline parity     — μόνο το 0000 αναπαράγει ΑΚΡΙΒΩΣ την παραγωγή
  2. Πλήρες replay       — 0000 + 0001 τρέχουν χωρίς σφάλμα
  3. Αναμενόμενο σχήμα   — το τελικό ταιριάζει με το staging, εκτός από τα
                           ρητά αποσυρμένα (site_variants, clients.selected_layout,
                           schema_migrations) που ΔΕΝ πρέπει να ξαναεμφανιστούν
  4. Λειτουργίες         — design persistence, claims RPC, append-only evidence
  5. Καθαρισμός          — ο container σβήνει πάντα
  6. Καμία αναφορά       — μηδέν runtime χρήση των αποσυρμένων

Ο container σβήνεται πάντα. Τίποτα δεν γράφεται σε staging ή παραγωγή.
"""
from __future__ import annotations

import json
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from scripts.schema_snapshot import diff, snapshot  # noqa: E402

MIGRATIONS = Path("db/migrations")
# Αποσύρθηκαν συνειδητά: ο κώδικας αποθηκεύει designs στον πίνακα `sites`.
WITHDRAWN_TABLES = {"site_variants"}
WITHDRAWN_COLUMNS = {"clients.selected_layout"}
# Ο πίνακας του runner — δεν είναι μέρος του σχήματος εφαρμογής.
INTERNAL_TABLES = {"schema_migrations"}

ok, bad = [], []


def check(good: bool, label: str, detail: str = "") -> None:
    (ok if good else bad).append(label)
    print(f"  {'✓' if good else '✗'} {label}{f'  — {detail}' if detail else ''}")


def _postgres():
    import psycopg2
    name = f"vitrina-seq-{secrets.token_hex(4)}"
    port = 55000 + secrets.randbelow(2000)
    pw = secrets.token_hex(12)
    subprocess.run(["docker", "run", "-d", "--rm", "--name", name,
                    "-e", f"POSTGRES_PASSWORD={pw}", "-p", f"{port}:5432",
                    "postgres:16-alpine"], capture_output=True, check=True, timeout=600)
    dsn = f"postgresql://postgres:{pw}@127.0.0.1:{port}/postgres"
    for _ in range(45):
        try:
            psycopg2.connect(dsn, connect_timeout=3).close()
            return dsn, name
        except Exception:  # noqa: BLE001
            time.sleep(1.5)
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=60)
    sys.exit("⛔ Ο Postgres δεν σηκώθηκε.")


def main() -> int:
    files = sorted(p for p in MIGRATIONS.iterdir()
                   if p.suffix == ".sql" and re.match(r"^\d{4}_", p.name))
    print("=" * 68)
    print("ΕΠΑΛΗΘΕΥΣΗ CANONICAL ΑΚΟΛΟΥΘΙΑΣ")
    print("=" * 68)
    print("\nΑκολουθία:")
    for f in files:
        scope = "staging-only" if "-- ENV: staging-only" in f.read_text(encoding="utf-8")[:200] else "όλα"
        print(f"  {f.name}  [{scope}]")

    import psycopg2
    dsn, container = _postgres()
    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True

        # ---- 1. Baseline parity ---------------------------------------
        print("\n[1] Baseline ↔ παραγωγή")
        with conn.cursor() as cur:
            cur.execute(files[0].read_text(encoding="utf-8"))
        base = snapshot("staging", dsn)
        base["env"] = "baseline"
        prod = json.loads(Path("db/snapshots/production.json").read_text(encoding="utf-8"))
        check(diff(prod, base) == 0, "το 0000 αναπαράγει ακριβώς την παραγωγή")

        # ---- 2. Πλήρες replay ------------------------------------------
        print("\n[2] Υπόλοιπα migrations")
        for path in files[1:]:
            try:
                with conn.cursor() as cur:
                    cur.execute(path.read_text(encoding="utf-8"))
                check(True, path.name)
            except Exception as e:  # noqa: BLE001
                check(False, path.name, str(e).splitlines()[0][:70])

        # ---- 3. Αναμενόμενο τελικό σχήμα -------------------------------
        print("\n[3] Τελικό σχήμα ↔ staging")
        final = snapshot("staging", dsn)
        final["env"] = "canonical"
        stg = json.loads(Path("db/snapshots/staging.json").read_text(encoding="utf-8"))

        missing = (set(stg["tables"]) - set(final["tables"])
                   - WITHDRAWN_TABLES - INTERNAL_TABLES)
        extra = set(final["tables"]) - set(stg["tables"])
        check(not missing, "κανένας πίνακας του staging δεν χάθηκε",
              ", ".join(sorted(missing)))
        check(not extra, "κανένας απροσδόκητος πίνακας", ", ".join(sorted(extra)))

        gone = WITHDRAWN_TABLES & set(final["tables"])
        check(not gone, "τα αποσυρμένα ΔΕΝ ξαναεμφανίζονται", ", ".join(sorted(gone)))
        cols = {f'{r["table_name"]}.{r["column_name"]}' for r in final["columns"]}
        back = WITHDRAWN_COLUMNS & cols
        check(not back, "καμία αποσυρμένη στήλη", ", ".join(sorted(back)))

        # ---- 4. Τα τρία που πρέπει να δουλεύουν στη νέα βάση ------------
        # Παρουσία σχήματος δεν είναι λειτουργία, αλλά η απουσία της είναι
        # βέβαιη αποτυχία — και ακριβώς αυτό είχε ξεφύγει με τις functions.
        print("\n[4] Design persistence · claims · Agency Kernel")

        # Design persistence: ο κώδικας γράφει τα variants στον `sites`.
        need = {"sites.client_id", "sites.preset", "sites.html",
                "sites.chosen_variant", "sites.url"}
        check(need <= cols, "ο `sites` κρατά τα designs (preset/html/chosen_variant/url)",
              ", ".join(sorted(need - cols)))

        # Claims: πίνακας ΚΑΙ η RPC που κάνει το claim atomic.
        check("client_site_claims" in final["tables"], "υπάρχει ο client_site_claims")
        fns = {r["table_name"] for r in final["functions"]}
        check("claim_client_site" in fns, "υπάρχει η RPC claim_client_site()")

        # Agency Kernel: τα evidence tables δεν αρκεί να υπάρχουν — πρέπει να
        # είναι append-only, αλλιώς το audit log δεν αποδεικνύει τίποτα.
        kernel = {"agent_registry", "agent_tasks", "agent_runs", "agent_approvals",
                  "agency_events", "agency_audit_log", "agency_action_queue"}
        check(kernel <= set(final["tables"]), "οι πίνακες του Agency Kernel",
              ", ".join(sorted(kernel - set(final["tables"]))))
        trg = {f'{r["table_name"]}.{r["tgname"]}' for r in final["triggers"]}
        need_trg = {"agency_events.agency_events_append_only",
                    "agency_audit_log.agency_audit_log_append_only"}
        check(need_trg <= trg, "τα evidence tables είναι append-only",
              ", ".join(sorted(need_trg - trg)))

        # Το append-only πρέπει να ΑΠΟΡΡΙΠΤΕΙ, όχι απλώς να υπάρχει.
        with conn.cursor() as cur:
            cur.execute("INSERT INTO agency_events "
                        "(event_type, actor_type, actor_id, trace_id) "
                        "VALUES ('verify_sequence', 'system', 'verify', 'verify') "
                        "RETURNING id")
            event_id = cur.fetchone()[0]
        blocked = False
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE agency_events SET event_type = 'tampered' "
                            "WHERE id = %s", (event_id,))
        except Exception:  # noqa: BLE001
            blocked = True
        check(blocked, "UPDATE σε agency_events απορρίπτεται όντως")

        conn.close()
    finally:
        subprocess.run(["docker", "rm", "-f", container], capture_output=True, timeout=60)
        print(f"\n[5] {container} σβήστηκε")

    # ---- 6. Καμία αναφορά runtime --------------------------------------
    print("\n[6] Αναφορές στον κώδικα")
    sources = [p for p in Path("src").rglob("*.py")]
    sources += [p for p in Path("sites/lib").rglob("*.js")]
    sources += [p for p in Path("sites/app").rglob("*.jsx")]
    hits_table, hits_col = [], []
    for path in sources:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'table\(["\']site_variants["\']\)|FROM\s+site_variants', text, re.I):
            hits_table.append(str(path))
        if "selected_layout" in text:
            hits_col.append(str(path))
    check(not hits_table, "καμία αναφορά στον πίνακα site_variants", ", ".join(hits_table))
    check(not hits_col, "καμία αναφορά στο clients.selected_layout", ", ".join(hits_col))

    print("\n" + "=" * 68)
    print(f"ΠΕΡΑΣΑΝ: {len(ok)}   ΕΣΠΑΣΑΝ: {len(bad)}")
    if bad:
        print("\n❌ " + "\n   ".join(bad))
        return 1
    print("\n✅ Η canonical ακολουθία είναι έτοιμη. Το staging μπορεί να ξαναστηθεί.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
