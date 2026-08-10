import unittest
from pathlib import Path


SQL = (Path(__file__).parents[1] / "db" / "migrations" /
       "0008_agency_kernel.sql").read_text(encoding="utf-8")


class AgencyMigrationTests(unittest.TestCase):
    def test_kernel_tables_and_action_queue_exist(self):
        for name in (
            "agent_registry", "agent_installations", "workspace_entitlements",
            "agent_tasks", "agent_runs", "agent_approvals", "agent_artifacts",
            "agency_events", "kpi_snapshots", "agency_audit_log",
            "agency_action_queue",
        ):
            self.assertIn(name, SQL)

    def test_no_agents_or_installations_are_seeded(self):
        self.assertNotIn("INSERT INTO agent_registry", SQL)
        self.assertNotIn("INSERT INTO agent_installations", SQL)

    def test_evidence_is_append_only(self):
        self.assertIn("agency_events_append_only", SQL)
        self.assertIn("agency_audit_log_append_only", SQL)

    def test_new_tables_enable_rls(self):
        self.assertIn("ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY", SQL)
        self.assertIn("ALTER TABLE agency_audit_log ENABLE ROW LEVEL SECURITY", SQL)


if __name__ == "__main__":
    unittest.main()
