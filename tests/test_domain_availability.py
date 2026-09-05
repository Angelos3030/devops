"""Η διαθεσιμότητα δεν επιτρέπεται να μαντεύεται.

Δύο κανόνες που κοστίζουν χρήματα σε πελάτη αν σπάσουν:

  1. Η απάντηση έρχεται από ΑΥΘΕΝΤΙΚΗ πηγή — το μητρώο (RDAP) ή registrar API.
     Ποτέ από DNS: παρκαρισμένο domain δεν έχει DNS και φαινόταν ελεύθερο.
  2. Αποτυχία παρόχου ΔΕΝ σημαίνει «ελεύθερο». Timeout, 5xx, 429, πτώση
     δικτύου, απρόσμενη εξαίρεση — όλα δίνουν `unknown`.

Τα tests τρέχουν ΧΩΡΙΣ δίκτυο: κάθε κλήση είναι mock, ώστε να μη γίνουν ποτέ
κόκκινα επειδή έπεσε ένα μητρώο.
"""
from __future__ import annotations

import socket
import unittest
import urllib.error
from unittest.mock import patch

from src import domain_availability as av

BOOT = {"com": "https://rdap.verisign.com/com/v1",
        "org": "https://rdap.publicinterestregistry.org/rdap"}


class _Resp:
    status = 200

    def read(self):
        return b"{}"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http(code: int):
    return urllib.error.HTTPError("u", code, "x", {}, None)


class Normalisation(unittest.TestCase):
    def test_noise_is_stripped(self):
        for raw in ("  https://WWW.Mitsos.GR/menu?a=1 ", "MITSOS.GR.",
                    "info@mitsos.gr", "mitsos.gr:8080", "http://mitsos.gr#x"):
            self.assertEqual(av.normalize_domain(raw)[0], "mitsos.gr", raw)

    def test_greek_becomes_punycode_but_display_stays_greek(self):
        puny, display = av.normalize_domain("Καφέ-Μήτσος.GR")
        self.assertTrue(puny.startswith("xn--"), puny)
        self.assertEqual(display, "καφέ-μήτσος.gr")

    def test_same_name_two_unicode_forms_give_one_punycode(self):
        """Χωρίς NFC, δύο οπτικά ίδια κείμενα θα έδιναν διαφορετικό punycode —
        και το «ένα ανοιχτό αίτημα ανά domain» θα έσπαγε σιωπηλά."""
        import unicodedata
        a = "καφέ.gr"
        b = unicodedata.normalize("NFD", a)
        self.assertNotEqual(a, b)
        self.assertEqual(av.normalize_domain(a)[0], av.normalize_domain(b)[0])

    def test_invalid_input_is_rejected(self):
        for raw in ("", "   ", ".gr", "a..gr", "-x.gr", "x-.gr", "mitsos",
                    "../../etc/passwd.gr", "a" * 70 + ".gr", "ελ", None, 42):
            with self.assertRaises(av.InvalidDomain, msg=repr(raw)):
                av.normalize_domain(raw)


class AuthoritativeAnswers(unittest.TestCase):
    def setUp(self):
        self.boot = patch.object(av, "_bootstrap", return_value=BOOT)
        self.boot.start()
        self.addCleanup(self.boot.stop)

    def test_registry_has_record_means_taken(self):
        with patch("urllib.request.urlopen", return_value=_Resp()):
            r = av.check("google.com")
        self.assertEqual(r.status, av.UNAVAILABLE)
        self.assertTrue(r.source.startswith("rdap:"), r.source)

    def test_registry_404_means_free(self):
        with patch("urllib.request.urlopen", side_effect=_http(404)):
            r = av.check("definitely-free-9f3k2.com")
        self.assertEqual(r.status, av.AVAILABLE)

    def test_result_carries_source_and_time(self):
        with patch("urllib.request.urlopen", side_effect=_http(404)):
            r = av.check("x-9f3k2.com")
        self.assertTrue(r.checked_at)
        self.assertIn("rdap", r.source)


class FailureIsNeverAvailable(unittest.TestCase):
    """Ο κανόνας που, αν σπάσει, χρεώνει τον πελάτη για ξένο domain."""

    def setUp(self):
        self.boot = patch.object(av, "_bootstrap", return_value=BOOT)
        self.boot.start()
        self.addCleanup(self.boot.stop)

    def test_every_provider_failure_gives_unknown(self):
        for label, exc in (
            ("timeout", socket.timeout("timed out")),
            ("503", _http(503)),
            ("502", _http(502)),
            ("429", _http(429)),
            ("403", _http(403)),
            ("network", urllib.error.URLError("no route")),
            ("unexpected", ValueError("boom")),
        ):
            with patch("urllib.request.urlopen", side_effect=exc):
                r = av.check("some-name-9f3k2.com")
            self.assertEqual(r.status, av.UNKNOWN, label)
            self.assertNotEqual(r.status, av.AVAILABLE, label)

    def test_missing_bootstrap_gives_unknown(self):
        with patch.object(av, "_bootstrap", return_value={}):
            r = av.check("anything-9f3k2.com")
        self.assertEqual(r.status, av.UNKNOWN)

    def test_tld_without_rdap_and_without_registrar_is_unknown(self):
        """Το .gr δεν έχει ούτε RDAP ούτε WHOIS (επαληθευμένο στο IANA).
        Χωρίς ρυθμισμένο registrar η μόνη τίμια απάντηση είναι «δεν ξέρω»."""
        from src import config as cfg
        with patch.object(cfg, "DOMAIN_REGISTRAR", "dns"):
            r = av.check("kati-9f3k2.gr")
        self.assertEqual(r.status, av.UNKNOWN)
        self.assertTrue(r.reason)

    def test_registrar_exception_gives_unknown(self):
        from src import config as cfg
        from src import registrars
        with patch.object(cfg, "DOMAIN_REGISTRAR", "pointer"), \
             patch.object(registrars, "get_registrar",
                          side_effect=RuntimeError("creds missing")):
            r = av.check("kati-9f3k2.gr")
        self.assertEqual(r.status, av.UNKNOWN)


class DnsGuessIsGone(unittest.TestCase):
    def test_dns_registrar_no_longer_decides(self):
        from src import registrars
        rows = registrars.DnsRegistrar().check_availability(["oti-nanai.gr"])
        self.assertIsNone(rows[0]["available"])

    def test_no_doh_lookup_left_in_the_code(self):
        src = open("src/registrars.py", encoding="utf-8").read()
        self.assertNotIn("dns-query", src)
        self.assertNotIn("cloudflare-dns", src)


class BatchIsResilient(unittest.TestCase):
    def test_one_invalid_name_does_not_sink_the_list(self):
        with patch.object(av, "_bootstrap", return_value=BOOT), \
             patch("urllib.request.urlopen", side_effect=_http(404)):
            out = av.check_many(["good-9f3k2.com", "-bad-", "other-9f3k2.com"])
        kinds = [o.status if hasattr(o, "status") else o["status"] for o in out]
        self.assertEqual(kinds, [av.AVAILABLE, "invalid", av.AVAILABLE])


if __name__ == "__main__":
    unittest.main()
