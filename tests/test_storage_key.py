"""Regression: ελληνικά ονόματα αρχείων πρέπει να ανεβαίνουν.

ΤΟ ΣΦΑΛΜΑ. Το Supabase Storage δέχεται μόνο ASCII κλειδιά. Το «βιτρίνα.png»
γύριζε 400 InvalidKey, το οποίο έβγαινε στον πελάτη ως 502 με εσωτερικό
μήνυμα. Για προϊόν ελληνικών επιχειρήσεων αυτό σημαίνει ότι ο ιδιοκτήτης που
φωτογραφίζει το μαγαζί του από ελληνικό κινητό δεν μπορούσε να ανεβάσει
φωτογραφία — το πιο βασικό βήμα του onboarding.

Μετρήθηκε ζωντανά: «shop photo.png» περνούσε, «βιτρίνα.png» όχι. Δηλαδή τα
κενά ήταν εντάξει και μόνο τα ελληνικά έσπαγαν — γι' αυτό δεν είχε φανεί.

    python -m unittest tests.test_storage_key
"""
import unittest

from src.db import _storage_key


class StorageKey(unittest.TestCase):


    def test_greek_becomes_latin(self):
        assert _storage_key("βιτρίνα.png") == "vitrina.png"
        assert _storage_key("Καφετέρια-Εξωτερικό.jpeg") == "kafeteria-exoteriko.jpeg"


    def test_spaces_and_symbols(self):
        assert _storage_key("αρχείο με κενά.png") == "archeio-me-kena.png"
        assert _storage_key("φωτό#1.PNG") == "foto-1.png"
        assert _storage_key("IMG_2024 (1).jpg") == "IMG_2024-1.jpg"


    def test_never_escapes_the_client_folder(self):
        """Το όνομα δεν επιτρέπεται να περιέχει διαδρομή — ούτε με backslash."""
        for name in ("../../../etc/passwd.png", "..\\..\\evil.png", "/abs/path.png"):
            key = _storage_key(name)
            assert "/" not in key and "\\" not in key and ".." not in key, key


    def test_degenerate_names_get_a_name(self):
        assert _storage_key(".png") == "arxeio.png"
        assert _storage_key("") == "arxeio.bin"
        assert _storage_key("...") == "arxeio.bin"


    def test_extension_is_kept_and_normalised(self):
        assert _storage_key("a.JPEG").endswith(".jpeg")
        assert _storage_key("a.tar.gz").endswith(".gz")


    def test_key_is_pure_ascii(self):
        """Ό,τι κι αν δοθεί, το κλειδί πρέπει να είναι ASCII — αλλιώς 400."""
        for name in ("ψητοπωλείο.jpg", "ΑΘΗΝΑ.PNG", "café☕.png", "日本語.png"):
            _storage_key(name).encode("ascii")   # σκάει αν δεν είναι


if __name__ == "__main__":
    unittest.main()
