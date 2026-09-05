# -*- coding: utf-8 -*-
"""Το ίδιο κείμενο δίνει ΠΑΝΤΑ το ίδιο επάγγελμα και τα ίδια themes.

    python -m unittest tests.test_recommendation_determinism

ΤΙ ΠΡΟΣΤΑΤΕΥΕΙ. Δύο ξεχωριστά ελαττώματα που μαζί έβγαζαν στον πελάτη αντίφαση:

1. Το `/designs` καλούσε `vertical_of()` για την ετικέτα και
   `recommend_templates()` για τα themes — δύο ανεξάρτητες αποφάσεις. Όταν η
   απόφαση περνούσε από το AI fallback, μπορούσαν να διαφωνήσουν: μετρήθηκε
   ετικέτα «Τεχνικά επαγγέλματα» πάνω από themes δικηγορικού γραφείου, που το
   ίδιο το backend βαθμολογούσε άσχετα.

2. Το AI fallback έτρεχε με `temperature=0.7`. Πέντε πανομοιότυπες κλήσεις στο
   ίδιο intake έδωσαν `professional, trade, professional, professional,
   professional` — ο ίδιος πελάτης, με το ίδιο κείμενο, έβλεπε άλλα site.

Τα τεστ εδώ ΔΕΝ καλούν δίκτυο: χρησιμοποιούν εισόδους που λύνονται ντετερμινιστικά
από λέξεις-κλειδιά, και ελέγχουν ότι το AI δεν καλείται καν γι' αυτές.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from src import premium_generator as pg


def intake(text: str, **kw) -> dict:
    return {"name": "", "type": "", "city": "", "description": text,
            "services": [], **kw}


# Επαγγέλματα που ΠΡΕΠΕΙ να λύνονται χωρίς AI.
KNOWN = [
    ("Έχω κομμωτήριο στη Γλυφάδα", "beauty"),
    ("Είμαι υδραυλικός στον Πειραιά", "trade"),
    ("Έχω οδοντιατρείο στο Χαλάνδρι", "dentist"),
    ("Έχω ταβέρνα στα Εξάρχεια", "food"),
    ("Έχω φαρμακείο στη Λάρισα", "pharmacy"),
    ("Είμαι δικηγόρος στο Κολωνάκι", "professional"),
    ("Έχω γυμναστήριο στο Περιστέρι", "gym"),
    ("Έχω ζαχαροπλαστείο στη Θεσσαλονίκη", "bakery"),
    ("Είμαι ξυλουργός στο Ηράκλειο", "wood"),
    ("Έχω ενοικιαζόμενα δωμάτια στην Πάρο", "rooms"),
]


class KnownProfessionsNeedNoModel(unittest.TestCase):
    """Γνωστό επάγγελμα = ντετερμινιστική απάντηση, χωρίς κλήση σε πάροχο."""

    def test_resolved_without_ai(self):
        with patch.object(pg, "_vertical_by_ai",
                          side_effect=AssertionError("κλήθηκε AI για γνωστό επάγγελμα")):
            for text, expected in KNOWN:
                with self.subTest(text=text):
                    self.assertEqual(pg._vertical(intake(text)), expected)

    def test_same_input_same_answer(self):
        """Επαναληψιμότητα: δέκα κλήσεις, μία απάντηση."""
        with patch.object(pg, "_vertical_by_ai",
                          side_effect=AssertionError("δεν έπρεπε να κληθεί AI")):
            for text, _ in KNOWN:
                answers = {pg._vertical(intake(text)) for _ in range(10)}
                self.assertEqual(len(answers), 1,
                                 f"«{text}» έδωσε {answers}")

    def test_same_input_same_themes(self):
        with patch.object(pg, "_vertical_by_ai",
                          side_effect=AssertionError("δεν έπρεπε να κληθεί AI")):
            for text, _ in KNOWN:
                runs = {tuple(pg.recommend_templates(intake(text), limit=12))
                        for _ in range(5)}
                self.assertEqual(len(runs), 1, f"«{text}» έδωσε {len(runs)} σειρές")


class LabelAndThemesShareOneDecision(unittest.TestCase):
    """Η ετικέτα και οι προτάσεις δεν επιτρέπεται να έρθουν από άλλη απόφαση."""

    def test_recommend_accepts_a_precomputed_vertical(self):
        data = intake("Έχω κομμωτήριο στη Γλυφάδα")
        for v in ("beauty", "food", "trade"):
            with self.subTest(vertical=v):
                got = pg.recommend_templates(data, limit=12, vertical=v)
                # Το περασμένο vertical είναι ΑΥΘΕΝΤΙΑ: οι προτάσεις πρέπει να
                # είναι εκείνου, όχι όποιου θα έβγαζε μια δεύτερη ανίχνευση.
                self.assertEqual(got, pg.recommend_templates(data, limit=12, vertical=v))
                self.assertTrue(got)

    def test_designs_endpoint_computes_vertical_once(self):
        """Στατικός έλεγχος: το /designs δεν ξανακαλεί την ανίχνευση.

        Ένα τεστ συμπεριφοράς θα χρειαζόταν βάση· εδώ αρκεί ότι ο κώδικας
        περνά ρητά το `vertical=` και δεν κάνει δεύτερη κλήση.
        """
        import inspect
        from src import meta_oauth
        raw = inspect.getsource(meta_oauth.list_designs)
        # Τα σχόλια εξηγούν το σφάλμα· δεν το προκαλούν. Μετράμε ΚΛΗΣΕΙΣ.
        code = "\n".join(line.split("#", 1)[0] for line in raw.splitlines())
        self.assertIn("vertical=vertical", code,
                      "το /designs δεν περνά την απόφαση στις προτάσεις")
        self.assertEqual(code.count("_intake_from_db("), 1,
                         "το /designs διαβάζει το intake πάνω από μία φορά")
        self.assertEqual(code.count("recommend_templates("), 1,
                         "το /designs καλεί τις προτάσεις πάνω από μία φορά")
        self.assertEqual(code.count("vertical_of("), 1,
                         "το /designs ανιχνεύει επάγγελμα πάνω από μία φορά")


class ClassificationAsksForZeroTemperature(unittest.TestCase):
    """Το fallback πρέπει να ζητά σταθερή απάντηση και να τη θυμάται."""

    def test_calls_model_with_temperature_zero(self):
        seen = {}

        def fake_complete(system, user, max_tokens=1500, temperature=None):
            seen["temperature"] = temperature
            return "trade"

        pg._AI_VERTICAL_CACHE.clear()
        with patch("src.ai.available", return_value=True), \
             patch("src.ai.complete", side_effect=fake_complete):
            pg._vertical_by_ai("κάτι εντελώς άγνωστο ζζζ")
        self.assertEqual(seen.get("temperature"), 0,
                         "η ταξινόμηση ζήτησε μη μηδενική θερμοκρασία")

    def test_second_call_uses_the_cache(self):
        calls = []

        def fake_complete(system, user, max_tokens=1500, temperature=None):
            calls.append(user)
            return "trade"

        pg._AI_VERTICAL_CACHE.clear()
        with patch("src.ai.available", return_value=True), \
             patch("src.ai.complete", side_effect=fake_complete):
            a = pg._vertical_by_ai("άγνωστο επάγγελμα ξξξ")
            b = pg._vertical_by_ai("άγνωστο επάγγελμα ξξξ")
        self.assertEqual(a, b)
        self.assertEqual(len(calls), 1, "το fallback ρώτησε δεύτερη φορά")


# ── Το πέρασμα σκελετού δεν επιτρέπεται να ξαναφέρει τις συγκρούσεις ────────
#
# Το `_SKEL_MIN=4` επιτρέπει κοντούς σκελετούς («δωρα»->dora, «καβα»->kava,
# «μελι»->meli, «νυχι»->nixi). Καθένας είναι πρόθεμα πραγματικού ελληνικού
# ονόματος ή τοπωνυμίου. Το σύνολο αξιολόγησης δεν περιέχει καμία τέτοια
# είσοδο, οπότε το σκορ του δεν αποδεικνύει τίποτα γι' αυτές.
#
# Δύο από τις παρακάτω περιπτώσεις ΑΠΕΤΥΧΑΝ όταν γράφτηκε αυτό το test, και
# απετύγχαναν ΚΑΙ ΠΡΙΝ από κάθε αλλαγή σκελετού — στο απλό ελληνικό πέρασμα:
# «Δώρα Παπαδοπούλου, δικηγόρος» -> retail, «Μελίνα Στούντιο, κομμωτήριο»
# -> farm. Ισοβαθμία 8-8 που την έκρινε η σειρά των κανόνων.
_ADVERSARIAL = (
    ("Δώρα Παπαδοπούλου, δικηγόρος στην Καβάλα", "professional"),
    ("Dora Papadopoulou, dikigoros stin Kavala", "professional"),
    ("Ηλεκτρολόγος στην Καβάλα", "trade"),
    ("Ilektrologos stin Kavala", "trade"),
    ("Barber Shop Nikos, Θεσσαλονίκη", "beauty"),
    ("Barbershop tou Kosta sto Peristeri", "beauty"),
    ("Farmakeio Papadopoulou sta Exarcheia", "pharmacy"),
    ("Thessaloniki Electric — ilektrologikes egkatastaseis", "trade"),
    ("Spartan Gym, propomisi dynamis", "gym"),
    ("Nail Bar Athens, manikioyr kai pedikioyr", "beauty"),
    ("Ktimatomesitiko grafeio, poliseis akiniton", "realestate"),
    ("Taverna To Steki, mageireyta kai mezedes", "food"),
    ("Melina Studio, kommotirio sto Chalandri", "beauty"),
    ("Villa Melina, enoikiazomena domatia sti Naxo", "rooms"),
    ("Meli apo ta vouna tis Arkadias, oikotechnia", "farm"),
    ("Kava krasion sto Kolonaki", "retail"),
    ("Odontiatreio Georgiou, emfytevmata", "dentist"),
    ("Scholi polemikon technon sto Peristeri", "gym"),
    ("Fysikotherapeytirio, apokatastasi meta apo travmatismo", "doctor"),
    ("Synergeio aytokiniton, fanopoieio kai vafeio", "garage"),
)


class SkeletonCollisions(unittest.TestCase):
    """Ονόματα και τοπωνύμια δεν γίνονται επαγγέλματα."""

    def test_no_name_or_place_decides_the_profession(self):
        wrong = []
        for text, expected in _ADVERSARIAL:
            got, _ = pg.vertical_of({"name": "", "description": text})
            if got != expected:
                wrong.append(f"{text!r}: {got} αντί {expected}")
        self.assertEqual(wrong, [], "; ".join(wrong))

    def test_the_fold_never_overrides_an_exact_match(self):
        """Το χαλαρό πέρασμα τρέχει ΜΟΝΟ όταν το ακριβές δεν αποφάσισε."""
        for text, expected in _ADVERSARIAL:
            intake = {"name": "", "description": text}
            exact = pg._decide(pg._signals(intake))
            if exact:
                self.assertEqual(
                    pg._vertical(intake), exact,
                    f"ο σκελετός ανέτρεψε ακριβές ταίριασμα: {text!r}")

    def test_short_skeletons_cannot_decide(self):
        """«μπαρ» -> «bar» δεν επιτρέπεται να πιάσει το «barber»."""
        self.assertLess(len(pg._skeleton("μπαρ")), pg._SKEL_MIN)
        self.assertFalse(pg._part_match("μπαρ", "barber", fold=True))
        self.assertFalse(pg._part_match("farm", "farmakeio", fold=True))
        self.assertFalse(pg._part_match("salon", "thessaloniki", fold=True))

    def test_greeklish_reaches_the_same_vertical_as_greek(self):
        for greek, greeklish in (
            ("κομμωτήριο στο Χαλάνδρι", "kommotirio sto Chalandri"),
            ("υδραυλικός στο Περιστέρι", "ydraylikos sto Peristeri"),
            ("οδοντιατρείο στη Λάρισα", "odontiatreio sti Larisa"),
            ("φαρμακείο στα Εξάρχεια", "farmakeio sta Exarcheia"),
        ):
            a, _ = pg.vertical_of({"description": greek})
            b, _ = pg.vertical_of({"description": greeklish})
            self.assertEqual(a, b, f"{greek!r} != {greeklish!r}")


if __name__ == "__main__":
    unittest.main()
