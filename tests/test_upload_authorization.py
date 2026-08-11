"""Authorization contracts for customer asset uploads."""

import hashlib
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from src import main


class UploadAuthorizationTests(unittest.TestCase):
    def test_authenticated_owner_is_allowed(self):
        with patch.object(main.auth, "require_client_access") as require:
            main._require_upload_access("client-1", "Bearer valid", "")
        require.assert_called_once_with("client-1", "Bearer valid")

    def test_valid_onboarding_claim_is_allowed(self):
        raw = "x" * 43
        with patch.object(main.db, "valid_client_claim", return_value=True) as valid:
            main._require_upload_access("client-1", None, raw)
        valid.assert_called_once_with(
            "client-1", hashlib.sha256(raw.encode()).hexdigest())

    def test_missing_or_invalid_claim_is_rejected(self):
        with self.assertRaises(HTTPException) as missing:
            main._require_upload_access("client-1", None, "")
        self.assertEqual(missing.exception.status_code, 401)

        with patch.object(main.db, "valid_client_claim", return_value=False):
            with self.assertRaises(HTTPException) as invalid:
                main._require_upload_access("client-1", None, "x" * 43)
        self.assertEqual(invalid.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
