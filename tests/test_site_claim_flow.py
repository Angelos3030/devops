"""Ownership hand-off contracts for site-first onboarding."""

import hashlib
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from src import meta_oauth


class SiteClaimFlowTests(unittest.TestCase):
    def test_claim_uses_authenticated_email_and_hashes_token(self):
        raw = "a" * 43
        seen = {}

        def fake_claim(client_id, token_hash, email):
            seen.update(client_id=client_id, token_hash=token_hash, email=email)
            return True

        with patch.object(meta_oauth.auth, "current_email", return_value="Owner@Example.GR"), \
             patch.object(meta_oauth.db, "claim_client_site", side_effect=fake_claim):
            result = meta_oauth.claim_site(
                "11111111-1111-1111-1111-111111111111",
                meta_oauth.ClaimSite(token=raw),
                "Bearer verified-token",
            )

        self.assertTrue(result["ok"])
        self.assertEqual(seen["email"], "Owner@Example.GR")
        self.assertEqual(seen["token_hash"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertNotIn(raw, seen.values())

    def test_claim_rejects_short_or_consumed_tokens(self):
        with patch.object(meta_oauth.auth, "current_email", return_value="owner@example.gr"):
            with self.assertRaises(HTTPException) as short:
                meta_oauth.claim_site(
                    "client", meta_oauth.ClaimSite(token="short"), "Bearer token")
            self.assertEqual(short.exception.status_code, 400)

            with patch.object(meta_oauth.db, "claim_client_site", return_value=False):
                with self.assertRaises(HTTPException) as consumed:
                    meta_oauth.claim_site(
                        "client", meta_oauth.ClaimSite(token="x" * 43), "Bearer token")
                self.assertEqual(consumed.exception.status_code, 404)

    def test_frontend_claim_contract_is_private_and_persistent(self):
        with open("web/start.html", encoding="utf-8") as handle:
            start = handle.read()
        with open("sites/app/choose/[client]/page.jsx", encoding="utf-8") as handle:
            choose = handle.read()
        with open("sites/app/dashboard/page.jsx", encoding="utf-8") as handle:
            dashboard = handle.read()

        self.assertIn("#claim=", start)
        self.assertIn("sessionStorage.setItem(`vitrina-claim:${client}`", choose)
        self.assertIn("history.replaceState", choose)
        self.assertIn("sessionStorage.getItem(claimKey)", dashboard)
        self.assertIn("`/clients/${fromUrl}/claim`", dashboard)
        self.assertIn("sessionStorage.removeItem(claimKey)", dashboard)
        self.assertIn("/clients/lookup", dashboard)
        self.assertIn("clients?.length > 1", dashboard)


if __name__ == "__main__":
    unittest.main()
