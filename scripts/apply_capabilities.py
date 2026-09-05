#!/usr/bin/env python3
"""Μεταφράζει την ΚΑΝΟΝΙΚΗ πηγή δυνατοτήτων στους δύο καταναλωτές.

    python scripts/apply_capabilities.py            # γράφει
    python scripts/apply_capabilities.py --check    # μόνο έλεγχος

Πηγή:   research/theme-library/capabilities.py   ← το μόνο αρχείο που γράφεται με το χέρι
Στόχοι: sites/lib/templates/capabilities.js      ← UI + μελλοντικός AI editor
        src/theme_capabilities.py                ← έλεγχος στο backend

ΓΙΑΤΙ ΔΥΟ ΑΡΧΕΙΑ ΚΑΙ ΟΧΙ ΕΝΑ. Το frontend είναι JavaScript και το backend
Python· δεν διαβάζουν το ίδιο αρχείο. Αυτό ΔΕΝ είναι αντιγραφή: και τα δύο
παράγονται από την ίδια πηγή και το `tests/test_theme_capabilities.py` κόβει αν
αποκλίνουν έστω σε ένα theme. Χειρόγραφη αλλαγή σε παραγόμενο αρχείο χάνεται
στην επόμενη εκτέλεση — γι' αυτό γράφεται προειδοποίηση στην κορυφή τους.

Η απόκρυψη ενός control στο UI ΔΕΝ είναι επιβολή κανόνα: το backend απορρίπτει
ανεξάρτητα, ακόμη κι αν κάποιος στείλει χειροποίητο αίτημα.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "theme-library"))
import capabilities as SRC  # noqa: E402

JS_OUT = ROOT / "sites" / "lib" / "templates" / "capabilities.js"
PY_OUT = ROOT / "src" / "theme_capabilities.py"

WARN_JS = ("// ΠΑΡΑΓΟΜΕΝΟ ΑΡΧΕΙΟ — μην το γράψεις στο χέρι.\n"
           "// Πηγή: research/theme-library/capabilities.py\n"
           "// Ξαναγράφεται με: python scripts/apply_capabilities.py\n")
WARN_PY = ('"""ΠΑΡΑΓΟΜΕΝΟ ΑΡΧΕΙΟ — μην το γράψεις στο χέρι.\n\n'
           "Πηγή: research/theme-library/capabilities.py\n"
           "Ξαναγράφεται με: python scripts/apply_capabilities.py\n"
           '"""\n')


def build_js() -> str:
    caps = {t: {"cls": c["class"], "mode": c["mode"],
                "palettes": list(c["palettes"]),
                "typography": list(c["typography"]),
                "logo": bool(c["logo"])}
            for t, c in SRC.CAPABILITIES.items()}
    body = json.dumps(caps, ensure_ascii=False, indent=1, sort_keys=True)
    return (WARN_JS + "\n"
            "export const THEME_CAPABILITIES = " + body + "\n\n"
            "/** Οι δυνατότητες ενός theme. Άγνωστο id -> τίποτα επιτρεπτό. */\n"
            "export function getThemeCapabilities(themeId) {\n"
            "  const c = THEME_CAPABILITIES[themeId]\n"
            "  if (!c) return { cls: 'C', mode: 'light', palettes: [], typography: [], logo: true }\n"
            "  return c\n"
            "}\n\n"
            "/** Επιτρέπεται αυτή η συγκεκριμένη αλλαγή; Ίδια απάντηση με το backend. */\n"
            "export function isAllowed(themeId, op, value) {\n"
            "  const c = getThemeCapabilities(themeId)\n"
            "  if (op === 'set_palette') return value === 'original' || c.palettes.includes(value)\n"
            "  if (op === 'set_font_pair') return c.typography.includes(value)\n"
            "  if (op === 'set_logo') return c.logo\n"
            "  return false\n"
            "}\n")


def build_py() -> str:
    caps = {t: {"cls": c["class"], "mode": c["mode"],
                "palettes": tuple(c["palettes"]),
                "typography": tuple(c["typography"]),
                "logo": bool(c["logo"])}
            for t, c in SRC.CAPABILITIES.items()}
    lines = [WARN_PY, "from __future__ import annotations", "",
             "THEME_CAPABILITIES: dict[str, dict] = {"]
    for t in sorted(caps):
        c = caps[t]
        lines.append(f"    {t!r}: {{'cls': {c['cls']!r}, 'mode': {c['mode']!r}, "
                     f"'palettes': {c['palettes']!r}, 'typography': {c['typography']!r}, "
                     f"'logo': {c['logo']!r}}},")
    lines += ["}", "", "",
              "def get(theme_id: str) -> dict:",
              '    """Οι δυνατότητες ενός theme. Άγνωστο id -> τίποτα επιτρεπτό."""',
              "    return THEME_CAPABILITIES.get(theme_id, {",
              "        'cls': 'C', 'mode': 'light', 'palettes': (),",
              "        'typography': (), 'logo': True})", "", "",
              "def is_allowed(theme_id: str, op: str, value=None) -> bool:",
              '    """Η ΜΟΝΗ πύλη. Το frontend κρύβει· εδώ απορρίπτεται.',
              "",
              '    Παράδειγμα: coast + set_palette(forest) -> False, ό,τι κι αν στείλει',
              '    ο client. Το `original` επιτρέπεται πάντα: είναι επιστροφή στην',
              '    ταυτότητα του theme, όχι προσαρμογή.',
              '    """',
              "    c = get(theme_id)",
              "    if op == 'set_palette':",
              "        return value == 'original' or value in c['palettes']",
              "    if op == 'set_font_pair':",
              "        return value in c['typography']",
              "    if op == 'set_logo':",
              "        return bool(c['logo'])",
              "    return False", ""]
    return "\n".join(lines)


def main() -> None:
    check = "--check" in sys.argv
    for path, text in ((JS_OUT, build_js()), (PY_OUT, build_py())):
        cur = path.read_text(encoding="utf-8") if path.exists() else ""
        same = cur == text
        print(f"  {'=' if same else '~'} {path.relative_to(ROOT)}"
              f"{'  (αμετάβλητο)' if same else '  ΕΝΗΜΕΡΩΝΕΤΑΙ'}")
        if not check and not same:
            io.open(path, "w", encoding="utf-8").write(text)
    n = len(SRC.CAPABILITIES)
    by = {}
    for c in SRC.CAPABILITIES.values():
        by[c["class"]] = by.get(c["class"], 0) + 1
    print(f"\n  {n} themes · " + " · ".join(f"{k}:{by[k]}" for k in sorted(by)))
    print(f"  με παλέτα: {sum(1 for c in SRC.CAPABILITIES.values() if c['palettes'])}"
          f" · με τυπογραφία: {sum(1 for c in SRC.CAPABILITIES.values() if c['typography'])}"
          f" · με λογότυπο: {sum(1 for c in SRC.CAPABILITIES.values() if c['logo'])}")
    if check:
        print("\n(έλεγχος μόνο)")


if __name__ == "__main__":
    main()
