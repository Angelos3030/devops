"""Δύο πάροχοι AI συνυπάρχουν χωρίς να πατάει ο ένας τον άλλον.

    python -m unittest tests.test_provider_isolation

ΤΙ ΠΡΟΣΤΑΤΕΥΕΙ. Το προϊόν μιλάει σε ΔΥΟ διαφορετικά πρωτόκολλα:

  src/ai.py            -> Anthropic Messages API   (site_copy, agents)
  src/ai_editor/       -> OpenAI-συμβατό, DeepSeek (ο βοηθός του πελάτη)

Και τα δύο διάβαζαν το ΙΔΙΟ `AI_API_KEY`. Ένα κλειδί δεν μπορεί να είναι
έγκυρο και για τους δύο, οπότε κάποιος έπαιρνε πάντα 401.

ΤΙ ΣΥΝΕΒΗ ΠΡΑΓΜΑΤΙΚΑ, ΜΕ ΤΗ ΣΕΙΡΑ:

  1. `AI_API_KEY` ήταν κλειδί Anthropic (`sk-ant-…`) και `AI_BASE_URL` κενό.
     Ο editor έπεφτε στο DeepSeek, έστελνε κλειδί Anthropic εκεί, έπαιρνε 401,
     και ΚΑΘΕ μήνυμα πελάτη γύριζε 502. Ο chat editor ήταν νεκρός.
  2. Πρώτη διόρθωση: αντικατάσταση του `AI_API_KEY` μέσα στο `config.py`.
     Αυτό ΕΣΠΑΣΕ το `src/ai.py`, που δούλευε μια χαρά — στέλνει με
     `AI_PROVIDER=anthropic` στο api.anthropic.com και ξαφνικά κρατούσε
     κλειδί DeepSeek. Μια σιωπηλή ανταλλαγή: διόρθωσα τον έναν σπάζοντας τον
     άλλον.
  3. Τελική λύση: το `config.py` ΔΕΝ αγγίζει το κοινό κλειδί. Ο κάθε
     καταναλωτής διαλέγει κλειδί που ταιριάζει στο ΔΙΚΟ ΤΟΥ endpoint, και η
     επιλογή του editor ζει στο `ai_editor/model.py`.

Χωρίς αυτό το test, το βήμα 2 ξαναγίνεται εύκολα: φαίνεται σαν καθαρή
διόρθωση, και η ζημιά είναι σε άλλο αρχείο.

Κανένα δικτυακό αίτημα εδώ — μόνο επίλυση ρυθμίσεων.
"""
from __future__ import annotations

import pathlib
import re
import unittest
from unittest.mock import patch

from src import ai
from src import config as cfg
from src.ai_editor.model import DeepSeekSiteEditingModel

ANTHROPIC_KEY = "sk-ant-" + "a" * 40
DEEPSEEK_KEY = "sk-" + "d" * 32
SRC = pathlib.Path(__file__).resolve().parents[1] / "src"


class AnthropicPathKeepsItsCredentials(unittest.TestCase):
    """Ό,τι κι αν κάνει ο editor, το μονοπάτι Anthropic μένει άθικτο."""

    def test_provider_follows_explicit_setting(self):
        with patch.object(cfg, "AI_PROVIDER", "anthropic"), \
             patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY), \
             patch.object(cfg, "AI_BASE_URL", ""):
            self.assertEqual(ai.provider(), "anthropic")

    def test_anthropic_key_shape_is_preserved(self):
        """Το `config.py` δεν επιτρέπεται να αντικαταστήσει καθολικά το κλειδί."""
        with patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY):
            self.assertTrue(cfg.AI_API_KEY.startswith("sk-ant-"))

    def test_config_never_swaps_the_shared_key(self):
        """Το βήμα 2 της ιστορίας δεν πρέπει να ξαναγραφτεί στο config.py."""
        source = (SRC / "config.py").read_text(encoding="utf-8")
        # Ανάθεση στο AI_API_KEY επιτρέπεται ΜΙΑ φορά: ο αρχικός ορισμός.
        assignments = re.findall(r"^AI_API_KEY\s*=", source, re.M)
        self.assertEqual(
            len(assignments), 1,
            "Το config.py ξαναναθέτει το AI_API_KEY. Αυτό σπάει το src/ai.py: "
            "η επιλογή κλειδιού ανήκει στον καταναλωτή, όχι στη ρύθμιση.")


class EditorPathResolvesItsOwnCredentials(unittest.TestCase):
    """Ο editor μιλάει OpenAI-συμβατά και διαλέγει κλειδί που ταιριάζει."""

    def test_defaults_to_deepseek_endpoint(self):
        with patch.object(cfg, "AI_BASE_URL", ""), \
             patch.object(cfg, "AI_API_KEY", DEEPSEEK_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY):
            model = DeepSeekSiteEditingModel()
            self.assertIn("deepseek", model.base_url)

    def test_anthropic_key_is_not_sent_to_deepseek(self):
        """Η ακριβής περίπτωση που σκότωνε τον βοηθό."""
        with patch.object(cfg, "AI_BASE_URL", ""), \
             patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY):
            model = DeepSeekSiteEditingModel()
            self.assertEqual(model.api_key, DEEPSEEK_KEY)
            self.assertFalse(model.api_key.startswith("sk-ant-"))

    def test_explicit_arguments_still_win(self):
        """Ρητό όρισμα υπερισχύει κάθε αυτόματης επιλογής."""
        with patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY):
            model = DeepSeekSiteEditingModel(api_key="explicit", base_url="https://example.test")
            self.assertEqual(model.api_key, "explicit")

    def test_anthropic_endpoint_keeps_the_anthropic_key(self):
        """Αν κάποιος στρέψει τον editor στην Anthropic, μην του αλλάξεις κλειδί."""
        with patch.object(cfg, "AI_BASE_URL", "https://api.anthropic.com"), \
             patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY):
            model = DeepSeekSiteEditingModel()
            self.assertEqual(model.api_key, ANTHROPIC_KEY)


class ChangingOneProviderCannotAffectTheOther(unittest.TestCase):
    """Το κρίσιμο αναλλοίωτο: η μία διαδρομή δεν πατάει την άλλη."""

    def test_building_the_editor_does_not_mutate_shared_config(self):
        with patch.object(cfg, "AI_BASE_URL", ""), \
             patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY), \
             patch.object(cfg, "AI_PROVIDER", "anthropic"):
            before = cfg.AI_API_KEY
            DeepSeekSiteEditingModel()          # ο editor διαλέγει το δικό του
            self.assertEqual(cfg.AI_API_KEY, before,
                             "Ο editor άλλαξε το κοινό κλειδί — το src/ai.py θα πάρει 401.")
            self.assertEqual(ai.provider(), "anthropic")

    def test_pointing_the_editor_elsewhere_leaves_anthropic_alone(self):
        with patch.object(cfg, "AI_PROVIDER", "anthropic"), \
             patch.object(cfg, "AI_API_KEY", ANTHROPIC_KEY):
            DeepSeekSiteEditingModel(api_key="other", base_url="https://openrouter.ai/api/v1")
            self.assertEqual(cfg.AI_API_KEY, ANTHROPIC_KEY)
            self.assertEqual(ai.provider(), "anthropic")


class NoProductionPathDependsOnKimi(unittest.TestCase):
    """Το Kimi/Moonshot είναι πειραματικό — μόνο σε scripts, ποτέ στο προϊόν."""

    def test_src_never_reads_a_kimi_credential(self):
        offenders = [p.relative_to(SRC).as_posix()
                     for p in SRC.rglob("*.py")
                     if "KIMI_API_KEY" in p.read_text(encoding="utf-8")]
        self.assertEqual(offenders, [],
                         f"Το src/ διαβάζει κλειδί Kimi: {offenders}")

    def test_moonshot_appears_only_as_an_optional_adaptation(self):
        """Αναφορά στο moonshot επιτρέπεται μόνο υπό συνθήκη base_url.

        Δηλαδή: «ΑΝ κάποιος ρυθμίσει Moonshot, προσαρμόσου» — όχι «κάλεσε
        Moonshot». Οι δύο υπάρχουσες γραμμές είναι ακριβώς αυτό.
        """
        for path in SRC.rglob("*.py"):
            for line in path.read_text(encoding="utf-8").splitlines():
                code = line.split("#", 1)[0]      # τα σχόλια εξηγούν, δεν καλούν
                if "moonshot" not in code.lower():
                    continue
                self.assertIn(
                    "base_url", code,
                    f"{path.name}: αναφορά σε Moonshot εκτός ελέγχου base_url -> {line.strip()}")

    def test_editor_default_is_not_moonshot(self):
        with patch.object(cfg, "AI_BASE_URL", ""), \
             patch.object(cfg, "AI_API_KEY", DEEPSEEK_KEY), \
             patch.object(cfg, "DEEPSEEK_API_KEY", DEEPSEEK_KEY):
            self.assertNotIn("moonshot", DeepSeekSiteEditingModel().base_url)


if __name__ == "__main__":
    unittest.main()
