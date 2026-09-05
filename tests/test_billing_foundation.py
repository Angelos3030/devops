"""Deterministic billing policy, checkout security and Stripe contract tests."""
from __future__ import annotations

import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

os.environ.setdefault("VITRINA_ENV", "staging")

import stripe  # noqa: E402
from fastapi import HTTPException  # noqa: E402

from src import billing, config as cfg  # noqa: E402
from src.meta_oauth import CheckoutRequest, billing_portal, create_checkout  # noqa: E402


NOW = datetime(2026, 9, 5, 12, tzinfo=timezone.utc)


class BillingEntitlementPolicy(unittest.TestCase):
    def test_trialing_and_active_have_full_access(self):
        for status in ("trialing", "active"):
            with self.subTest(status=status):
                self.assertTrue(billing.entitlement({"status": status}, now=NOW)["entitled"])

    def test_past_due_has_exact_seven_day_grace(self):
        failed = NOW - timedelta(days=6, hours=23)
        allowed = billing.entitlement(
            {"status": "past_due", "first_payment_failed_at": failed}, now=NOW)
        denied = billing.entitlement(
            {"status": "past_due", "first_payment_failed_at": NOW - timedelta(days=7)}, now=NOW)
        self.assertTrue(allowed["entitled"])
        self.assertEqual(allowed["reason"], "past_due_grace")
        self.assertFalse(denied["entitled"])
        self.assertTrue(denied["data_preserved"])

    def test_canceled_access_uses_ended_at_as_authority(self):
        sub = {
            "status": "canceled",
            "ended_at": NOW - timedelta(seconds=1),
            "current_period_end": NOW + timedelta(days=20),
        }
        result = billing.entitlement(sub, now=NOW)
        self.assertFalse(result["entitled"])
        self.assertEqual(result["reason"], "canceled_effective")

    def test_canceled_at_period_end_keeps_access(self):
        result = billing.entitlement({
            "status": "canceled", "current_period_end": NOW + timedelta(days=2)
        }, now=NOW)
        self.assertTrue(result["entitled"])

    def test_non_entitled_states_preserve_data(self):
        for status in ("unpaid", "incomplete", "incomplete_expired", "paused"):
            with self.subTest(status=status):
                result = billing.entitlement({"status": status}, now=NOW)
                self.assertFalse(result["entitled"])
                self.assertTrue(result["data_preserved"])


class StripeConfiguration(unittest.TestCase):
    def test_sdk_object_is_converted_before_field_access(self):
        price = stripe.Price.construct_from({
            "id": "price_test", "livemode": False, "currency": "eur",
            "unit_amount": 1499, "active": True,
            "recurring": {"interval": "month", "interval_count": 1},
        }, "sk_test_x")
        with patch.object(cfg, "STRIPE_SECRET_KEY", "sk_test_example"), \
             patch.object(cfg, "STRIPE_WEBHOOK_SECRET", "whsec_example"), \
             patch.object(cfg, "STRIPE_PRICE_SITE", "price_test"), \
             patch("src.billing.env.stripe_mode", return_value="test"), \
             patch("src.billing.stripe.Price.retrieve", return_value=price):
            result = billing.validate_runtime_configuration(retrieve_price=True)
        self.assertEqual(result["amount_cents"], 1499)

    def test_mixed_live_and_test_configuration_fails_closed(self):
        with patch.object(cfg, "STRIPE_SECRET_KEY", "sk_live_example"), \
             patch.object(cfg, "STRIPE_WEBHOOK_SECRET", "whsec_example"), \
             patch.object(cfg, "STRIPE_PRICE_SITE", "price_test"), \
             patch("src.billing.env.stripe_mode", return_value="test"):
            with self.assertRaisesRegex(RuntimeError, "sk_test"):
                billing.validate_runtime_configuration()


class CheckoutSecurity(unittest.TestCase):
    def test_anonymous_and_cross_tenant_are_rejected_before_stripe(self):
        for error in (HTTPException(401, "login"), HTTPException(404, "not found")):
            with self.subTest(status=error.status_code), \
                 patch("src.meta_oauth.auth.require_client_access", side_effect=error), \
                 patch("src.meta_oauth.stripe.checkout.Session.create") as create:
                with self.assertRaises(HTTPException) as raised:
                    create_checkout(CheckoutRequest(client_id="tenant-b"), None)
                self.assertEqual(raised.exception.status_code, error.status_code)
                create.assert_not_called()

    def test_server_owns_price_trial_and_tenant_metadata(self):
        session = type("Session", (), {"url": "https://checkout.stripe.test/session"})()
        with patch("src.meta_oauth.auth.require_client_access",
                   return_value={"id": "tenant-a", "email": "owner@example.test"}), \
             patch("src.billing.validate_runtime_configuration"), \
             patch("src.meta_oauth.stripe.checkout.Session.create", return_value=session) as create, \
             patch.object(cfg, "STRIPE_PRICE_SITE", "price_server_owned"):
            result = create_checkout(CheckoutRequest(client_id="tenant-a"), "Bearer valid")
        args = create.call_args.kwargs
        self.assertEqual(args["mode"], "subscription")
        self.assertEqual(args["payment_method_collection"], "always")
        self.assertEqual(args["line_items"], [{"price": "price_server_owned", "quantity": 1}])
        self.assertEqual(args["subscription_data"]["trial_period_days"], 30)
        self.assertEqual(args["metadata"]["client_id"], "tenant-a")
        self.assertEqual(result["amount_due_today"], 0)
        self.assertEqual(result["recurring_amount_cents"], 1499)

    def test_cross_tenant_cannot_open_billing_portal(self):
        with patch("src.meta_oauth.auth.require_client_access",
                   side_effect=HTTPException(404, "not found")), \
             patch("src.meta_oauth.stripe.billing_portal.Session.create") as create:
            with self.assertRaises(HTTPException) as raised:
                billing_portal("tenant-b", "Bearer tenant-a")
        self.assertEqual(raised.exception.status_code, 404)
        create.assert_not_called()

    def test_checkout_response_never_exposes_stripe_secrets(self):
        session = type("Session", (), {"url": "https://checkout.stripe.test/session"})()
        with patch("src.meta_oauth.auth.require_client_access",
                   return_value={"id": "tenant-a", "email": "owner@example.test"}), \
             patch("src.billing.validate_runtime_configuration"), \
             patch("src.meta_oauth.stripe.checkout.Session.create", return_value=session):
            result = create_checkout(CheckoutRequest(client_id="tenant-a"), "Bearer valid")
        blob = str(result).lower()
        self.assertNotIn("sk_test_", blob)
        self.assertNotIn("whsec_", blob)


if __name__ == "__main__":
    unittest.main()
