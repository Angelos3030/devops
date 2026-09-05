#!/usr/bin/env python3
"""
Migrations runner — μία βάση, μία σειρά, μία καταγραφή.

    python scripts/migrate.py --status                       # τι έχει τρέξει
    VITRINA_ENV=staging    python scripts/migrate.py --apply
    VITRINA_ENV=production python scripts/migrate.py --apply --confirm-production

Γιατί υπάρχει: τα SQL έτρεχαν χειροκίνητα στο Supabase SQL Editor, χωρίς σειρά
και χωρίς καταγραφή. Δεν μπορούσε να στηθεί δεύτερη βάση με βεβαιότητα ότι
είναι ίδια — άρα το staging δεν θα ήταν αντίγραφο, θα ήταν εικασία.

ΚΑΝΟΝΑΣ ΣΧΗΜΑΤΟΣ: μόνο προσθετικές αλλαγές ανά έκδοση. Για καταστροφική αλλαγή
(μετονομασία/διαγραφή στήλης) ακολουθούμε expand → migrate data → contract σε
ΞΕΧΩΡΙΣΤΑ releases:

    release N     0007_add_new_column.sql        (expand — γράφουν και τα δύο)
    release N+1   0008_backfill_new_column.sql   (migrate data)
    release N+2   0009_drop_old_column.sql       (contract — αφού ο παλιός
                                                  κώδικας δεν τρέχει πουθενά)

Έτσι το rollback του κώδικα είναι πάντα ασφαλές: η παλιά έκδοση βρίσκει το
σχήμα που περιμένει.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import env  # noqa: E402

MIGRATIONS = Path("db/migrations")
NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")

TRACKING = """
CREATE TABLE IF NOT EXISTS schema_migrations (
  version     text PRIMARY KEY,
  filename    text NOT NULL,
  checksum    text NOT NULL,
  applied_at  timestamptz NOT NULL DEFAULT now()
);
"""


def _dsn() -> str:
    """Postgres connection string του τρέχοντος περιβάλλοντος.

    Χωριστό όνομα ανά περιβάλλον, όπως και τα υπόλοιπα credentials — ώστε ένα
    λάθος flag να μη βρίσκει καν στοιχεία σύνδεσης για την παραγωγή."""
    suffix = "PRODUCTION" if env.is_production else "STAGING"
    dsn = os.environ.get(f"DATABASE_URL_{suffix}", "").strip()
    if not dsn:
        sys.exit(
            f"⛔ Λείπει το DATABASE_URL_{suffix}.\n"
            f"   Supabase → Project Settings → Database → Connection string (URI).\n"
            f"   {env.banner()}"
        )
    return dsn


def _env_scope(path: Path) -> str:
    """«-- ENV: staging-only» στην κορυφή = δεν φτάνει ποτέ στην παραγωγή.

    Ο Agency Kernel υπάρχει στην ακολουθία αλλά δεν έχει ολοκληρωθεί. Χωρίς
    αυτή τη σήμανση θα έμπαινε στην παραγωγή με το επόμενο --apply.
    """
    first = path.read_text(encoding="utf-8")[:200]
    return "staging-only" if "-- ENV: staging-only" in first else "all"


def _files() -> list[Path]:
    if not MIGRATIONS.is_dir():
        sys.exit(f"⛔ Δεν βρέθηκε ο φάκελος {MIGRATIONS}")
    out = []
    # Το legacy/ είναι ιστορικό, όχι εκτελέσιμο — δεν διαβάζεται ποτέ.
    for path in sorted(MIGRATIONS.iterdir()):
        if path.suffix != ".sql" or path.is_dir():
            continue
        if not NAME_RE.match(path.name):
            sys.exit(f"⛔ Λάθος όνομα: {path.name}\n   Μορφή: 0007_short_description.sql")
        out.append(path)
    versions = [NAME_RE.match(p.name).group(1) for p in out]
    if len(set(versions)) != len(versions):
        sys.exit("⛔ Διπλός αριθμός έκδοσης στο db/migrations/")
    return out


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ── Υιοθέτηση baseline ──────────────────────────────────────────────────────
#
# ΤΟ ΠΡΟΒΛΗΜΑ. Μια βάση που υπάρχει από πριν το migration system έχει ήδη τα
# αντικείμενα του 0000, αλλά δεν έχει `schema_migrations`. Το πρώτο `--apply`
# θα εκτελούσε το 0000 — και θα έσκαγε:
#
#     ✗ multiple primary keys for table "clients" are not allowed
#
# Το 0000 τυλίγει κάθε περιορισμό σε `EXCEPTION WHEN duplicate_object`, αλλά η
# PostgreSQL ελέγχει «δεύτερο primary key» ΠΡΙΝ τη σύγκρουση ονόματος και
# ρίχνει `invalid_table_definition` (42P16). Ο handler δεν ενεργοποιείται ποτέ.
#
# Η ΛΥΣΗ ΔΕΝ ΕΙΝΑΙ να πειραχτεί το 0000 — είναι να μπορεί κανείς να ΔΗΛΩΣΕΙ
# ότι το baseline υπάρχει ήδη. Αλλά όχι στα τυφλά: πρώτα αποδεικνύεται.
#
# ΓΙΑΤΙ ΜΟΝΟ ΤΟ 0000. Η υιοθέτηση παρακάμπτει εκτέλεση SQL. Αν επιτρεπόταν για
# οποιοδήποτε migration, θα ήταν εργαλείο για να «περάσει» ένα migration που
# δεν έτρεξε ποτέ — δηλαδή σιωπηλή απόκλιση σχήματος. Το baseline είναι η
# μοναδική περίπτωση όπου η βάση ΝΟΜΙΜΑ προϋπάρχει του συστήματος.
BASELINE_VERSION = "0000"
FINGERPRINT = Path("db/baseline_fingerprint.json")


def _adopt_baseline(conn, version: str, files: list[Path]) -> int:
    """Δηλώνει το baseline ως εφαρμοσμένο — ΜΟΝΟ αν η βάση το έχει όντως."""
    if version != BASELINE_VERSION:
        print(f"⛔ Υιοθέτηση επιτρέπεται ΜΟΝΟ για το {BASELINE_VERSION}.\n"
              f"   Ζητήθηκε: {version}. Κάθε άλλο migration πρέπει να ΤΡΕΞΕΙ.")
        return 1
    if not FINGERPRINT.exists():
        print(f"⛔ Λείπει το {FINGERPRINT}.\n"
              f"   Φτιάξ' το: python scripts/make_baseline_fingerprint.py")
        return 1

    fp = json.loads(FINGERPRINT.read_text(encoding="utf-8"))
    path = next((p for p in files if NAME_RE.match(p.name).group(1) == version), None)
    if path is None:
        print(f"⛔ Δεν βρέθηκε αρχείο για την έκδοση {version}.")
        return 1
    checksum = _checksum(path)
    if fp.get("source_checksum") != checksum:
        print(f"⛔ Το αποτύπωμα δεν αντιστοιχεί στο σημερινό {path.name}.\n"
              f"   αποτύπωμα={fp.get('source_checksum')}  αρχείο={checksum}\n"
              f"   Ξαναφτιάξ' το: python scripts/make_baseline_fingerprint.py")
        return 1

    # ── Κατάσταση ιστορικού ────────────────────────────────────────────────
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.schema_migrations')")
        tracking_exists = cur.fetchone()[0] is not None
        recorded: dict[str, str] = {}
        if tracking_exists:
            cur.execute("SELECT version, checksum FROM schema_migrations")
            recorded = dict(cur.fetchall())
    if version in recorded:
        print(f"⛔ Το {version} είναι ΗΔΗ καταγεγραμμένο "
              f"(checksum {recorded[version]}). Δεν υιοθετείται δεύτερη φορά.")
        return 1
    if recorded:
        print(f"⛔ Το `schema_migrations` έχει ήδη {len(recorded)} εγγραφές "
              f"({', '.join(sorted(recorded))}) χωρίς το baseline.\n"
              "   Αυτό δεν είναι βάση που περιμένει υιοθέτηση — είναι βάση σε\n"
              "   ασυνεπή κατάσταση. Χρειάζεται άνθρωπος, όχι αυτόματο βήμα.")
        return 1

    # ── Επαλήθευση αποτυπώματος ────────────────────────────────────────────
    missing: list[str] = []
    with conn.cursor() as cur:
        cur.execute("""SELECT table_name||'.'||column_name,
                              data_type||'|'||is_nullable
                       FROM information_schema.columns WHERE table_schema='public'""")
        have_cols = dict(cur.fetchall())
        cur.execute("""SELECT rel.relname||':'||con.conname,
                              con.contype::text, pg_get_constraintdef(con.oid)
                       FROM pg_constraint con
                       JOIN pg_class rel ON rel.oid=con.conrelid
                       JOIN pg_namespace n ON n.oid=rel.relnamespace
                       WHERE n.nspname='public' AND con.contype IN ('p','u','f')""")
        have_cons = {k: (t, d) for k, t, d in cur.fetchall()}

    have_tables = {k.split(".")[0] for k in have_cols}
    for table in fp["tables"]:
        if table not in have_tables:
            missing.append(f"πίνακας {table}")
    for key, want in fp["columns"].items():
        if key.split(".")[0] not in have_tables:
            continue                      # ήδη αναφέρθηκε ως πίνακας που λείπει
        got = have_cols.get(key)
        if got is None:
            missing.append(f"στήλη {key}")
        elif got != want:
            missing.append(f"στήλη {key}: βρέθηκε {got}, απαιτείται {want}")
    for label, group in (("primary key", "primary_keys"),
                         ("unique", "unique_constraints"),
                         ("foreign key", "foreign_keys")):
        for key, want in fp[group].items():
            got = have_cons.get(key)
            if got is None:
                missing.append(f"{label} {key}")
            elif got[1] != want:
                missing.append(f"{label} {key}: βρέθηκε «{got[1]}», "
                               f"απαιτείται «{want}»")

    if missing:
        print(f"⛔ Η βάση ΔΕΝ έχει το baseline {version}. "
              f"{len(missing)} απαιτήσεις δεν ικανοποιούνται:\n")
        for m in missing[:25]:
            print(f"   · {m}")
        if len(missing) > 25:
            print(f"   … και άλλες {len(missing) - 25}")
        print("\n   ΔΕΝ γράφτηκε τίποτα. Η υιοθέτηση σταματά κλειστά.")
        return 1

    # ── Καταγραφή, ΜΟΝΟ τώρα ───────────────────────────────────────────────
    with conn.cursor() as cur:
        cur.execute(TRACKING)
        cur.execute(
            "INSERT INTO schema_migrations (version, filename, checksum) "
            "VALUES (%s, %s, %s)", (version, path.name, checksum))
    conn.commit()

    extra_tables = sorted(have_tables - set(fp["tables"]))
    print(f"✅ Υιοθετήθηκε το baseline {version} — ΧΩΡΙΣ εκτέλεση SQL.\n")
    print(f"   αρχείο            {path.name}")
    print(f"   checksum          {checksum}")
    print(f"   επαληθεύτηκαν     {len(fp['tables'])} πίνακες, "
          f"{len(fp['columns'])} στήλες, {len(fp['primary_keys'])} PK, "
          f"{len(fp['unique_constraints'])} unique, "
          f"{len(fp['foreign_keys'])} FK")
    if extra_tables:
        print(f"   επιπλέον στη βάση {', '.join(extra_tables)}  (αποδεκτό)")
    print(f"\n   Επόμενο βήμα:  python scripts/migrate.py --status")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="τι έχει τρέξει (default)")
    ap.add_argument("--apply", action="store_true", help="εφάρμοσε ό,τι λείπει")
    ap.add_argument("--confirm-production", action="store_true",
                    help="απαιτείται για --apply στην παραγωγή")
    ap.add_argument("--adopt-baseline", metavar="ΕΚΔΟΣΗ",
                    help="δήλωσε ότι η βάση ΕΧΕΙ ΗΔΗ το baseline, χωρίς να "
                         "τρέξει το SQL του (μόνο για το 0000, με επαλήθευση)")
    ap.add_argument("--accept-checksum", nargs="+", metavar="ΕΚΔΟΣΗ",
                    help="κατέγραψε το νέο checksum για ήδη εφαρμοσμένο "
                         "migration που διορθώθηκε (ΔΕΝ τρέχει το SQL)")
    args = ap.parse_args()

    env.print_banner()

    if args.apply and env.is_production and not args.confirm_production:
        sys.exit("⛔ Migration στην ΠΑΡΑΓΩΓΗ χωρίς επιβεβαίωση.\n"
                 "   Πρόσθεσε --confirm-production. Και τρέξ' το πρώτα σε staging.")

    try:
        import psycopg2
    except ImportError:
        sys.exit("⛔ Λείπει το psycopg2. pip install psycopg2-binary")

    files = _files()
    conn = psycopg2.connect(_dsn())
    conn.autocommit = False
    try:
        if args.adopt_baseline:
            # ΠΡΙΝ από το `CREATE TABLE schema_migrations`: η υιοθέτηση φτιάχνει
            # τον πίνακα ΜΟΝΟ αφού περάσει η επαλήθευση. Αλλιώς μια αποτυχημένη
            # προσπάθεια θα άφηνε πίσω της άδειο ιστορικό, που μοιάζει με
            # «βάση υπό διαχείριση» ενώ δεν είναι.
            return _adopt_baseline(conn, args.adopt_baseline, files)

        with conn.cursor() as cur:
            cur.execute(TRACKING)
            conn.commit()
            cur.execute("SELECT version, checksum FROM schema_migrations")
            done = dict(cur.fetchall())

        print(f"\n{len(files)} migrations στο δίσκο, {len(done)} εφαρμοσμένα\n")
        pending = []
        drifted: list[tuple[str, str, str, str]] = []
        for path in files:
            version = NAME_RE.match(path.name).group(1)
            checksum = _checksum(path)
            if _env_scope(path) == "staging-only" and env.is_production:
                print(f"  ⊘ {path.name}  (staging-only — δεν αφορά την παραγωγή)")
                continue
            if version in done:
                changed = done[version] != checksum
                mark = "⚠️  ΑΛΛΑΞΕ" if changed else "✓"
                print(f"  {mark} {path.name}")
                if changed:
                    drifted.append((version, path.name, done[version], checksum))
                    print(f"      Το αρχείο άλλαξε μετά την εφαρμογή. Τα migrations είναι")
                    print(f"      αμετάβλητα — φτιάξε ΝΕΟ αρχείο αντί να πειράξεις αυτό.")
                    print(f"      καταγεγραμμένο={done[version]}  τώρα={checksum}")
            else:
                print(f"  · {path.name}  (εκκρεμεί)")
                pending.append((version, path, checksum))

        # ── Συμφιλίωση checksum ────────────────────────────────────────────
        #
        # ΓΙΑΤΙ ΥΠΑΡΧΕΙ. Ένα migration ΔΕΝ πρέπει να αλλάζει μετά την εφαρμογή
        # του. Μία φορά όμως συνέβη και έπρεπε να διορθωθεί: το 0004 ανέφερε
        # στήλη που το ξαναγραμμένο 0003 δεν δημιουργούσε πια, οπότε κάθε
        # καθαρή εγκατάσταση — και η παραγωγή — σταματούσε εκεί.
        #
        # Χωρίς αυτή την εντολή, η προειδοποίηση μένει για πάντα και μαθαίνει
        # τον κόσμο να αγνοεί προειδοποιήσεις. Με αυτήν, η αποδοχή είναι
        # ΡΗΤΗ, ανά έκδοση, και απαιτεί να έχει αποδειχθεί ισοδυναμία.
        #
        # ΔΕΝ τρέχει το SQL. Ενημερώνει ΜΟΝΟ την εγγραφή — γι' αυτό επιτρέπεται
        # μόνο αφού κάποιος έχει δείξει ότι η βάση είναι ήδη στην κατάσταση
        # που θα παρήγαγε το διορθωμένο αρχείο.
        if args.accept_checksum:
            wanted = set(args.accept_checksum)
            index = {v: (f, old, new) for v, f, old, new in drifted}
            unknown = wanted - set(index)
            if unknown:
                print(f"\n⛔ Δεν υπάρχει απόκλιση για: {', '.join(sorted(unknown))}")
                return 1
            print()
            with conn.cursor() as cur:
                for version in sorted(wanted):
                    filename, old, new = index[version]
                    cur.execute(
                        "UPDATE schema_migrations SET checksum=%s WHERE version=%s",
                        (new, version))
                    print(f"  ✓ {filename}: {old} → {new}")
                conn.commit()
            print(f"\n✅ Συμφιλιώθηκαν {len(wanted)}. Το SQL ΔΕΝ ξανατρέχθηκε.")
            return 0

        if not pending:
            if drifted:
                print("\n⚠️  Η βάση είναι ενημερωμένη, αλλά "
                      f"{len(drifted)} αρχείο(α) έχουν αλλάξει μετά την εφαρμογή.")
                print("   Αν έχει αποδειχθεί ότι η βάση είναι ήδη στην κατάσταση")
                print("   που παράγει το διορθωμένο αρχείο:")
                print("     python scripts/migrate.py --accept-checksum "
                      + " ".join(v for v, *_ in drifted))
                return 0
            print("\n✅ Η βάση είναι ενημερωμένη.")
            return 0
        if not args.apply:
            print(f"\n{len(pending)} εκκρεμούν. Για εφαρμογή:  --apply")
            return 0

        print()
        for version, path, checksum in pending:
            sql = path.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                try:
                    cur.execute(sql)
                    cur.execute(
                        "INSERT INTO schema_migrations (version, filename, checksum) "
                        "VALUES (%s, %s, %s)", (version, path.name, checksum))
                    conn.commit()
                    print(f"  ✓ {path.name}")
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    print(f"  ✗ {path.name}\n      {e}")
                    print("\n⛔ Σταμάτησα. Οι επόμενες δεν έτρεξαν.")
                    return 1
        print(f"\n✅ Εφαρμόστηκαν {len(pending)}.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
