"""Η αλυσίδα των migrations πρέπει να τρέχει σε ΚΕΝΗ βάση, χωρίς χειροκίνητο βήμα.

ΓΙΑΤΙ ΥΠΑΡΧΕΙ. Το `0003` ξαναγράφτηκε αφού είχε εφαρμοστεί: από «πίνακας
τεκμηρίων» (με `timestamp`/`publish_status`) σε «ατομικός editor». Το `0004`
όμως είχε γραφτεί για να αναβαθμίσει την ΠΑΛΙΑ μορφή και διάβαζε τη στήλη
`timestamp`. Αποτέλεσμα: κάθε βάση χτισμένη από το μηδέν σταματούσε με
`column "timestamp" does not exist` — άρα και η παραγωγή, που δεν έχει
καθόλου πίνακες editor.

Δεν το έπιανε κανένα test επειδή το `scripts/verify_editing_engine.py`
εφαρμόζει ΜΟΝΟ 0000 και 0003, ποτέ την ακολουθία 0003 → 0004 → 0005.

ΔΥΟ ΔΙΑΔΡΟΜΕΣ, ΧΩΡΙΣΤΑ:

  Α. ΚΑΘΑΡΗ ΕΓΚΑΤΑΣΤΑΣΗ   κενή βάση → 0000 → … → τελευταίο
  Β. ΠΑΛΙΟ STAGING        κενή βάση → 0000 … 0003 → *αναπαραγωγή της παλιάς
                          μορφής* → διορθωμένο 0004 → … → τελευταίο

Και οι δύο πρέπει να καταλήγουν στο ΙΔΙΟ συμβόλαιο. Οι μόνες επιτρεπτές
διαφορές είναι οι τεκμηριωμένες legacy στήλες του staging.

Χρειάζεται Docker/Podman. Χωρίς αυτό το test κάνει SKIP — δεν περνά σιωπηλά.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import socket
import subprocess
import time
import unittest
import uuid
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "db" / "migrations"
NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")

# Οι στήλες που υπάρχουν ΜΟΝΟ στο staging, από το παλιό 0003. Ο κώδικας δεν
# τις αναφέρει πουθενά (επαληθευμένο με grep σε src/, sites/, scripts/).
# Δεν διαδίδονται σε καθαρές βάσεις — είναι υπόλειμμα, όχι συμβόλαιο.
LEGACY_ONLY = {"timestamp", "publish_status"}
LEGACY_INDEX = "idx_site_revisions_client"
LEGACY_CONSTRAINT = "site_revisions_publish_status_check"


def docker_ok() -> bool:
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=25)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def migration_files() -> list[Path]:
    out = []
    for p in sorted(MIGRATIONS.iterdir()):
        if p.is_dir() or p.suffix != ".sql":
            continue
        assert NAME_RE.match(p.name), f"λάθος όνομα migration: {p.name}"
        out.append(p)
    return out


class Postgres:
    """Μια αναλώσιμη, ΚΕΝΗ βάση. Σβήνεται πάντα."""

    def __init__(self) -> None:
        self.name = f"vitrina-chain-{secrets.token_hex(4)}"
        self.password = secrets.token_urlsafe(16)
        self.port = free_port()

    def __enter__(self) -> str:
        subprocess.run(
            ["docker", "run", "-d", "--rm", "--name", self.name,
             "-e", f"POSTGRES_PASSWORD={self.password}",
             "-e", "POSTGRES_DB=vitrina",
             "-p", f"{self.port}:5432", "postgres:17-alpine"],
            capture_output=True, check=True)
        self.dsn = (f"postgresql://postgres:{self.password}"
                    f"@127.0.0.1:{self.port}/vitrina")
        for _ in range(90):
            try:
                psycopg2.connect(self.dsn, connect_timeout=2).close()
                return self.dsn
            except psycopg2.OperationalError:
                time.sleep(0.5)
        raise RuntimeError("η Postgres δεν σηκώθηκε")

    def __exit__(self, *a) -> None:
        subprocess.run(["docker", "rm", "-f", self.name], capture_output=True)


def apply_all(dsn: str, upto: str | None = None,
              after_version: dict[str, str] | None = None,
              skip: tuple[str, ...] = ()) -> list[str]:
    """Εφαρμόζει ΚΑΘΕ migration με τη σειρά ονόματος. Σκάει στο πρώτο σφάλμα.

    `after_version`: SQL που τρέχει ΜΕΤΑ από συγκεκριμένη έκδοση — έτσι
    αναπαράγεται η ιστορική μορφή του staging χωρίς να πειραχτεί κανένα αρχείο.
    """
    applied: list[str] = []
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for path in migration_files():
                version = NAME_RE.match(path.name).group(1)
                if version in skip:
                    continue
                try:
                    cur.execute(path.read_text(encoding="utf-8"))
                except Exception as e:  # noqa: BLE001
                    raise AssertionError(
                        f"το {path.name} ΔΕΝ ΕΚΤΕΛΕΣΤΗΚΕ: {e}") from e
                applied.append(version)
                if after_version and version in after_version:
                    cur.execute(after_version[version])
                if upto and version == upto:
                    break
    finally:
        conn.close()
    return applied


def introspect(dsn: str) -> dict:
    """Ό,τι μπορεί να αποκλίνει σιωπηλά."""
    q = {
        "columns": """SELECT table_name||'.'||column_name||':'||data_type||':'
                             ||is_nullable||':'||COALESCE(column_default,'')
                      FROM information_schema.columns WHERE table_schema='public'""",
        "constraints": """SELECT rel.relname||':'||con.conname||':'
                                 ||pg_get_constraintdef(con.oid)
                          FROM pg_constraint con
                          JOIN pg_class rel ON rel.oid=con.conrelid
                          JOIN pg_namespace n ON n.oid=rel.relnamespace
                          WHERE n.nspname='public'""",
        "indexes": """SELECT tablename||':'||indexname||':'||indexdef
                      FROM pg_indexes WHERE schemaname='public'""",
        "rls": """SELECT rel.relname||':'||rel.relrowsecurity::text
                  FROM pg_class rel JOIN pg_namespace n ON n.oid=rel.relnamespace
                  WHERE n.nspname='public' AND rel.relkind='r'""",
        "policies": """SELECT tablename||':'||policyname||':'||cmd
                       FROM pg_policies WHERE schemaname='public'""",
        "grants": """SELECT table_name||':'||grantee||':'||privilege_type
                     FROM information_schema.role_table_grants
                     WHERE table_schema='public'
                       AND grantee IN ('service_role','anon','authenticated')""",
        "functions": """SELECT p.proname||'('
                               ||pg_get_function_identity_arguments(p.oid)||')'
                               ||'::'||md5(regexp_replace(
                                    pg_get_functiondef(p.oid), '\\s+', ' ', 'g'))
                        FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
                        WHERE n.nspname='public'
                          AND p.proname IN ('editor_commit','editor_undo')""",
    }
    out: dict[str, set] = {}
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            for key, sql in q.items():
                cur.execute(sql)
                out[key] = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()
    return out


def drop_legacy(entries: set[str]) -> set[str]:
    """Αφαιρεί ΜΟΝΟ τα ρητά τεκμηριωμένα legacy υπολείμματα."""
    keep = set()
    for e in entries:
        if any(f"site_revisions.{c}:" in e for c in LEGACY_ONLY):
            continue
        if LEGACY_INDEX in e or LEGACY_CONSTRAINT in e:
            continue
        keep.add(e)
    return keep


# Η ιστορική μορφή, όπως την έφτιαχνε το ΤΟΤΕ 0003. Ανακατασκευάστηκε από το
# πραγματικό σχήμα του staging (16 στήλες έναντι 14).
LEGACY_SHAPE = """
ALTER TABLE public.site_revisions
  ADD COLUMN IF NOT EXISTS "timestamp" timestamptz NOT NULL DEFAULT now(),
  ADD COLUMN IF NOT EXISTS publish_status text NOT NULL DEFAULT 'draft';
ALTER TABLE public.site_revisions
  DROP CONSTRAINT IF EXISTS site_revisions_publish_status_check;
ALTER TABLE public.site_revisions
  ADD CONSTRAINT site_revisions_publish_status_check
  CHECK (publish_status IN ('draft','published'));
CREATE INDEX IF NOT EXISTS idx_site_revisions_client
  ON public.site_revisions(client_id, "timestamp" DESC);
"""


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class MigrationChain(unittest.TestCase):

    def test_a_fresh_install_runs_every_migration(self):
        """ΔΙΑΔΡΟΜΗ Α: κενή βάση → όλα τα migrations, χωρίς παρέμβαση."""
        expected = [NAME_RE.match(p.name).group(1) for p in migration_files()]
        with Postgres() as dsn:
            applied = apply_all(dsn)
        self.assertEqual(applied, expected,
                         "δεν εκτελέστηκαν όλα τα migrations με τη σειρά")

    def test_b_legacy_staging_shape_upgrades(self):
        """ΔΙΑΔΡΟΜΗ Β: η ιστορική μορφή του staging αναβαθμίζεται καθαρά."""
        expected = [NAME_RE.match(p.name).group(1) for p in migration_files()]
        with Postgres() as dsn:
            applied = apply_all(dsn, after_version={"0003": LEGACY_SHAPE})
        self.assertEqual(applied, expected)

    def test_both_paths_reach_the_same_contract(self):
        """Το τελικό συμβόλαιο είναι ΕΝΑ — εκτός των legacy υπολειμμάτων."""
        with Postgres() as fresh_dsn:
            apply_all(fresh_dsn)
            fresh = introspect(fresh_dsn)
        with Postgres() as legacy_dsn:
            apply_all(legacy_dsn, after_version={"0003": LEGACY_SHAPE})
            legacy = introspect(legacy_dsn)

        problems: list[str] = []
        for key in fresh:
            a, b = drop_legacy(fresh[key]), drop_legacy(legacy[key])
            if a != b:
                problems.append(
                    f"{key}: μόνο-καθαρή={sorted(a - b)[:4]} "
                    f"μόνο-legacy={sorted(b - a)[:4]}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_legacy_columns_never_reach_a_clean_database(self):
        with Postgres() as dsn:
            apply_all(dsn)
            conn = psycopg2.connect(dsn)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name='site_revisions'")
                    cols = {r[0] for r in cur.fetchall()}
                    cur.execute(
                        "SELECT data_type, is_nullable, column_default "
                        "FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name='site_content' "
                        "  AND column_name='editor_version'")
                    editor_version = cur.fetchone()
            finally:
                conn.close()
        self.assertFalse(cols & LEGACY_ONLY,
                         f"legacy στήλες διέρρευσαν σε καθαρή βάση: "
                         f"{cols & LEGACY_ONLY}")
        # Το `editor_version` είναι ο μετρητής της αισιόδοξης ταυτοχρονίας:
        # χωρίς NOT NULL + default 0, το πρώτο commit συγκρίνει με NULL.
        self.assertIsNotNone(editor_version, "λείπει το site_content.editor_version")
        self.assertEqual(editor_version[0], "bigint")
        self.assertEqual(editor_version[1], "NO")
        self.assertIn("0", editor_version[2] or "")

    def test_0004_never_touches_the_legacy_column_unguarded(self):
        """Στατικός φρουρός: η αναφορά επιτρέπεται ΜΟΝΟ μέσα σε έλεγχο ύπαρξης.

        Χωρίς αυτό, μια μελλοντική επεξεργασία μπορεί να ξαναβάλει σιωπηλά
        αναφορά στη legacy στήλη και να σπάσει ξανά κάθε καθαρή εγκατάσταση."""
        src = (MIGRATIONS / "0004_ai_editor_atomic_upgrade.sql").read_text(
            encoding="utf-8")
        code = "\n".join(l for l in src.splitlines()
                         if not l.strip().startswith("--"))
        marker = "$legacy_created_at$"
        self.assertIn(marker, code, "χάθηκε ο φρουρός του 0004")
        parts = code.split(marker)
        # parts[1] είναι το σώμα του DO block· ό,τι είναι εκτός δεν επιτρέπεται
        # να αναφέρει τη στήλη.
        outside = parts[0] + "".join(parts[2:])
        self.assertNotIn('"timestamp"', outside,
                         "το 0004 αναφέρει τη legacy στήλη εκτός φρουρού")

    def test_0007_is_idempotent(self):
        """Το ίδιο αρχείο δύο φορές δεν αλλάζει τίποτα."""
        with Postgres() as dsn:
            apply_all(dsn)
            before = introspect(dsn)["grants"]
            conn = psycopg2.connect(dsn)
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    cur.execute((MIGRATIONS / "0007_service_role_grants.sql")
                                .read_text(encoding="utf-8"))
            finally:
                conn.close()
            after = introspect(dsn)["grants"]
        self.assertEqual(before, after)

    def test_rerunning_the_whole_chain_changes_nothing(self):
        """ΤΟ ΤΕΚΜΗΡΙΟ ΓΙΑ ΤΟ CHECKSUM.

        Το staging έτρεξε ΠΑΛΙΟ 0004· το repo έχει τώρα διορθωμένο, άρα άλλο
        checksum. Το ερώτημα δεν είναι «να το ξανατρέξουμε;» — είναι «αν
        ξανατρέξει, πειράζει;». Εδώ κάθε migration εκτελείται ΔΕΥΤΕΡΗ φορά
        πάνω σε ήδη μεταναστευμένη βάση, και το σχήμα πρέπει να μείνει
        απαράλλαχτο. Αν αυτό ισχύει, η ενημέρωση της εγγραφής checksum είναι
        λογιστική πράξη, όχι αλλαγή κατάστασης.

        ΤΟ 0000 ΕΞΑΙΡΕΙΤΑΙ, ΚΑΙ ΔΗΛΩΝΕΤΑΙ ΓΙΑΤΙ. Το ίδιο του το σχόλιο λέει
        «Ασφαλές να ξανατρέξει (IF NOT EXISTS παντού)» — μετρήθηκε ότι ΔΕΝ
        ισχύει: σκάει με «multiple primary keys for table "clients"». Δεν
        διορθώνεται εδώ (είναι το baseline, εφαρμοσμένο παντού) και δεν
        κρύβεται: το `test_baseline_is_not_rerunnable` το κλειδώνει ως γνωστό.
        """
        rest = [p for p in migration_files()
                if not p.name.startswith("0000_")]
        with Postgres() as dsn:
            apply_all(dsn, after_version={"0003": LEGACY_SHAPE})
            before = introspect(dsn)
            conn = psycopg2.connect(dsn)
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    for path in rest:
                        try:
                            cur.execute(path.read_text(encoding="utf-8"))
                        except Exception as e:  # noqa: BLE001
                            self.fail(f"το {path.name} δεν αντέχει δεύτερη "
                                      f"εκτέλεση: {e}")
            finally:
                conn.close()
            after = introspect(dsn)
        problems = [f"{k}: +{sorted(after[k] - before[k])[:3]} "
                    f"-{sorted(before[k] - after[k])[:3]}"
                    for k in before if before[k] != after[k]]
        self.assertEqual(problems, [], "\n".join(problems))

    def test_baseline_is_not_rerunnable(self):
        """Γνωστό, τεκμηριωμένο όριο — όχι σιωπηλή παράλειψη.

        Αν κάποια μέρα το 0000 γίνει όντως idempotent, αυτό το test θα
        κοκκινίσει και θα θυμίσει να ενημερωθεί το σχόλιό του.
        """
        with Postgres() as dsn:
            apply_all(dsn, upto="0000")
            conn = psycopg2.connect(dsn)
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    with self.assertRaises(psycopg2.Error):
                        cur.execute(
                            (MIGRATIONS / "0000_production_baseline.sql")
                            .read_text(encoding="utf-8"))
            finally:
                conn.close()

    def test_service_role_can_reach_every_table(self):
        with Postgres() as dsn:
            apply_all(dsn)
            conn = psycopg2.connect(dsn)
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT t.table_name FROM information_schema.tables t
                        WHERE t.table_schema='public' AND t.table_type='BASE TABLE'
                          AND 0=(SELECT count(*)
                                 FROM information_schema.role_table_grants g
                                 WHERE g.table_schema='public'
                                   AND g.table_name=t.table_name
                                   AND g.grantee='service_role')""")
                    missing = [r[0] for r in cur.fetchall()]
            finally:
                conn.close()
        self.assertEqual(missing, [],
                         f"ο service_role δεν φτάνει σε: {missing}")


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class EditorContractOnFreshInstall(unittest.TestCase):
    """Το σχήμα που παράγει η αλυσίδα πρέπει να ΔΟΥΛΕΥΕΙ, όχι απλώς να υπάρχει.

    Μία βάση καθαρής εγκατάστασης, όλα τα σενάρια του editor πάνω της.
    """

    @classmethod
    def setUpClass(cls):
        cls.pg = Postgres()
        cls.dsn = cls.pg.__enter__()
        apply_all(cls.dsn)

    @classmethod
    def tearDownClass(cls):
        cls.pg.__exit__(None, None, None)

    def setUp(self):
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True
        self.a, self.b = str(uuid.uuid4()), str(uuid.uuid4())
        self.state = {"name": "Δοκιμή", "phone": "2100000000"}
        with self.conn.cursor() as cur:
            for cid, nm in ((self.a, "Α"), (self.b, "Β")):
                cur.execute("INSERT INTO clients(id,name,business_type,city) "
                            "VALUES(%s,%s,'doctor','Αθήνα')", (cid, nm))
                cur.execute("INSERT INTO site_content(client_id,content) "
                            "VALUES(%s,%s)", (cid, json.dumps(self.state)))

    def tearDown(self):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM clients WHERE id IN (%s,%s)", (self.a, self.b))
        self.conn.close()

    def commit(self, cid, expected, key, after, cur=None):
        own = cur is None
        cur = cur or self.conn.cursor()
        try:
            cur.execute(
                "SELECT editor_commit(%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)",
                (cid, expected, key, "μήνυμα", json.dumps([]),
                 json.dumps(self.state), json.dumps(after)))
            return cur.fetchone()[0]
        finally:
            if own:
                cur.close()

    def content(self, cid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT content, editor_version FROM site_content "
                        "WHERE client_id=%s", (cid,))
            return cur.fetchone()

    def test_apply(self):
        out = self.commit(self.a, 0, "k1", {**self.state, "phone": "2101111111"})
        self.assertEqual(out["version"], 1)
        self.assertEqual(self.content(self.a)[0]["phone"], "2101111111")

    def test_idempotency(self):
        after = {**self.state, "phone": "2102222222"}
        first = self.commit(self.a, 0, "same", after)
        second = self.commit(self.a, 0, "same", after)
        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(first["revision_id"], second["revision_id"])
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM site_revisions WHERE client_id=%s",
                        (self.a,))
            self.assertEqual(cur.fetchone()[0], 1)

    def test_stale_version_is_rejected_as_application_conflict(self):
        self.commit(self.a, 0, "k1", {**self.state, "phone": "2103333333"})
        with self.assertRaises(psycopg2.Error) as ctx:
            self.commit(self.a, 0, "k2", {**self.state, "phone": "2104444444"})
        # P0001, όχι 40001: μια ξεπερασμένη καρτέλα είναι σύγκρουση εφαρμογής,
        # όχι serialization failure που θα ξαναδοκίμαζε ο PostgREST.
        self.assertEqual(ctx.exception.pgcode, "P0001")

    def test_undo(self):
        self.commit(self.a, 0, "k1", {**self.state, "phone": "2105555555"})
        with self.conn.cursor() as cur:
            cur.execute("SELECT editor_undo(%s,1,'u1')", (self.a,))
            out = cur.fetchone()[0]
        self.assertEqual(out["content"]["phone"], "2100000000")
        self.assertEqual(out["version"], 2, "το undo προχωράει την έκδοση")
        content, version = self.content(self.a)
        self.assertEqual(content, self.state)
        self.assertEqual(version, 2)

    def test_forced_rollback_leaves_nothing_behind(self):
        """Αποτυχία στη μέση της συναλλαγής δεν αφήνει μισή κατάσταση."""
        conn = psycopg2.connect(self.dsn)          # ΧΩΡΙΣ autocommit
        try:
            with conn.cursor() as cur:
                self.commit(self.a, 0, "tx", {**self.state, "phone": "2106666666"},
                            cur=cur)
                cur.execute("SELECT 1/0")          # σκόπιμη κατάρρευση
        except psycopg2.Error:
            conn.rollback()
        finally:
            conn.close()
        content, version = self.content(self.a)
        self.assertEqual(version, 0, "η έκδοση προχώρησε παρά το rollback")
        self.assertEqual(content, self.state, "το περιεχόμενο άλλαξε παρά το rollback")
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM site_revisions WHERE client_id=%s",
                        (self.a,))
            self.assertEqual(cur.fetchone()[0], 0, "έμεινε ορφανή αναθεώρηση")

    def test_tenant_isolation(self):
        """Η επεξεργασία του Α δεν αγγίζει τον Β — ούτε καν στο idempotency."""
        self.commit(self.a, 0, "shared-key", {**self.state, "phone": "2107777777"})
        # Ίδιο κλειδί, ΑΛΛΟΣ πελάτης: πρέπει να είναι κανονική νέα εγγραφή.
        out_b = self.commit(self.b, 0, "shared-key",
                            {**self.state, "phone": "2108888888"})
        self.assertFalse(out_b["duplicate"],
                         "το idempotency key διέρρευσε ανάμεσα σε πελάτες")
        self.assertEqual(self.content(self.a)[0]["phone"], "2107777777")
        self.assertEqual(self.content(self.b)[0]["phone"], "2108888888")
        self.assertEqual(self.content(self.a)[1], 1)
        self.assertEqual(self.content(self.b)[1], 1)
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM site_revisions WHERE client_id=%s",
                        (self.a,))
            self.assertEqual(cur.fetchone()[0], 1)

    def test_undo_of_one_tenant_does_not_move_the_other(self):
        self.commit(self.a, 0, "ka", {**self.state, "phone": "2109999999"})
        self.commit(self.b, 0, "kb", {**self.state, "phone": "2101010101"})
        with self.conn.cursor() as cur:
            cur.execute("SELECT editor_undo(%s,1,'ua')", (self.a,))
        self.assertEqual(self.content(self.a)[0]["phone"], "2100000000")
        self.assertEqual(self.content(self.b)[0]["phone"], "2101010101",
                         "το undo του Α μετακίνησε τον Β")

    def test_published_site_is_untouched(self):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO sites(client_id,url,preset,html) "
                        "VALUES(%s,'https://live.test','marble','ΖΩΝΤΑΝΟ')",
                        (self.a,))
        self.commit(self.a, 0, "k1", {**self.state, "phone": "2101212121"})
        with self.conn.cursor() as cur:
            cur.execute("SELECT html FROM sites WHERE client_id=%s", (self.a,))
            self.assertEqual(cur.fetchone()[0], "ΖΩΝΤΑΝΟ")

    def test_only_service_role_may_execute_the_editor(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT p.proname,
                       has_function_privilege('service_role', p.oid, 'EXECUTE'),
                       has_function_privilege('anon', p.oid, 'EXECUTE'),
                       has_function_privilege('authenticated', p.oid, 'EXECUTE')
                FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
                WHERE n.nspname='public'
                  AND p.proname IN ('editor_commit','editor_undo')
                ORDER BY 1""")
            for name, svc, anon, auth in cur.fetchall():
                self.assertTrue(svc, f"{name}: ο service_role δεν μπορεί")
                self.assertFalse(anon, f"{name}: ο anon ΜΠΟΡΕΙ")
                self.assertFalse(auth, f"{name}: ο authenticated ΜΠΟΡΕΙ")


if __name__ == "__main__":
    unittest.main()
