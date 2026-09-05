"""Το email λογαριασμού ΔΕΝ γίνεται δημόσιο στοιχείο επικοινωνίας.

Η ΑΝΑΛΛΟΙΩΤΗ:

    Το `clients.email` δεν εμφανίζεται ΠΟΤΕ στο δημόσιο `/site-data`, εκτός αν
    ο πελάτης έγραψε ΡΗΤΑ την ίδια τιμή στο `site_content.email`.

ΤΙ ΕΣΠΑΣΕ. Το `_intake_from_db` ξεκινούσε με `email = clients.email`. Αυτό
όμως είναι η ταυτότητα λογαριασμού/χρέωσης — το γράφει το Stripe checkout
(`link_client_email`) και πάνω του στηρίζεται το login. Χωρίς καμία ενέργεια
του πελάτη τυπωνόταν στη δημόσια, indexable σελίδα του.

ΜΕΤΡΗΘΗΚΕ:
    clients.email        = private-billing@gmail.test
    site_content.email   = (κενό)
    φόρμα «Email (φαίνεται στο site)» = ΚΕΝΗ
    δημόσιο /site-data   = private-billing@gmail.test   ← σιωπηλή δημοσίευση

Ο πελάτης δεν μπορούσε ούτε να το δει ούτε να το σβήσει: το άδειασμα ενός ήδη
άδειου πεδίου δεν κάνει τίποτα.

ΔΥΟ ΠΕΔΙΑ, ΔΥΟ ΣΚΟΠΟΙ, ΚΑΜΙΑ ΓΕΦΥΡΑ:
    clients.email       → σύνδεση, χρέωση, ιδιοκτησία. Ιδιωτικό.
    site_content.email  → δημόσιο email επικοινωνίας. Το γράφει ο πελάτης.
"""
from __future__ import annotations

import json
import os
import unittest
import uuid

os.environ.setdefault("VITRINA_ENV", "staging")

from fastapi.testclient import TestClient  # noqa: E402

from src import auth, db, meta_oauth       # noqa: E402

API = TestClient(meta_oauth.app, raise_server_exceptions=False)

ACCOUNT_EMAIL = "private-billing@gmail.test"
PUBLIC_EMAIL = "info@business.gr"


class PublicEmailPrivacy(unittest.TestCase):

    def setUp(self):
        self.cid = str(uuid.uuid4())
        db._client().table("clients").insert({
            "id": self.cid, "name": "Δοκιμή Ιδιωτικότητας", "status": "active",
            "email": ACCOUNT_EMAIL, "business_type": "test",
            "city": "Αθήνα", "phone": "2100000000",
        }).execute()

    def tearDown(self):
        for table, col in (("site_content", "client_id"), ("clients", "id")):
            try:
                db._client().table(table).delete().eq(col, self.cid).execute()
            except Exception:  # noqa: BLE001
                pass

    # ── βοηθητικά ──────────────────────────────────────────────────────────
    def public(self) -> tuple[dict, str]:
        r = API.get(f"/clients/{self.cid}/site-data")
        self.assertEqual(r.status_code, 200, r.text[:200])
        return r.json().get("data", {}), r.text

    def set_public_email(self, value):
        content = db.get_site_content(self.cid) or {}
        content["email"] = value
        db.save_site_content(self.cid, content)

    def account_email(self) -> str:
        return (db.get_client(self.cid) or {}).get("email")

    # ── 1. κενό δημόσιο email → τίποτα δεν φαίνεται ────────────────────────
    def test_account_email_is_not_published_when_public_email_is_empty(self):
        data, blob = self.public()
        self.assertFalse(data.get("EMAIL"),
                         f"δημοσιεύτηκε email χωρίς ο πελάτης να το ζητήσει: "
                         f"{data.get('EMAIL')!r}")
        self.assertNotIn(ACCOUNT_EMAIL, blob,
                         "το email λογαριασμού διέρρευσε στο δημόσιο site-data")

    def test_account_email_absent_from_the_whole_public_payload(self):
        """Όχι μόνο από το πεδίο EMAIL — από ΟΛΟ το σώμα."""
        _, blob = self.public()
        for fragment in (ACCOUNT_EMAIL, ACCOUNT_EMAIL.split("@")[0],
                         ACCOUNT_EMAIL.split("@")[1]):
            self.assertNotIn(fragment.lower(), blob.lower(), fragment)

    # ── 2. ρητή επιλογή → δημοσιεύεται ─────────────────────────────────────
    def test_explicit_public_email_is_published(self):
        self.set_public_email(PUBLIC_EMAIL)
        data, blob = self.public()
        self.assertEqual(data.get("EMAIL"), PUBLIC_EMAIL)
        self.assertNotIn(ACCOUNT_EMAIL, blob,
                         "το email λογαριασμού εμφανίστηκε παράλληλα")

    # ── 3. σβήσιμο → εξαφανίζεται, ο λογαριασμός μένει ─────────────────────
    def test_clearing_public_email_removes_it_and_keeps_the_account(self):
        self.set_public_email(PUBLIC_EMAIL)
        self.assertEqual(self.public()[0].get("EMAIL"), PUBLIC_EMAIL)

        self.set_public_email("")
        data, blob = self.public()
        self.assertFalse(data.get("EMAIL"),
                         f"το δημόσιο email δεν έφυγε: {data.get('EMAIL')!r}")
        self.assertNotIn(ACCOUNT_EMAIL, blob,
                         "μετά το σβήσιμο ΞΑΝΑΓΥΡΙΣΕ το email λογαριασμού")
        self.assertEqual(self.account_email(), ACCOUNT_EMAIL,
                         "το σβήσιμο του δημόσιου πείραξε τον λογαριασμό")

    # ── 4. αλλαγή λογαριασμού → το δημόσιο δεν κουνιέται ───────────────────
    def test_changing_the_account_email_does_not_change_the_public_one(self):
        self.set_public_email(PUBLIC_EMAIL)
        db._client().table("clients").update(
            {"email": "another-billing@gmail.test"}).eq("id", self.cid).execute()
        data, blob = self.public()
        self.assertEqual(data.get("EMAIL"), PUBLIC_EMAIL)
        self.assertNotIn("another-billing", blob)

    def test_account_email_appearing_later_is_still_not_published(self):
        """Η ροή «site first»: ο πελάτης πληρώνει και το checkout γράφει το
        `clients.email` ΜΕΤΑ. Ούτε τότε δημοσιεύεται."""
        db._client().table("clients").update({"email": None}).eq(
            "id", self.cid).execute()
        self.assertFalse(self.public()[0].get("EMAIL"))
        db._client().table("clients").update(
            {"email": "paid-with-this@gmail.test"}).eq("id", self.cid).execute()
        data, blob = self.public()
        self.assertFalse(data.get("EMAIL"))
        self.assertNotIn("paid-with-this", blob)

    # ── 5. ρητή ταύτιση → επιτρέπεται ──────────────────────────────────────
    def test_customer_may_deliberately_publish_the_same_address(self):
        """Αν ο πελάτης γράψει ο ίδιος το email του λογαριασμού στο δημόσιο
        πεδίο, είναι επιλογή του και τη σεβόμαστε."""
        self.set_public_email(ACCOUNT_EMAIL)
        data, _ = self.public()
        self.assertEqual(data.get("EMAIL"), ACCOUNT_EMAIL)

    # ── 6. η φόρμα και το site λένε το ΙΔΙΟ πράγμα ─────────────────────────
    def test_dashboard_form_and_public_site_never_disagree(self):
        """Η καρδιά του bug ήταν η ασυμφωνία: κενή φόρμα, γεμάτο site."""
        from unittest.mock import patch
        for value in ("", PUBLIC_EMAIL, ""):
            self.set_public_email(value)
            with patch.object(auth, "current_email", return_value=ACCOUNT_EMAIL):
                form = API.get(f"/clients/{self.cid}/content",
                               headers={"Authorization": "Bearer t"}
                               ).json().get("content", {})
            shown = (form.get("email") or "")
            published = (self.public()[0].get("EMAIL") or "")
            self.assertEqual(shown, published,
                             f"η φόρμα δείχνει {shown!r} και το site {published!r}")


class NoOtherAccountEmailFallback(unittest.TestCase):
    """Στατικός φρουρός: ο δημόσιος intake δεν ξαναπαίρνει το email λογαριασμού."""

    def test_intake_builder_does_not_seed_account_email(self):
        import inspect
        src = inspect.getsource(meta_oauth._intake_from_db)
        body = "\n".join(l for l in src.splitlines()
                         if not l.strip().startswith("#"))
        self.assertNotIn('"email": c.get("email")', body,
                         "επέστρεψε το fallback από το clients.email")
        self.assertIn('"email": ""', body,
                      "το δημόσιο intake πρέπει να ξεκινά με ΚΕΝΟ email")

    def test_account_endpoint_still_shows_it_to_the_owner(self):
        """Ο ιδιοκτήτης ΠΡΕΠΕΙ να βλέπει το email του λογαριασμού του —
        η διόρθωση αφορά μόνο τη ΔΗΜΟΣΙΑ διαδρομή."""
        import inspect
        src = inspect.getsource(meta_oauth.get_account)
        self.assertIn('client.get("email")', src)


if __name__ == "__main__":
    unittest.main()
