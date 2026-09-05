"""Υιοθέτηση baseline: μια βάση που ΠΡΟΫΠΑΡΧΕΙ μπαίνει υπό διαχείριση.

ΤΟ ΠΡΟΒΛΗΜΑ. Η παραγωγή έχει τα αντικείμενα του 0000 αλλά όχι
`schema_migrations`. Το πρώτο `--apply` θα εκτελούσε το 0000 πάνω τους και θα
έσκαγε με «multiple primary keys for table clients» — το 0000 πιάνει
`duplicate_object`, ενώ η PostgreSQL ρίχνει `invalid_table_definition` (42P16).

Η λύση δεν είναι να πειραχτεί το 0000. Είναι να μπορεί κανείς να ΔΗΛΩΣΕΙ ότι
το baseline υπάρχει ήδη — αφού πρώτα ΑΠΟΔΕΙΧΘΕΙ.

Το ομοίωμα της παραγωγής χτίζεται από read-only introspection
(`research/billing-domain/production_shape.json`): ΜΟΝΟ δομή, καμία γραμμή
πελάτη, κανένα secret. Οι γραμμές που μπαίνουν είναι συνθετικές και υπάρχουν
για να αποδειχθεί ότι η μετανάστευση ΔΕΝ τις πειράζει.
"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
import uuid
from pathlib import Path

import psycopg2

from tests.test_migration_chain import (MIGRATIONS, Postgres, apply_all,
                                        docker_ok, introspect, migration_files)

ROOT = Path(__file__).resolve().parents[1]
SHAPE = json.loads(
    (ROOT / "research" / "billing-domain" / "production_shape.json")
    .read_text(encoding="utf-8"))
FINGERPRINT = json.loads(
    (ROOT / "db" / "baseline_fingerprint.json").read_text(encoding="utf-8"))


def run_migrate(dsn: str, *args: str) -> subprocess.CompletedProcess:
    """Το ΠΡΑΓΜΑΤΙΚΟ CLI, όπως θα το τρέξει άνθρωπος."""
    import os
    env = {**os.environ, "VITRINA_ENV": "staging", "DATABASE_URL_STAGING": dsn,
           "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([__import__("sys").executable, "scripts/migrate.py",
                           *args], cwd=ROOT, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def production_shaped(dsn: str) -> None:
    """Η αφετηρία της παραγωγής: το 0000 σε κενή βάση, χωρίς ιστορικό.

    Το 0000 παρήχθη από αποτύπωμα της παραγωγής, οπότε η εκτέλεσή του σε κενή
    βάση αναπαράγει ακριβώς αυτή τη μορφή. Το `test_shape_matches_production`
    το επαληθεύει έναντι του read-only αποτυπώματος — δεν το υποθέτει.
    """
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute((MIGRATIONS / "0000_production_baseline.sql")
                        .read_text(encoding="utf-8"))
    finally:
        conn.close()


# Συνθετικές γραμμές — τίποτα από πραγματικό πελάτη.
SEED_CLIENT = "11111111-1111-4111-8111-111111111111"
SEED_POST = "22222222-2222-4222-8222-222222222222"


def seed(dsn: str) -> None:
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clients(id,name,business_type,city,phone,status,plan)"
                " VALUES(%s,'Προϋπάρχων','taverna','Λάρισα','2100000000',"
                "'active','starter')", (SEED_CLIENT,))
            cur.execute("INSERT INTO site_content(client_id,content) "
                        "VALUES(%s,'{\"phone\":\"2100000000\"}')", (SEED_CLIENT,))
            cur.execute("INSERT INTO sites(client_id,url,preset,html) "
                        "VALUES(%s,'https://live.test','marble','ΖΩΝΤΑΝΟ')",
                        (SEED_CLIENT,))
            cur.execute("INSERT INTO subscriptions(client_id,plan,status,"
                        "stripe_customer_id) VALUES(%s,'site','active','cus_seed')",
                        (SEED_CLIENT,))
            cur.execute("INSERT INTO domain_orders(client_id,domain,status) "
                        "VALUES(%s,'proipar.gr','paid')", (SEED_CLIENT,))
            cur.execute("INSERT INTO posts(id,client_id,caption,status) "
                        "VALUES(%s,%s,'κείμενο','pending_approval')",
                        (SEED_POST, SEED_CLIENT))
    finally:
        conn.close()


def snapshot_rows(dsn: str) -> dict:
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            out = {}
            cur.execute("SELECT name,business_type,city,phone,status,plan "
                        "FROM clients WHERE id=%s", (SEED_CLIENT,))
            out["client"] = cur.fetchone()
            cur.execute("SELECT content FROM site_content WHERE client_id=%s",
                        (SEED_CLIENT,))
            out["content"] = cur.fetchone()
            cur.execute("SELECT url,preset,html FROM sites WHERE client_id=%s",
                        (SEED_CLIENT,))
            out["site"] = cur.fetchone()
            cur.execute("SELECT plan,status,stripe_customer_id FROM subscriptions "
                        "WHERE client_id=%s", (SEED_CLIENT,))
            out["subscription"] = cur.fetchone()
            cur.execute("SELECT domain,status FROM domain_orders WHERE client_id=%s",
                        (SEED_CLIENT,))
            out["order"] = cur.fetchone()
            cur.execute("SELECT caption,status FROM posts WHERE id=%s", (SEED_POST,))
            out["post"] = cur.fetchone()
            for table in SHAPE["tables"]:
                cur.execute(f"SELECT count(*) FROM {table}")
                out[f"count:{table}"] = cur.fetchone()[0]
            return out
    finally:
        conn.close()


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class ProductionShapedUpgrade(unittest.TestCase):
    """Η πλήρης ροή, πάνω σε βάση με σχήμα παραγωγής και δεδομένα μέσα."""

    @classmethod
    def setUpClass(cls):
        cls.pg = Postgres()
        cls.dsn = cls.pg.__enter__()
        production_shaped(cls.dsn)
        seed(cls.dsn)
        cls.before = snapshot_rows(cls.dsn)
        cls.adopt = run_migrate(cls.dsn, "--adopt-baseline", "0000")
        cls.status = run_migrate(cls.dsn, "--status")
        cls.apply = run_migrate(cls.dsn, "--apply")
        cls.after = snapshot_rows(cls.dsn)

    @classmethod
    def tearDownClass(cls):
        cls.pg.__exit__(None, None, None)

    def q(self, sql, *params):
        conn = psycopg2.connect(self.dsn)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            conn.close()

    # ── η αφετηρία ─────────────────────────────────────────────────────────
    def test_shape_matches_production(self):
        """Το ομοίωμα πρέπει να είναι όντως το σχήμα της παραγωγής."""
        rows = self.q("""SELECT table_name||'.'||column_name||'|'||data_type
                                ||'|'||is_nullable
                         FROM information_schema.columns
                         WHERE table_schema='public'
                           AND table_name = ANY(%s)""", SHAPE["tables"])
        have = {r[0] for r in rows}
        want = set(SHAPE["columns"])
        self.assertEqual(want - have, set(), "λείπουν στήλες της παραγωγής")
        for table, want_pk in SHAPE["primary_keys"].items():
            got = self.q("""SELECT pg_get_constraintdef(con.oid)
                            FROM pg_constraint con
                            JOIN pg_class rel ON rel.oid=con.conrelid
                            JOIN pg_namespace n ON n.oid=rel.relnamespace
                            WHERE n.nspname='public' AND rel.relname=%s
                              AND con.contype='p'""", table)
            self.assertEqual(got and got[0][0], want_pk, table)

    def test_baseline_would_fail_if_executed(self):
        """Η αιτία ύπαρξης όλου αυτού — αναπαράγεται, δεν υποτίθεται."""
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                with self.assertRaises(psycopg2.errors.InvalidTableDefinition):
                    cur.execute((MIGRATIONS / "0000_production_baseline.sql")
                                .read_text(encoding="utf-8"))
        finally:
            conn.close()

    # ── υιοθέτηση ──────────────────────────────────────────────────────────
    def test_adoption_succeeds_and_says_what_it_did(self):
        self.assertEqual(self.adopt.returncode, 0, self.adopt.stdout + self.adopt.stderr)
        out = self.adopt.stdout
        self.assertIn("ΧΩΡΙΣ εκτέλεση SQL", out)
        self.assertIn(FINGERPRINT["source_checksum"], out)
        self.assertIn(str(len(FINGERPRINT["tables"])), out)

    def test_baseline_recorded_with_repository_checksum(self):
        rows = self.q("SELECT version, filename, checksum FROM schema_migrations "
                      "WHERE version='0000'")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "0000_production_baseline.sql")
        self.assertEqual(rows[0][2], FINGERPRINT["source_checksum"])

    def test_adoption_did_not_create_editor_objects(self):
        """Η υιοθέτηση ΔΗΛΩΝΕΙ, δεν χτίζει."""
        rows = self.q("SELECT to_regclass('public.site_revisions')")
        # Μετά το --apply υπάρχει· ελέγχουμε ότι το ίδιο το adopt δεν το έφτιαξε,
        # μέσω της εξόδου του: δεν εκτέλεσε SQL.
        self.assertNotIn("✓ 0001", self.adopt.stdout)
        self.assertNotIn("✓ 0003", self.adopt.stdout)

    # ── status & apply ─────────────────────────────────────────────────────
    def test_status_shows_baseline_applied_and_rest_pending(self):
        out = self.status.stdout
        self.assertIn("0000_production_baseline.sql", out)
        self.assertRegex(out, r"✓\s+0000_production_baseline\.sql")
        self.assertIn("εκκρεμεί", out)

    def test_apply_runs_the_rest_and_never_the_baseline(self):
        self.assertEqual(self.apply.returncode, 0,
                         self.apply.stdout + self.apply.stderr)
        lines = self.apply.stdout.splitlines()
        # Η έξοδος έχει ΔΥΟ τμήματα: πρώτα η ΛΙΣΤΑ κατάστασης (όπου το ήδη
        # εφαρμοσμένο 0000 εμφανίζεται σωστά με ✓), και μετά η ΕΚΤΕΛΕΣΗ. Μόνο
        # το δεύτερο δείχνει τι έτρεξε τώρα.
        last_pending = max((i for i, l in enumerate(lines)
                            if "(εκκρεμεί)" in l), default=-1)
        executed = [l for l in lines[last_pending + 1:]
                    if l.strip().startswith("✓")]
        self.assertTrue(executed, "δεν εκτελέστηκε κανένα migration")
        self.assertFalse(any("0000_production_baseline" in l for l in executed),
                         "το 0000 ΕΚΤΕΛΕΣΤΗΚΕ — δεν έπρεπε")
        for version in ("0002", "0003", "0004", "0005", "0006", "0007", "0008"):
            self.assertTrue(any(version in l for l in executed),
                            f"το {version} δεν εφαρμόστηκε")
        # Ανεξάρτητο σήμα: το πλήθος. 9 αρχεία στον δίσκο, 8 εκτελέστηκαν.
        self.assertIn(f"Εφαρμόστηκαν {len(migration_files()) - 1}.",
                      self.apply.stdout)

    def test_every_version_recorded(self):
        rows = self.q("SELECT version FROM schema_migrations ORDER BY version")
        have = [r[0] for r in rows]
        # Το 0001 είναι staging-only· εδώ τρέχουμε ως staging, άρα μπαίνει.
        expect = [__import__("re").match(r"^(\d{4})_", p.name).group(1)
                  for p in migration_files()]
        self.assertEqual(have, expect)

    # ── το αποτέλεσμα ──────────────────────────────────────────────────────
    def test_editor_schema_is_correct(self):
        cols = {r[0] for r in self.q(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name='site_revisions'")}
        self.assertIn("idempotency_key", cols)
        self.assertIn("version_after", cols)
        self.assertNotIn("timestamp", cols, "legacy στήλη σε νέα βάση")
        self.assertNotIn("publish_status", cols)
        fns = {r[0] for r in self.q(
            "SELECT p.proname FROM pg_proc p JOIN pg_namespace n "
            "ON n.oid=p.pronamespace WHERE n.nspname='public' "
            "AND p.proname IN ('editor_commit','editor_undo')")}
        self.assertEqual(fns, {"editor_commit", "editor_undo"})
        ver = self.q("SELECT data_type,is_nullable FROM information_schema.columns "
                     "WHERE table_schema='public' AND table_name='site_content' "
                     "AND column_name='editor_version'")
        self.assertEqual(ver, [("bigint", "NO")])

    def test_service_role_permissions(self):
        missing = self.q("""
            SELECT t.table_name FROM information_schema.tables t
            WHERE t.table_schema='public' AND t.table_type='BASE TABLE'
              AND 0=(SELECT count(*) FROM information_schema.role_table_grants g
                     WHERE g.table_schema='public' AND g.table_name=t.table_name
                       AND g.grantee='service_role')""")
        self.assertEqual(missing, [])

    def test_rls_and_policies(self):
        rls = dict(self.q("""SELECT rel.relname, rel.relrowsecurity
                             FROM pg_class rel
                             JOIN pg_namespace n ON n.oid=rel.relnamespace
                             WHERE n.nspname='public' AND rel.relkind='r'"""))
        for table in SHAPE["rls_enabled"]:
            self.assertTrue(rls.get(table), f"το RLS έσβησε στο {table}")
        self.assertTrue(rls.get("site_revisions"), "RLS στο site_revisions")
        self.assertEqual(self.q("SELECT count(*) FROM pg_policies "
                                "WHERE schemaname='public'"), [(0,)])

    # ── τα δεδομένα ────────────────────────────────────────────────────────
    def test_existing_rows_survive_untouched(self):
        for key in ("client", "content", "site", "subscription", "order", "post"):
            self.assertEqual(self.before[key], self.after[key],
                             f"άλλαξε: {key}")

    def test_no_rows_appeared_or_vanished(self):
        for table in SHAPE["tables"]:
            k = f"count:{table}"
            self.assertEqual(self.before[k], self.after[k],
                             f"άλλαξε το πλήθος γραμμών στο {table}")

    def test_editor_works_on_the_preexisting_client(self):
        """Ο πελάτης που υπήρχε ΠΡΙΝ τη μετανάστευση μπορεί να επεξεργαστεί."""
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT editor_commit(%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)",
                    (SEED_CLIENT, 0, "adopt-1", "αλλαγή", json.dumps([]),
                     json.dumps({"phone": "2100000000"}),
                     json.dumps({"phone": "2109999999"})))
                out = cur.fetchone()[0]
                self.assertEqual(out["version"], 1)
                cur.execute("SELECT editor_undo(%s,1,'adopt-undo')", (SEED_CLIENT,))
                back = cur.fetchone()[0]
                self.assertEqual(back["content"]["phone"], "2100000000")
                cur.execute("SELECT html FROM sites WHERE client_id=%s",
                            (SEED_CLIENT,))
                self.assertEqual(cur.fetchone()[0], "ΖΩΝΤΑΝΟ")
                cur.execute("DELETE FROM site_revisions WHERE client_id=%s",
                            (SEED_CLIENT,))
                cur.execute("UPDATE site_content SET content=%s, editor_version=0 "
                            "WHERE client_id=%s",
                            (json.dumps({"phone": "2100000000"}), SEED_CLIENT))
        finally:
            conn.close()


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class AdoptionFailsClosed(unittest.TestCase):
    """Κάθε επικίνδυνη περίπτωση σταματά ΠΡΙΝ γράψει οτιδήποτε."""

    def _fresh_shape(self, mutate: str | None = None):
        pg = Postgres()
        dsn = pg.__enter__()
        self.addCleanup(pg.__exit__, None, None, None)
        production_shaped(dsn)
        if mutate:
            conn = psycopg2.connect(dsn)
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    cur.execute(mutate)
            finally:
                conn.close()
        return dsn

    def assert_refused(self, dsn: str, result, needle: str = ""):
        self.assertNotEqual(result.returncode, 0,
                            f"ΕΓΙΝΕ ΔΕΚΤΟ:\n{result.stdout}")
        if needle:
            self.assertIn(needle, result.stdout)
        rows = psycopg2.connect(dsn)
        try:
            with rows.cursor() as cur:
                cur.execute("SELECT to_regclass('public.schema_migrations')")
                self.assertIsNone(cur.fetchone()[0],
                                  "δημιουργήθηκε ιστορικό παρά την αποτυχία")
        finally:
            rows.close()

    def test_missing_table(self):
        dsn = self._fresh_shape("DROP TABLE public.brand_profiles CASCADE")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "πίνακας brand_profiles")

    def test_missing_primary_key(self):
        dsn = self._fresh_shape(
            "ALTER TABLE public.clients DROP CONSTRAINT clients_pkey CASCADE")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "primary key clients:clients_pkey")

    def test_incompatible_column_type(self):
        dsn = self._fresh_shape(
            "ALTER TABLE public.clients ALTER COLUMN name TYPE varchar(10)")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "clients.name")

    def test_missing_column(self):
        dsn = self._fresh_shape("ALTER TABLE public.clients DROP COLUMN phone")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "στήλη clients.phone")

    def test_nullability_change_is_caught(self):
        dsn = self._fresh_shape(
            "ALTER TABLE public.clients ALTER COLUMN city DROP NOT NULL")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "clients.city")

    def test_missing_unique_constraint(self):
        dsn = self._fresh_shape("ALTER TABLE public.domains "
                                "DROP CONSTRAINT domains_domain_key")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "unique domains:domains_domain_key")

    def test_missing_foreign_key(self):
        dsn = self._fresh_shape("ALTER TABLE public.sites "
                                "DROP CONSTRAINT sites_client_id_fkey")
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"),
                            "foreign key sites:sites_client_id_fkey")

    def test_empty_database_is_refused(self):
        pg = Postgres()
        dsn = pg.__enter__()
        self.addCleanup(pg.__exit__, None, None, None)
        self.assert_refused(dsn, run_migrate(dsn, "--adopt-baseline", "0000"))

    def test_non_baseline_version_is_refused(self):
        dsn = self._fresh_shape()
        for version in ("0001", "0003", "0008", "9999"):
            r = run_migrate(dsn, "--adopt-baseline", version)
            self.assertNotEqual(r.returncode, 0, version)
            self.assertIn("ΜΟΝΟ για το 0000", r.stdout, version)

    def test_already_adopted_is_refused(self):
        dsn = self._fresh_shape()
        first = run_migrate(dsn, "--adopt-baseline", "0000")
        self.assertEqual(first.returncode, 0, first.stdout)
        second = run_migrate(dsn, "--adopt-baseline", "0000")
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("ΗΔΗ καταγεγραμμένο", second.stdout)
        rows = psycopg2.connect(dsn)
        try:
            with rows.cursor() as cur:
                cur.execute("SELECT count(*) FROM schema_migrations")
                self.assertEqual(cur.fetchone()[0], 1, "διπλή εγγραφή")
        finally:
            rows.close()

    def test_partially_populated_history_is_refused(self):
        dsn = self._fresh_shape()
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("""CREATE TABLE schema_migrations(
                    version text PRIMARY KEY, filename text NOT NULL,
                    checksum text NOT NULL,
                    applied_at timestamptz NOT NULL DEFAULT now())""")
                cur.execute("INSERT INTO schema_migrations VALUES"
                            "('0002','0002_media_semantics.sql','deadbeef')")
        finally:
            conn.close()
        r = run_migrate(dsn, "--adopt-baseline", "0000")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ασυνεπή κατάσταση", r.stdout)

    def test_stale_fingerprint_is_refused(self):
        """Αν το 0000 αλλάξει χωρίς να ξαναφτιαχτεί το αποτύπωμα."""
        dsn = self._fresh_shape()
        fp = ROOT / "db" / "baseline_fingerprint.json"
        original = fp.read_text(encoding="utf-8")
        data = json.loads(original)
        data["source_checksum"] = "0000000000000000"
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=2,
                                 sort_keys=True) + "\n", encoding="utf-8")
        try:
            r = run_migrate(dsn, "--adopt-baseline", "0000")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("αποτύπωμα δεν αντιστοιχεί", r.stdout)
        finally:
            fp.write_text(original, encoding="utf-8")


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class ProductionScope(unittest.TestCase):
    """Η ΠΡΑΓΜΑΤΙΚΗ διαδρομή της παραγωγής, με `VITRINA_ENV=production`.

    ΓΙΑΤΙ ΧΩΡΙΣΤΑ. Οι υπόλοιπες δοκιμές τρέχουν ως staging, όπου το
    `0001_agency_kernel.sql` ΕΦΑΡΜΟΖΕΤΑΙ. Στην παραγωγή δεν πρέπει: φέρει
    `-- ENV: staging-only` γιατί ο Agency Kernel δεν έχει ολοκληρωθεί. Η
    διαφορά είναι μία γραμμή στο runbook (7 migrations αντί 8) και δεν
    επιτρέπεται να μείνει υπόθεση.

    Το `DATABASE_URL_PRODUCTION` δείχνει σε ΑΝΑΛΩΣΙΜΟ container, όχι στην
    παραγωγή. Αυτό που δοκιμάζεται είναι η ΛΟΓΙΚΗ ΕΠΙΛΟΓΗΣ του runner.
    """

    @classmethod
    def setUpClass(cls):
        import os
        cls.pg = Postgres()
        cls.dsn = cls.pg.__enter__()
        production_shaped(cls.dsn)
        seed(cls.dsn)
        cls.env = {**os.environ, "VITRINA_ENV": "production",
                   "DATABASE_URL_PRODUCTION": cls.dsn,
                   "PYTHONIOENCODING": "utf-8"}
        cls.env.pop("DATABASE_URL_STAGING", None)
        # Η ΑΚΟΛΟΥΘΙΑ ΤΡΕΧΕΙ ΕΔΩ, ΜΙΑ ΦΟΡΑ. Το unittest εκτελεί τα tests
        # αλφαβητικά· αν η μετανάστευση γινόταν μέσα σε test, όποιο έτρεχε πριν
        # θα έβλεπε βάση χωρίς editor. Τα tests ΔΙΑΒΑΖΟΥΝ αποτέλεσμα, δεν το
        # παράγουν.
        cls.adopt = cls.run_prod_cls(cls, "--adopt-baseline", "0000")
        cls.status = cls.run_prod_cls(cls, "--status")
        cls.applied = cls.run_prod_cls(cls, "--apply", "--confirm-production")

    def run_prod_cls(self, *args):
        import sys as _sys
        return subprocess.run([_sys.executable, "scripts/migrate.py", *args],
                              cwd=ROOT, env=self.env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")

    @classmethod
    def tearDownClass(cls):
        cls.pg.__exit__(None, None, None)

    def run_prod(self, *args):
        import sys as _sys
        return subprocess.run([_sys.executable, "scripts/migrate.py", *args],
                              cwd=ROOT, env=self.env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")

    def test_apply_refuses_without_explicit_confirmation(self):
        r = self.run_prod("--apply")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--confirm-production", r.stdout + r.stderr)

    def test_full_production_path(self):
        self.assertEqual(self.adopt.returncode, 0,
                         self.adopt.stdout + self.adopt.stderr)
        self.assertIn("staging-only", self.status.stdout,
                      "το 0001 δεν σημάνθηκε ως εκτός παραγωγής")
        self.assertEqual(self.applied.returncode, 0,
                         self.applied.stdout + self.applied.stderr)
        # ΠΑΡΑΓΟΜΕΝΟ, ΟΧΙ ΣΤΑΘΕΡΟ. Ήταν γραμμένο «7» και πάλιωσε την ημέρα που
        # προστέθηκε το 0009 — το test κοκκίνισε ενώ η διαδρομή ήταν σωστή.
        # Ο αριθμός προκύπτει: όλα τα αρχεία − το υιοθετημένο baseline − όσα
        # φέρουν `-- ENV: staging-only`.
        staging_only = sum(
            1 for p in migration_files()
            if "-- ENV: staging-only" in p.read_text(encoding="utf-8")[:200])
        expected = len(migration_files()) - 1 - staging_only
        self.assertIn(f"Εφαρμόστηκαν {expected}.", self.applied.stdout)

        conn = psycopg2.connect(self.dsn)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                versions = [r[0] for r in cur.fetchall()]
                cur.execute("SELECT to_regclass('public.agent_registry')")
                agency = cur.fetchone()[0]
        finally:
            conn.close()
        expect_versions = ["0000"] + [
            re.match(r"^(\d{4})_", p.name).group(1) for p in migration_files()
            if not p.name.startswith("0000_")
            and "-- ENV: staging-only" not in p.read_text(encoding="utf-8")[:200]]
        self.assertEqual(
            versions, expect_versions,
            "το 0001 δεν έπρεπε να καταγραφεί στην παραγωγή")
        self.assertIsNone(agency, "ο Agency Kernel μπήκε στην παραγωγή")

    def test_data_and_editor_survive_the_production_path(self):
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM clients WHERE id=%s", (SEED_CLIENT,))
                self.assertEqual(cur.fetchone(), ("Προϋπάρχων",))
                cur.execute("SELECT html FROM sites WHERE client_id=%s",
                            (SEED_CLIENT,))
                self.assertEqual(cur.fetchone(), ("ΖΩΝΤΑΝΟ",))
                cur.execute(
                    "SELECT editor_commit(%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)",
                    (SEED_CLIENT, 0, "prod-1", "αλλαγή", json.dumps([]),
                     json.dumps({"phone": "2100000000"}),
                     json.dumps({"phone": "2107777777"})))
                self.assertEqual(cur.fetchone()[0]["version"], 1)
        finally:
            conn.close()


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class FingerprintMatchesBaseline(unittest.TestCase):
    def test_fingerprint_is_current(self):
        """Το αποτύπωμα δεν επιτρέπεται να ξεμείνει πίσω από το 0000."""
        import hashlib
        actual = hashlib.sha256(
            (MIGRATIONS / "0000_production_baseline.sql").read_bytes()
        ).hexdigest()[:16]
        self.assertEqual(FINGERPRINT["source_checksum"], actual,
                         "ξανατρέξε: python scripts/make_baseline_fingerprint.py")

    def test_fingerprint_describes_what_0000_builds(self):
        with Postgres() as dsn:
            apply_all(dsn, upto="0000")
            conn = psycopg2.connect(dsn)
            try:
                with conn.cursor() as cur:
                    cur.execute("""SELECT table_name||'.'||column_name,
                                          data_type||'|'||is_nullable
                                   FROM information_schema.columns
                                   WHERE table_schema='public'""")
                    built = dict(cur.fetchall())
            finally:
                conn.close()
        self.assertEqual(FINGERPRINT["columns"], built)


if __name__ == "__main__":
    unittest.main()
