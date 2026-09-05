"""Ο webhook δεν επιτρέπεται να εξαρτάται από τη μορφή του StripeObject.

ΓΙΑΤΙ ΥΠΑΡΧΕΙ. Το `requirements.txt` έλεγε `stripe>=8.0.0` χωρίς άνω όριο. Στο
stripe-python 12 το `StripeObject` έπαψε να είναι `dict` και έχασε το `.get()`.
Ο handler έκανε `obj.get("metadata", {})`, οπότε από τη στιγμή που το Railway
έχτισε με νεότερη έκδοση:

    customer.subscription.created  → AttributeError → HTTP 500 → retry → 500 …
    checkout.session.completed     → AttributeError → HTTP 500 → retry → 500 …

Δηλαδή: ΚΑΜΙΑ συνδρομή νέου πελάτη δεν αποθηκευόταν και ΚΑΝΕΝΑ email δεν
συνδεόταν. Ο πελάτης πλήρωνε €14.99 και έβλεπε άδειο dashboard για πάντα.
Το σφάλμα δεν φαινόταν σε κανένα test επειδή κανένα test δεν έστελνε
υπογεγραμμένο event στον πραγματικό handler.

Τα δύο tests εδώ κλειδώνουν το συμβόλαιο: το σώμα διαβάζεται από το JSON, και
η υπογραφή εξακολουθεί να επαληθεύεται.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("VITRINA_ENV", "staging")

from fastapi.testclient import TestClient  # noqa: E402

from src import config as cfg              # noqa: E402
from src.stripe_webhook import app, _transition  # noqa: E402

SECRET = cfg.STRIPE_WEBHOOK_SECRET or "whsec_" + "t" * 32
CID = "00000000-0000-4000-8000-000000000001"


def signed(event: dict, secret: str = SECRET, ts: int | None = None):
    body = json.dumps(event).encode()
    ts = ts or int(time.time())
    mac = hmac.new(secret.encode(), f"{ts}.".encode() + body,
                   hashlib.sha256).hexdigest()
    return body, {"stripe-signature": f"t={ts},v1={mac}",
                  "content-type": "application/json"}


def event(type_: str, obj: dict) -> dict:
    return {"id": "evt_contract", "object": "event", "type": type_,
            "api_version": "2024-06-20", "created": int(time.time()),
            "livemode": False, "pending_webhooks": 1,
            "request": {"id": None, "idempotency_key": None},
            "data": {"object": obj}}


class WebhookReadsPlainJson(unittest.TestCase):
    def test_subscription_period_supports_current_stripe_item_shape(self):
        ev = event("customer.subscription.updated", {
            "id": "sub_1", "customer": "cus_1", "status": "trialing",
            "metadata": {"client_id": CID},
            "items": {"data": [{
                "current_period_start": 1_700_000_000,
                "current_period_end": 1_702_592_000,
                "price": {"id": "price_x"},
            }]},
        })
        transition = _transition(ev, ev["data"]["object"])
        self.assertEqual(transition["current_period_start"], 1_700_000_000)
        self.assertEqual(transition["current_period_end"], 1_702_592_000)

    def test_malformed_tenant_metadata_is_rejected_before_rpc_cast(self):
        ev = event("customer.subscription.created", {
            "id": "sub_1", "customer": "cus_1", "status": "trialing",
            "metadata": {"client_id": "../../another-client"},
            "items": {"data": []},
        })
        transition = _transition(ev, ev["data"]["object"])
        self.assertIsNone(transition["client_id"])
        self.assertEqual(transition["disposition"], "ignored_malformed")

    def test_zero_trial_invoice_does_not_turn_trial_active(self):
        ev = event("invoice.paid", {
            "id": "in_trial", "customer": "cus_1", "subscription": "sub_1",
            "amount_paid": 0, "billing_reason": "subscription_create",
            "lines": {"data": [{"period": {"start": 10, "end": 20}}]},
        })
        self.assertEqual(_transition(ev, ev["data"]["object"])["status"], "trialing")

    def test_paid_cycle_invoice_activates_subscription(self):
        ev = event("invoice.paid", {
            "id": "in_paid", "customer": "cus_1", "subscription": "sub_1",
            "amount_paid": 1499, "billing_reason": "subscription_cycle",
            "lines": {"data": [{"period": {"start": 10, "end": 20}}]},
        })
        self.assertEqual(_transition(ev, ev["data"]["object"])["status"], "active")

    def test_new_customer_subscription_reaches_the_database(self):
        """Ο πρώτος πελάτης: δεν υπάρχει ακόμα γραμμή, το client_id έρχεται
        από τα metadata. Αυτό ακριβώς το μονοπάτι έσκαγε."""
        ev = event("customer.subscription.created", {
            "id": "sub_1", "object": "subscription", "customer": "cus_1",
            "status": "active", "metadata": {"client_id": CID},
            "items": {"data": [{"price": {"id": "price_x"}}]}})
        body, headers = signed(ev)
        with patch("src.stripe_webhook.process_stripe_billing_event",
                   return_value={"ok": True, "status": "processed"}) as process, \
             patch.object(cfg, "STRIPE_WEBHOOK_SECRET", SECRET):
            with TestClient(app, raise_server_exceptions=False) as client:
                r = client.post("/stripe/webhook", content=body, headers=headers)
        self.assertEqual(r.status_code, 200, r.text)
        process.assert_called_once()
        transition = process.call_args.args[0]
        self.assertEqual(transition["client_id"], CID)
        self.assertEqual(transition["customer_id"], "cus_1")
        self.assertEqual(transition["subscription_id"], "sub_1")
        self.assertEqual(transition["status"], "active")

    def test_checkout_links_the_purchase_email(self):
        ev = event("checkout.session.completed", {
            "id": "cs_1", "object": "checkout_session",
            "metadata": {"client_id": CID},
            "customer_details": {"email": "buyer@example.test"},
            "customer_email": None})
        body, headers = signed(ev)
        with patch("src.stripe_webhook.process_stripe_billing_event",
                   return_value={"ok": True, "status": "processed"}) as process, \
             patch.object(cfg, "STRIPE_WEBHOOK_SECRET", SECRET):
            with TestClient(app, raise_server_exceptions=False) as client:
                r = client.post("/stripe/webhook", content=body, headers=headers)
        self.assertEqual(r.status_code, 200, r.text)
        process.assert_called_once()
        transition = process.call_args.args[0]
        self.assertEqual(transition["client_id"], CID)
        self.assertEqual(transition["customer_email"], "buyer@example.test")

    def test_payload_comes_from_json_not_from_the_stripe_object(self):
        """Η αναλλοίωτη δεν είναι «μη χρησιμοποιείς .get» — σε απλό dict το
        `.get` είναι σωστό. Είναι η ΠΡΟΕΛΕΥΣΗ: το σώμα πρέπει να βγαίνει από
        `json.loads(payload)`, ώστε να μην εξαρτάται από την έκδοση του
        stripe-python. Αν κάποιος ξαναγράψει `event = construct_event(...)`
        και διαβάσει από εκεί, το σφάλμα επιστρέφει αυτούσιο."""
        with open("src/stripe_webhook.py", encoding="utf-8") as source:
            src = source.read()
        code = "\n".join(l for l in src.split("async def webhook", 1)[1].splitlines()
                         if not l.strip().startswith("#"))
        self.assertIn("event = json.loads(payload)", code,
                      "το σώμα πρέπει να διαβάζεται από το επαληθευμένο JSON")
        self.assertNotIn("= stripe.Webhook.construct_event", code,
                         "το construct_event επαληθεύει· δεν τροφοδοτεί δεδομένα")

    def test_signature_is_still_verified(self):
        ev = event("customer.subscription.created", {
            "id": "sub_1", "object": "subscription", "customer": "cus_1",
            "status": "active", "metadata": {"client_id": CID},
            "items": {"data": [{"price": {"id": "price_x"}}]}})
        body, _ = signed(ev, secret="whsec_" + "0" * 32)
        with patch.object(cfg, "STRIPE_WEBHOOK_SECRET", SECRET):
            with TestClient(app, raise_server_exceptions=False) as client:
                r = client.post(
                    "/stripe/webhook", content=body,
                    headers={"stripe-signature": "t=1,v1=bad",
                             "content-type": "application/json"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
