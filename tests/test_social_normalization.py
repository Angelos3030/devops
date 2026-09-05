"""Τα social του πελάτη δεν χάνονται, και δεν γίνονται φορέας phishing.

ΤΙ ΕΣΠΑΣΕ ΚΑΙ ΓΙΑΤΙ ΓΡΑΦΤΗΚΕ ΑΥΤΟ. Ο φρουρός URL δεχόταν ΜΟΝΟ `^https?://`.
Σωστό για `javascript:`/`data:`, καταστροφικό για τον πελάτη: το dashboard του
λέει να γράψει «instagram.com/tomagazimou» (κυριολεκτικά το placeholder) και
μετά το πετούσε σιωπηλά — HTTP 200, πεδίο κενό, καμία ένδειξη.

ΜΕΤΡΗΘΗΚΕ σε staging: 27 γραμμές `site_content`, **μηδέν** αποθηκευμένα social.
Χάνονταν όλα, από κάθε πελάτη.

Δύο αναλλοίωτες, και οι δύο πρέπει να ισχύουν ταυτόχρονα:

  1. Ό,τι γράφει πραγματικά ο κόσμος ΚΑΝΟΝΙΚΟΠΟΙΕΙΤΑΙ, δεν χάνεται.
  2. Ό,τι είναι επικίνδυνο ή ξένο ΑΠΟΡΡΙΠΤΕΤΑΙ με σφάλμα — ποτέ «σχεδόν
     σωστό URL», ποτέ σιωπηλά κενό.

Ο έλεγχος host δεν είναι υπερβολή: το `SocialLinks.jsx` αποδίδει αυτά τα πεδία
με το ΕΙΚΟΝΙΔΙΟ της πλατφόρμας. Σύνδεσμος με το γλυφικό του Instagram που πάει
αλλού είναι phishing — το εικονίδιο είναι ο ισχυρισμός.
"""
from __future__ import annotations

import os
import unittest

os.environ.setdefault("VITRINA_ENV", "staging")

from src.meta_oauth import (SocialValueError, normalize_social,  # noqa: E402
                            _safe_url)


class AcceptsWhatPeopleActuallyType(unittest.TestCase):

    def test_instagram(self):
        for raw, want in (
            ("@kafedokimi", "https://instagram.com/kafedokimi"),
            ("instagram.com/kafedokimi", "https://instagram.com/kafedokimi"),
            ("www.instagram.com/kafedokimi",
             "https://www.instagram.com/kafedokimi"),
            ("https://instagram.com/kafedokimi",
             "https://instagram.com/kafedokimi"),
            ("http://instagram.com/kafedokimi",
             "https://instagram.com/kafedokimi"),          # αναβάθμιση σε https
            ("kafedokimi", "https://instagram.com/kafedokimi"),
            ("INSTAGRAM.COM/Kafe", "https://instagram.com/Kafe"),
            ("/instagram.com/kafedokimi", "https://instagram.com/kafedokimi"),
        ):
            self.assertEqual(normalize_social("instagram", raw), want, raw)

    def test_facebook(self):
        for raw, want in (
            ("@kafedokimi", "https://facebook.com/kafedokimi"),
            ("facebook.com/kafedokimi", "https://facebook.com/kafedokimi"),
            ("www.facebook.com/kafedokimi",
             "https://www.facebook.com/kafedokimi"),
            ("https://facebook.com/kafedokimi",
             "https://facebook.com/kafedokimi"),
            ("fb.com/kafedokimi", "https://fb.com/kafedokimi"),
            ("m.facebook.com/kafedokimi", "https://m.facebook.com/kafedokimi"),
        ):
            self.assertEqual(normalize_social("facebook", raw), want, raw)

    def test_whitespace_is_trimmed(self):
        for raw in ("  @kafedokimi  ", "\t@kafedokimi\n",
                    "  instagram.com/kafedokimi  "):
            self.assertEqual(normalize_social("instagram", raw),
                             "https://instagram.com/kafedokimi", repr(raw))

    def test_empty_stays_empty(self):
        """Ο πελάτης έσβησε το πεδίο — έγκυρη πρόθεση, όχι σφάλμα."""
        for raw in ("", "   ", None):
            self.assertEqual(normalize_social("instagram", raw), "")


class RejectsDangerousAndForeign(unittest.TestCase):

    def test_dangerous_schemes(self):
        for raw in ("javascript:alert(1)", "JavaScript:alert(1)",
                    "  javascript:alert(1)", "data:text/html,<script>x</script>",
                    "vbscript:msgbox(1)", "file:///etc/passwd",
                    "ftp://instagram.com/x", "mailto:a@b.gr",
                    "tel:+302100000000"):
            for field in ("instagram", "facebook"):
                with self.assertRaises(SocialValueError, msg=f"{field}: {raw}"):
                    normalize_social(field, raw)

    def test_dangerous_scheme_is_never_silently_transformed(self):
        """Ρητή επικίνδυνη πρόθεση δεν «διορθώνεται» σε https://javascript:…"""
        for raw in ("javascript:alert(1)", "data:text/html,x"):
            with self.assertRaises(SocialValueError):
                normalize_social("instagram", raw)

    def test_foreign_hosts(self):
        for raw in ("evil.example/kafe", "https://evil.example",
                    "https://instagram.com.evil.example/kafe",
                    "instagram.evil.example/kafe"):
            with self.assertRaises(SocialValueError, msg=raw):
                normalize_social("instagram", raw)

    def test_platform_fields_do_not_cross(self):
        with self.assertRaises(SocialValueError):
            normalize_social("facebook", "instagram.com/kafe")
        with self.assertRaises(SocialValueError):
            normalize_social("instagram", "facebook.com/kafe")

    def test_malformed(self):
        for raw in ("instagram.com", "https://instagram.com/", "@",
                    "@κακό χρήστης", "@a b", "instagram.com/<script>",
                    'instagram.com/a"b', "@" + "x" * 80):
            with self.assertRaises(SocialValueError, msg=raw):
                normalize_social("instagram", raw)

    def test_error_message_tells_the_customer_what_to_type(self):
        for raw in ("javascript:alert(1)", "evil.example/x", "instagram.com"):
            try:
                normalize_social("instagram", raw)
                self.fail(f"δεν απορρίφθηκε: {raw}")
            except SocialValueError as e:
                self.assertIn("instagram.com", str(e).lower(),
                              f"το μήνυμα δεν λέει τι να γράψει: {e}")


class SecurityGuardIsIntact(unittest.TestCase):
    """Ο παλιός φρουρός δεν χαλάρωσε — απλώς δεν είναι πια η μόνη πύλη."""

    def test_safe_url_still_rejects_non_http(self):
        for raw in ("javascript:alert(1)", "data:text/html,x", "vbscript:x",
                    "file:///etc/passwd", "instagram.com/x", "@handle"):
            self.assertEqual(_safe_url(raw), "", raw)

    def test_gbp_url_contract_unchanged(self):
        """Το `gbp_url` ΔΕΝ είναι πεδίο πλατφόρμας: μένει ελεύθερο http/https
        (Google Maps, short links, g.page). Δεν το άγγιξε αυτή η αλλαγή."""
        from src.meta_oauth import _SOCIAL_HOSTS, _URL_FIELDS
        self.assertIn("gbp_url", _URL_FIELDS)
        self.assertNotIn("gbp_url", _SOCIAL_HOSTS)
        self.assertEqual(_safe_url("https://g.page/kafe"), "https://g.page/kafe")


class ApiRejectsInsteadOfSilentlyDropping(unittest.TestCase):
    """Η καρδιά του bug: 200 + κενό πεδίο. Πρέπει να είναι 422 + μήνυμα."""

    def test_write_path_raises_http_422(self):
        import inspect

        from src import meta_oauth
        src = inspect.getsource(meta_oauth.put_content)
        self.assertIn("normalize_social", src,
                      "η διαδρομή εγγραφής δεν κανονικοποιεί")
        self.assertIn("422", src, "η αποτυχία δεν επιστρέφει σφάλμα στον πελάτη")

    def test_dashboard_placeholders_are_accepted_values(self):
        """Ό,τι λέει η φόρμα στον πελάτη να γράψει, πρέπει να δουλεύει.

        Αυτό ήταν το πιο καταδικαστικό μέρος του bug: το placeholder ζητούσε
        ακριβώς τη μορφή που πετιόταν."""
        from pathlib import Path
        import re
        page = Path("sites/app/dashboard/page.jsx").read_text(encoding="utf-8")
        found = dict(re.findall(
            r"setField\('(facebook|instagram)'\)[^>]*?placeholder=\"([^\"]+)\"",
            page, re.S))
        self.assertEqual(set(found), {"facebook", "instagram"},
                         f"δεν βρέθηκαν τα placeholders: {found}")
        for field, placeholder in found.items():
            self.assertTrue(
                normalize_social(field, placeholder).startswith("https://"),
                f"το placeholder «{placeholder}» του {field} ΔΕΝ γίνεται δεκτό")


if __name__ == "__main__":
    unittest.main()
