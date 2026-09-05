"""Real Postgres proof for migration 0009 and the atomic billing RPC."""
from __future__ import annotations

import concurrent.futures
import time
import unittest
import uuid

import psycopg2

from tests.test_migration_chain import Postgres, apply_all, docker_ok


def add_client(dsn: str, client_id: str | None = None) -> str:
    client_id = client_id or str(uuid.uuid4())
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO clients(id,name,business_type,city,email) VALUES (%s,'Billing QA','service','Athens','qa@example.test')",
            (client_id,),
        )
    return client_id


def process(dsn: str, *, event_id: str, created: int, client_id: str,
            status: str = "trialing", customer: str | None = None,
            subscription: str | None = None) -> dict:
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT process_stripe_billing_event(
                 p_event_id => %s, p_event_type => 'customer.subscription.updated',
                 p_event_created => %s, p_client_id => %s,
                 p_customer_id => %s, p_subscription_id => %s,
                 p_price_id => 'price_1499', p_subscription_status => %s,
                 p_trial_start => %s, p_trial_end => %s,
                 p_period_start => %s, p_period_end => %s,
                 p_cancel_at_period_end => false)""",
            (event_id, created, client_id, customer or f"cus_{client_id}",
             subscription or f"sub_{client_id}", status,
             created, created + 30 * 86400, created, created + 30 * 86400),
        )
        return cur.fetchone()[0]


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class BillingMigrationPostgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pg = Postgres()
        cls.dsn = cls.pg.__enter__()
        apply_all(cls.dsn)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pg.__exit__()

    def test_schema_and_rpc_permissions(self):
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT relrowsecurity FROM pg_class WHERE oid='public.stripe_events'::regclass")
            self.assertTrue(cur.fetchone()[0])
            signature = ("process_stripe_billing_event(text,text,bigint,uuid,text,text,text,text,"
                         "bigint,bigint,bigint,bigint,boolean,bigint,bigint,text,text,text,text)")
            for role, expected in (("anon", False), ("authenticated", False),
                                   ("service_role", True)):
                cur.execute("SELECT has_function_privilege(%s, %s, 'EXECUTE')",
                            (role, signature))
                self.assertEqual(cur.fetchone()[0], expected, role)

    def test_duplicate_and_older_event_do_not_regress_state(self):
        client_id = add_client(self.dsn)
        newer = int(time.time())
        first = process(self.dsn, event_id=f"evt_new_{client_id}", created=newer,
                        client_id=client_id, status="active")
        duplicate = process(self.dsn, event_id=f"evt_new_{client_id}", created=newer,
                            client_id=client_id, status="unpaid")
        stale = process(self.dsn, event_id=f"evt_old_{client_id}", created=newer - 60,
                        client_id=client_id, status="unpaid")
        self.assertEqual(first["status"], "processed")
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(stale["status"], "ignored_stale")
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT status,last_stripe_event_id FROM subscriptions WHERE client_id=%s",
                        (client_id,))
            self.assertEqual(cur.fetchone(), ("active", f"evt_new_{client_id}"))

    def test_concurrent_duplicate_creates_one_transition(self):
        client_id = add_client(self.dsn)
        event_id = f"evt_concurrent_{client_id}"
        created = int(time.time())
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(
                lambda _: process(self.dsn, event_id=event_id, created=created,
                                  client_id=client_id), range(2)))
        self.assertEqual(sum(not r["duplicate"] for r in results), 1)
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM stripe_events WHERE stripe_event_id=%s", (event_id,))
            self.assertEqual(cur.fetchone()[0], 1)

    def test_failed_transition_rolls_back_and_same_event_retries(self):
        client_id = add_client(self.dsn)
        event_id = f"evt_retry_{client_id}"
        created = int(time.time())
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("""CREATE OR REPLACE FUNCTION fail_billing_test() RETURNS trigger
                           LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'intentional'; END $$""")
            cur.execute("""CREATE TRIGGER fail_billing_test_trigger BEFORE INSERT OR UPDATE
                           ON subscriptions FOR EACH ROW EXECUTE FUNCTION fail_billing_test()""")
        failed = process(self.dsn, event_id=event_id, created=created, client_id=client_id)
        self.assertFalse(failed["ok"])
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM subscriptions WHERE client_id=%s", (client_id,))
            self.assertEqual(cur.fetchone()[0], 0)
            cur.execute("DROP TRIGGER fail_billing_test_trigger ON subscriptions")
            cur.execute("DROP FUNCTION fail_billing_test()")
        retried = process(self.dsn, event_id=event_id, created=created, client_id=client_id)
        self.assertTrue(retried["ok"])
        self.assertFalse(retried["duplicate"])
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT processing_status,attempt_count FROM stripe_events WHERE stripe_event_id=%s",
                        (event_id,))
            self.assertEqual(cur.fetchone(), ("processed", 2))


@unittest.skipUnless(docker_ok(), "χρειάζεται Docker/Podman daemon")
class BillingUpgradePreservesRows(unittest.TestCase):
    def test_existing_0008_subscription_survives_0009(self):
        pg = Postgres()
        dsn = pg.__enter__()
        try:
            apply_all(dsn, upto="0008")
            client_id = add_client(dsn)
            with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
                cur.execute("""INSERT INTO subscriptions(
                               client_id,stripe_customer_id,stripe_sub_id,plan,status,current_period_end)
                               VALUES (%s,'cus_existing','sub_existing','site','active',now()+interval '5 days')""",
                            (client_id,))
            apply_all(dsn, skip=tuple(f"{n:04d}" for n in range(9)))
            with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
                cur.execute("""SELECT stripe_customer_id,stripe_sub_id,status,
                                      stripe_price_id,trial_end,cancel_at_period_end
                               FROM subscriptions WHERE client_id=%s""", (client_id,))
                self.assertEqual(cur.fetchone(),
                                 ("cus_existing", "sub_existing", "active", None, None, False))
        finally:
            pg.__exit__()


if __name__ == "__main__":
    unittest.main()
