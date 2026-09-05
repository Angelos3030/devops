"""Ένα γεγονός Stripe για διαγραμμένο πελάτη ΔΕΝ δηλητηριάζει τον webhook.

ΤΟ ΣΦΑΛΜΑ ΠΟΥ ΜΠΛΟΚΑΡΕ ΤΗΝ ΕΚΔΟΣΗ. Έγκυρα υπογεγραμμένο event με `client_id`
που είναι σωστό uuid αλλά δεν υπάρχει πια στο `clients` έριχνε τον handler:

    stripe_events_client_id_fkey violated  →  HTTP 500

Το Stripe ξαναπροσπαθεί σε 5xx έως τρεις ημέρες και μετά ΑΠΕΝΕΡΓΟΠΟΙΕΙ το
endpoint. Τότε σταματά η επεξεργασία γεγονότων για ΟΛΟΥΣ τους πελάτες. Ένας
νόμιμα διαγραμμένος πελάτης (GDPR/admin) γινόταν δηλητήριο για όλο το billing.

Η λογική του RPC ήταν ήδη σωστή (`ignored_unknown` / `unknown_client`) — απλώς
το INSERT στο ledger γινόταν πριν από τον έλεγχο και έσκαγε στο FK. Το 0010
αφαιρεί το FK: ένα γεγονός είναι ιστορικό και επιβιώνει της οντότητας.

Ο πίνακας που κλειδώνεται εδώ:

    χωρίς client_id                → 2xx, μη ενεργήσιμο
    client_id όχι-uuid             → 2xx, μη ενεργήσιμο
    υπαρκτός client_id             → κανονική επεξεργασία
    έγκυρο uuid, ανύπαρκτος        → 2xx, ignored_unknown, ΚΑΜΙΑ μεταβολή
    replay του παραπάνω            → 2xx, καμία διπλή επίδραση
    παλαιό event άγνωστου πελάτη   → δεν αγγίζει καμία πραγματική συνδρομή
    ΑΚΥΡΗ υπογραφή + άγνωστος      → 400 · η υπογραφή ΔΕΝ παρακάμπτεται ποτέ
    event του Α δεν πειράζει τον Β
    πελάτης διαγράφεται → event μετά → ασφαλής τερματισμός, όχι 500
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import unittest
import uuid

os.environ.setdefault("VITRINA_ENV", "staging")

from fastapi.testclient import TestClient  # noqa: E402

from src import config as cfg, db          # noqa: E402
from src.stripe_webhook import app         # noqa: E402

C = TestClient(app, raise_server_exceptions=False)
ACCEPTED = {200, 202}


def sign(body: bytes, ts: int | None = None, secret: str | None = None) -> str:
    ts = ts or int(time.time())
    mac = hmac.new((secret or cfg.STRIPE_WEBHOOK_SECRET).encode(),
                   f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"


def event(eid: str, cid, status: str, created: int, cust: str, sub_id: str) -> dict:
    meta = {} if cid is None else {"client_id": cid}
    return {"id": eid, "object": "event", "api_version": "2024-06-20",
            "created": created, "livemode": False, "pending_webhooks": 1,
            "request": {"id": None, "idempotency_key": None},
            "type": "customer.subscription.updated",
            "data": {"object": {
                "id": sub_id, "object": "subscription", "customer": cust,
                "status": status, "metadata": meta,
                "current_period_start": created,
                "current_period_end": created + 30 * 86400,
                "items": {"data": [{"price": {"id": cfg.STRIPE_PRICE_SITE}}]}}}}


def post(ev: dict, *, raw_sig: str | None = None, secret: str | None = None):
    body = json.dumps(ev).encode()
    sig = raw_sig if raw_sig is not None else sign(body, secret=secret)
    return C.post("/stripe/webhook", content=body,
                  headers={"stripe-signature": sig,
                           "content-type": "application/json"})


def ledger(eid: str) -> dict | None:
    rows = (db._client().table("stripe_events")
            .select("stripe_event_id,processing_status,result_code,client_id,"
                    "attempt_count")
            .eq("stripe_event_id", eid).execute()).data or []
    return rows[0] if rows else None


def subs(cid: str) -> list[dict]:
    return (db._client().table("subscriptions").select("*")
            .eq("client_id", cid).execute()).data or []


class WebhookUnknownClient(unittest.TestCase):

    def setUp(self):
        self.run_id = uuid.uuid4().hex[:8]
        self.events: list[str] = []
        self.clients: list[str] = []

    def tearDown(self):
        for eid in self.events:
            try:
                db._client().table("stripe_events").delete().eq(
                    "stripe_event_id", eid).execute()
            except Exception:  # noqa: BLE001
                pass
        for cid in self.clients:
            for table, col in (("subscriptions", "client_id"), ("clients", "id")):
                try:
                    db._client().table(table).delete().eq(col, cid).execute()
                except Exception:  # noqa: BLE001
                    pass

    def make_client(self, name="RC unknown-client") -> str:
        cid = str(uuid.uuid4())
        db._client().table("clients").insert({
            "id": cid, "name": name, "status": "pending", "business_type": "test",
            "city": "RC-P1", "phone": "0000000000"}).execute()
        self.clients.append(cid)
        return cid

    def eid(self, tag: str) -> str:
        e = f"evt_p1_{self.run_id}_{tag}"
        self.events.append(e)
        return e

    # ── A ──────────────────────────────────────────────────────────────────
    def test_a_missing_client_id_is_terminal_and_safe(self):
        r = post(event(self.eid("a"), None, "active", int(time.time()),
                       f"cus_a_{self.run_id}", f"sub_a_{self.run_id}"))
        self.assertIn(r.status_code, ACCEPTED, r.text[:200])

    # ── B ──────────────────────────────────────────────────────────────────
    def test_b_malformed_client_id_is_terminal_and_safe(self):
        r = post(event(self.eid("b"), "όχι-uuid", "active", int(time.time()),
                       f"cus_b_{self.run_id}", f"sub_b_{self.run_id}"))
        self.assertIn(r.status_code, ACCEPTED, r.text[:200])

    # ── C ──────────────────────────────────────────────────────────────────
    def test_c_existing_client_is_processed_normally(self):
        cid = self.make_client()
        r = post(event(self.eid("c"), cid, "trialing", int(time.time()),
                       f"cus_c_{self.run_id}", f"sub_c_{self.run_id}"))
        self.assertIn(r.status_code, ACCEPTED, r.text[:200])
        rows = subs(cid)
        self.assertEqual(len(rows), 1, "η κανονική επεξεργασία δεν έγινε")
        self.assertEqual(rows[0]["status"], "trialing")
        led = ledger(self.eid("c").replace(f"_{self.run_id}_c", f"_{self.run_id}_c"))
        self.assertIsNotNone(led)
        self.assertEqual(led["processing_status"], "processed")

    # ── D ── ΤΟ ΣΦΑΛΜΑ ─────────────────────────────────────────────────────
    def test_d_valid_uuid_missing_client_is_ignored_not_500(self):
        ghost = str(uuid.uuid4())
        eid = self.eid("d")
        r = post(event(eid, ghost, "active", int(time.time()),
                       f"cus_d_{self.run_id}", f"sub_d_{self.run_id}"))
        self.assertIn(r.status_code, ACCEPTED,
                      f"ΔΗΛΗΤΗΡΙΟ: HTTP {r.status_code} {r.text[:160]}")
        led = ledger(eid)
        self.assertIsNotNone(led, "το γεγονός δεν καταγράφηκε στο ledger")
        self.assertEqual(led["processing_status"], "ignored_unknown")
        self.assertEqual(led["result_code"], "unknown_client")
        # Το αναγνωριστικό ΔΙΑΤΗΡΕΙΤΑΙ ως μεταδεδομένο ελέγχου.
        self.assertEqual(led["client_id"], ghost,
                         "χάθηκε το αναγνωριστικό του γεγονότος")
        # Καμία εφεύρεση οντότητας.
        self.assertEqual(subs(ghost), [], "δημιουργήθηκε συνδρομή από το πουθενά")
        rows = (db._client().table("clients").select("id")
                .eq("id", ghost).execute()).data or []
        self.assertEqual(rows, [], "δημιουργήθηκε πελάτης από το πουθενά")

    # ── E ──────────────────────────────────────────────────────────────────
    def test_e_replaying_the_unknown_client_event_stays_harmless(self):
        ghost = str(uuid.uuid4())
        eid = self.eid("e")
        ev = event(eid, ghost, "active", int(time.time()),
                   f"cus_e_{self.run_id}", f"sub_e_{self.run_id}")
        codes = [post(ev).status_code for _ in range(3)]
        self.assertTrue(all(c in ACCEPTED for c in codes), str(codes))
        led = ledger(eid)
        self.assertEqual(led["processing_status"], "ignored_unknown")
        self.assertEqual(led["attempt_count"], 1, "το replay πολλαπλασίασε προσπάθειες")
        self.assertEqual(subs(ghost), [])

    # ── F ──────────────────────────────────────────────────────────────────
    def test_f_old_unknown_client_event_cannot_touch_a_real_subscription(self):
        cid = self.make_client()
        now = int(time.time())
        post(event(self.eid("f1"), cid, "active", now, f"cus_f_{self.run_id}",
                   f"sub_f_{self.run_id}"))
        self.assertEqual(subs(cid)[0]["status"], "active")
        # ΠΑΛΙΟ event, ΑΓΝΩΣΤΟΣ πελάτης, ΙΔΙΟ stripe customer.
        ghost = str(uuid.uuid4())
        r = post(event(self.eid("f2"), ghost, "canceled", now - 3600,
                       f"cus_f_{self.run_id}", f"sub_f_{self.run_id}"))
        self.assertIn(r.status_code, ACCEPTED)
        self.assertEqual(subs(cid)[0]["status"], "active",
                         "άγνωστος πελάτης μετέβαλε πραγματική συνδρομή")

    # ── G ──────────────────────────────────────────────────────────────────
    def test_g_bad_signature_with_unknown_client_is_still_rejected(self):
        ghost = str(uuid.uuid4())
        ev = event(self.eid("g"), ghost, "active", int(time.time()),
                   f"cus_g_{self.run_id}", f"sub_g_{self.run_id}")
        self.assertEqual(post(ev, raw_sig="t=1,v1=deadbeef").status_code, 400)
        self.assertEqual(post(ev, secret="whsec_" + "0" * 32).status_code, 400)
        body = json.dumps(ev).encode()
        self.assertEqual(
            C.post("/stripe/webhook", content=body).status_code, 400)
        self.assertIsNone(ledger(self.eid("g")),
                          "μη επαληθευμένο γεγονός γράφτηκε στο ledger")

    # ── H ──────────────────────────────────────────────────────────────────
    def test_h_event_for_one_tenant_never_mutates_another(self):
        a, b = self.make_client("RC A"), self.make_client("RC B")
        now = int(time.time())
        post(event(self.eid("h1"), a, "active", now, f"cus_ha_{self.run_id}",
                   f"sub_ha_{self.run_id}"))
        post(event(self.eid("h2"), b, "trialing", now, f"cus_hb_{self.run_id}",
                   f"sub_hb_{self.run_id}"))
        self.assertEqual(subs(a)[0]["status"], "active")
        self.assertEqual(subs(b)[0]["status"], "trialing")
        self.assertEqual(subs(a)[0]["stripe_customer_id"], f"cus_ha_{self.run_id}")
        self.assertEqual(subs(b)[0]["stripe_customer_id"], f"cus_hb_{self.run_id}")

    # ── I ── η πραγματική ιστορία: GDPR διαγραφή, event αργότερα ───────────
    def test_i_event_after_legitimate_client_deletion_is_safe(self):
        cid = self.make_client("RC θα διαγραφεί")
        now = int(time.time())
        cust = f"cus_i_{self.run_id}"
        post(event(self.eid("i1"), cid, "active", now, cust, f"sub_i_{self.run_id}"))
        self.assertEqual(len(subs(cid)), 1)

        db.delete_client(cid)          # η ΠΡΑΓΜΑΤΙΚΗ διαδρομή διαγραφής
        gone = (db._client().table("clients").select("id")
                .eq("id", cid).execute()).data or []
        self.assertEqual(gone, [], "ο πελάτης δεν διαγράφηκε")

        r = post(event(self.eid("i2"), cid, "canceled", now + 60, cust,
                       f"sub_i_{self.run_id}"))
        self.assertIn(r.status_code, ACCEPTED,
                      f"ΔΗΛΗΤΗΡΙΟ μετά από διαγραφή: HTTP {r.status_code}")
        led = ledger(self.eid("i2"))
        self.assertEqual(led["processing_status"], "ignored_unknown")
        self.assertEqual(led["client_id"], cid,
                         "το ιστορικό έχασε ποιον αφορούσε το γεγονός")

    def test_i2_earlier_ledger_history_survives_the_deletion(self):
        """Το `ON DELETE SET NULL` ΕΣΒΗΝΕ ποιον αφορούσε κάθε παλιό γεγονός.
        Χωρίς FK, το ιστορικό μένει χρήσιμο για έλεγχο."""
        cid = self.make_client("RC ιστορικό")
        eid = self.eid("j")
        post(event(eid, cid, "active", int(time.time()), f"cus_j_{self.run_id}",
                   f"sub_j_{self.run_id}"))
        self.assertEqual(ledger(eid)["client_id"], cid)
        db.delete_client(cid)
        self.assertEqual(ledger(eid)["client_id"], cid,
                         "η διαγραφή έσβησε το αναγνωριστικό από το ιστορικό")


class LedgerHasNoForeignKey(unittest.TestCase):
    """Στατικός φρουρός: αν κάποιος επαναφέρει το FK, το δηλητήριο γυρνά."""

    def test_stripe_events_client_id_has_no_foreign_key(self):
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv()
        dsn = os.environ.get("DATABASE_URL_STAGING")
        if not dsn:
            self.skipTest("λείπει το DATABASE_URL_STAGING")
        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT con.conname FROM pg_constraint con
                    JOIN pg_class r ON r.oid = con.conrelid
                    JOIN pg_namespace n ON n.oid = r.relnamespace
                    WHERE n.nspname='public' AND r.relname='stripe_events'
                      AND con.contype='f'""")
                fks = [r[0] for r in cur.fetchall()]
        finally:
            conn.close()
        self.assertEqual(fks, [],
                         "το ledger ξαναπέκτησε foreign key — το event για "
                         "διαγραμμένο πελάτη θα ξαναρίξει τον webhook")


if __name__ == "__main__":
    unittest.main()
