"""
Η canonical ακολουθία migrations — κανόνες που πρέπει να ισχύουν χωρίς βάση.

Το `scripts/verify_sequence.py` αποδεικνύει το αποτέλεσμα σε πραγματικό Postgres
(container). Αυτά εδώ φυλάνε τους κανόνες που έκαναν την ενοποίηση απαραίτητη και
τρέχουν παντού, χωρίς Docker: ένα legacy αρχείο που ξαναμπαίνει στη σειρά, ή ο
Agency Kernel που χάνει τη σήμανση staging-only, δεν φαίνονται με το μάτι.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
MIGRATIONS = ROOT / "db" / "migrations"
LEGACY = MIGRATIONS / "legacy"
BASELINE = MIGRATIONS / "0000_production_baseline.sql"
KERNEL = MIGRATIONS / "0001_agency_kernel.sql"

NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")


def canonical() -> list[Path]:
    return sorted(p for p in MIGRATIONS.iterdir()
                  if p.suffix == ".sql" and NAME_RE.match(p.name))


class SequenceShapeTests(unittest.TestCase):
    def test_every_canonical_file_is_correctly_named(self):
        for path in MIGRATIONS.iterdir():
            if path.is_dir() or path.suffix != ".sql":
                continue
            self.assertRegex(path.name, NAME_RE, f"λάθος όνομα: {path.name}")

    def test_versions_are_unique_and_start_at_baseline(self):
        versions = [NAME_RE.match(p.name).group(1) for p in canonical()]
        self.assertEqual(len(versions), len(set(versions)), "διπλός αριθμός έκδοσης")
        self.assertEqual(versions[0], "0000", "η ακολουθία ξεκινά από το baseline")

    def test_legacy_is_history_not_sequence(self):
        """Ο runner διαβάζει MIGRATIONS/*.sql. Ένα legacy αρχείο που θα γύριζε
        πίσω στον φάκελο θα ξανάφτιαχνε πίνακες που αποσύρθηκαν."""
        self.assertTrue(LEGACY.is_dir())
        self.assertTrue(any(LEGACY.glob("*.sql")))
        for path in canonical():
            self.assertEqual(path.parent, MIGRATIONS)


class ProductionSafetyTests(unittest.TestCase):
    def test_kernel_is_marked_staging_only(self):
        """Χωρίς τη σήμανση, το επόμενο --apply --confirm-production θα έβαζε
        στην παραγωγή ημιτελές υποσύστημα."""
        self.assertIn("-- ENV: staging-only",
                      KERNEL.read_text(encoding="utf-8")[:200])

    def test_runner_honours_the_marker(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from scripts.migrate import _env_scope
        self.assertEqual(_env_scope(KERNEL), "staging-only")
        self.assertEqual(_env_scope(BASELINE), "all")

    def test_baseline_is_safe_to_re_run(self):
        sql = BASELINE.read_text(encoding="utf-8")
        for stmt in re.findall(r"^CREATE TABLE[^\n(]*", sql, re.M):
            self.assertIn("IF NOT EXISTS", stmt)
        for stmt in re.findall(r"^CREATE (?:UNIQUE )?INDEX[^\n(]*", sql, re.M):
            self.assertIn("IF NOT EXISTS", stmt)


class WithdrawnObjectsTests(unittest.TestCase):
    """Ο `site_variants` δημιουργούνταν επί μήνες χωρίς να τον διαβάζει κανείς."""

    def test_withdrawn_objects_are_not_recreated(self):
        for path in canonical():
            sql = path.read_text(encoding="utf-8")
            self.assertNotIn("site_variants", sql, f"{path.name}")
            self.assertNotIn("selected_layout", sql, f"{path.name}")

    def test_no_runtime_code_references_them(self):
        sources = list((ROOT / "src").rglob("*.py"))
        sources += list((ROOT / "sites" / "lib").rglob("*.js"))
        for path in sources:
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotRegex(text, r"table\(['\"]site_variants['\"]\)", str(path))
            self.assertNotIn("selected_layout", text, str(path))


class CriticalSchemaTests(unittest.TestCase):
    """Τρία πράγματα που, αν λείψουν από το baseline, σπάνε σιωπηλά."""

    def test_baseline_carries_the_claims_table_and_rpc(self):
        sql = BASELINE.read_text(encoding="utf-8")
        self.assertIn("client_site_claims", sql)
        # Η RPC έλειπε: το σχήμα περνούσε κάθε έλεγχο και το claim έσκαγε.
        self.assertIn("FUNCTION public.claim_client_site", sql)

    def test_claim_rpc_is_backend_only(self):
        sql = BASELINE.read_text(encoding="utf-8")
        signature = "FUNCTION public.claim_client_site(uuid, text, text)"
        self.assertIn(f"REVOKE ALL ON {signature} FROM PUBLIC, anon, authenticated", sql)
        self.assertIn(f"GRANT EXECUTE ON {signature} TO service_role", sql)

    def test_baseline_carries_design_persistence(self):
        sql = BASELINE.read_text(encoding="utf-8")
        block = sql.split('CREATE TABLE IF NOT EXISTS "sites"')[1].split(");")[0]
        for column in ("client_id", "preset", "html", "chosen_variant", "url"):
            self.assertIn(f'"{column}"', block)

    def test_kernel_evidence_is_append_only(self):
        sql = KERNEL.read_text(encoding="utf-8")
        self.assertIn("agency_events_append_only", sql)
        self.assertIn("agency_audit_log_append_only", sql)


if __name__ == "__main__":
    unittest.main()
