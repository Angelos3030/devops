#!/usr/bin/env python3
"""Σκούρο mode για τον spine: η παλέτα δίνει ΑΠΟΧΡΩΣΗ, το theme τη ΦΩΤΕΙΝΟΤΗΤΑ.

    python scripts/build_dark_mode.py            # γράφει CSS + χάρτη mode
    python scripts/build_dark_mode.py --check    # μόνο αναφορά

ΤΟ ΠΡΟΒΛΗΜΑ. Και οι πέντε παλέτες του spine έχουν ΑΝΟΙΧΤΗ επιφάνεια (0,83-0,95).
Επτά themes είναι εγγενώς σκούρα (μετρημένη φωτεινότητα 0,004-0,017). Όταν ο
πελάτης διάλεγε παλέτα, το σκούρο theme αντιστρεφόταν: τα σκληρογραμμένα σκούρα
πάνελ έμεναν σκούρα, οι ρόλοι κειμένου γίνονταν σκούροι, και το κείμενο
εξαφανιζόταν — μετρήθηκε 1:1 στο dispatch, στο motor, στο cinematic.

Η ΛΥΣΗ ΔΕΝ ΕΙΝΑΙ ΔΕΥΤΕΡΟ ΣΥΣΤΗΜΑ. Ίδιοι ρόλοι, ίδια ονόματα οικογενειών,
δεύτερη σειρά τιμών για σκούρο mode. Η επιλογή γίνεται από ΜΕΤΡΗΜΕΝΗ
φωτεινότητα της επιφάνειας που δηλώνει το ίδιο το theme — ποτέ από όνομα.
"""
from __future__ import annotations

import colorsys
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "sites" / "lib" / "templates"
THEME_CSS = ROOT / "sites" / "app" / "site" / "[client]" / "theme.module.css"
MODE_JS = T / "themeMode.js"

DARK_MAX_LUM = 0.20   # πάνω από αυτό το theme θεωρείται ανοιχτό

ROLES = ("surface", "surface-2", "surface-deep", "ink", "ink-soft", "on-deep",
         "accent", "on-accent", "accent-ink", "accent-on-deep", "line")


def lin(v):
    v /= 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def lum(rgb):
    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])


def unhex(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexs(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def hsl(h, s, light):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, light, s)
    return (r * 255, g * 255, b * 255)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def toward(rgb, target):
    r, g, b = [c / 255 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    best = bl = None
    for i in range(1001):
        c = hsl(h * 360, s, i / 1000)
        d = abs(lum(c) - target)
        if best is None or d < best:
            best, bl = d, c
    return bl


def fit(fg, bg, need, darker):
    r, g, b = [c / 255 for c in fg]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    for i in range(401):
        cl = l * (1 - i / 400) if darker else l + (1 - l) * i / 400
        c = hsl(h * 360, s, cl)
        if ratio(c, bg) >= need:
            return c
    return None


# Απόχρωση από τις ΥΠΑΡΧΟΥΣΕΣ ανοιχτές παλέτες: «ροζ» σημαίνει το ίδιο ροζ.
FAMILY_ACCENT = {"warm": "#b95732", "forest": "#3d7a58", "ocean": "#247997",
                 "rose": "#b75870", "mono": "#151515"}
TARGET = {"surface": 0.012, "surface-2": 0.030, "surface-deep": 0.006}

PAIRS = [("ink", "surface", 4.5), ("ink", "surface-2", 4.5),
         ("ink-soft", "surface", 4.5), ("ink-soft", "surface-2", 4.5),
         ("accent-ink", "surface", 4.5), ("accent-ink", "surface-2", 4.5),
         ("on-accent", "accent", 4.5), ("on-deep", "surface-deep", 4.5),
         ("accent-on-deep", "surface-deep", 4.5)]


def build_dark(name: str) -> dict[str, str]:
    acc = unhex(FAMILY_ACCENT[name])
    r, g, b = [c / 255 for c in acc]
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    hue = h * 360
    sat = 0.0 if name == "mono" else min(s, 0.35)

    surface = toward(hsl(hue, sat, 0.5), TARGET["surface"])
    surface2 = toward(hsl(hue, sat, 0.5), TARGET["surface-2"])
    deep = toward(hsl(hue, sat, 0.5), TARGET["surface-deep"])
    ink = fit(hsl(hue, sat * 0.3, 0.9), surface2, 4.5, False) or (255, 255, 255)
    ink_soft = fit(hsl(hue, sat * 0.4, 0.62), surface2, 4.5, False) or (200, 200, 200)
    on_deep = fit(hsl(hue, sat * 0.2, 0.95), deep, 4.5, False) or (255, 255, 255)
    accent = hsl(hue, max(s, 0.45) if name != "mono" else 0.0,
                 0.62 if name != "mono" else 0.86)
    on_accent = fit((20, 20, 20), accent, 4.5, True) or (255, 255, 255)
    accent_ink = fit(accent, surface2, 4.5, False) or ink
    accent_on_deep = fit(accent, deep, 4.5, False) or on_deep
    line = toward(hsl(hue, sat, 0.5), 0.075)
    return dict(zip(ROLES, map(hexs, [surface, surface2, deep, ink, ink_soft,
                                      on_deep, accent, on_accent, accent_ink,
                                      accent_on_deep, line])))


MEASURED = ROOT / "research" / "theme-modes.json"


def theme_modes() -> dict[str, dict]:
    """Το mode ΚΑΘΕ theme, από ΜΕΤΡΗΣΗ ΣΤΗΝ ΑΠΟΔΟΣΗ.

    Η στατική ανάγνωση του CSS ΔΕΝ δουλεύει: τα CafeCollection και
    CapabilitySystems στεγάζουν επτά ταυτότητες το καθένα, και το ελάχιστο
    surface όλου του αρχείου μάρκαρε σκούρο το ανοιχτό bakery-editorial μαζί
    με το μαύρο counter-menu. Μόνο ο browser ξέρει ποια ταυτότητα ισχύει.

    Παράγεται από sites/artifacts/measure-mode.mjs.
    """
    if MEASURED.exists():
        data = json.loads(MEASURED.read_text(encoding="utf-8"))
        return {t: {"mode": v["mode"], "lum": v["lum"], "file": v.get("source", "")}
                for t, v in data.items()}
    print("⚠ λείπει research/theme-modes.json — τρέξε πρώτα measure-mode.mjs")
    return _theme_modes_static()


def _theme_modes_static() -> dict[str, dict]:
    """Εφεδρικό, ΑΝΑΚΡΙΒΕΣ για αρχεία με πολλές ταυτότητες. Βλ. theme_modes()."""
    idx = (T / "index.js").read_text(encoding="utf-8")
    themes = json.loads(re.search(r"COMMERCIAL_THEMES = (\[[^\]]+\])", idx).group(1))
    file_of = {}
    for m in re.finditer(r"^import\s+([A-Za-z0-9_]+)\s+from\s+'\./([A-Za-z0-9_]+)'", idx, re.M):
        file_of[m.group(1)] = m.group(2)
    for m in re.finditer(r"^import\s+\{([^}]+)\}\s+from\s+'\./([A-Za-z0-9_]+)'", idx, re.M):
        for n in [x.strip() for x in m.group(1).split(",") if x.strip()]:
            file_of[n] = m.group(2)
    tm = re.search(r"export const TEMPLATES = \{(.*?)\}\s*\n", idx, re.S).group(1)
    comp = dict(re.findall(r"'?([A-Za-z0-9-]+)'?\s*:\s*([A-Za-z0-9_]+)", tm))

    out = {}
    for t in themes:
        css = T / f"{file_of[comp[t]]}.module.css"
        s = css.read_text(encoding="utf-8")
        # Πολλά αρχεία στεγάζουν πολλές ταυτότητες· κρατάμε ΚΑΘΕ δήλωση surface
        # και παίρνουμε τη σκουρότερη — αν έστω μία ταυτότητα είναι σκούρη, το
        # theme χρειάζεται σκούρο mode.
        vals = re.findall(r"--vt-surface\s*:\s*(#[0-9a-fA-F]{3,8})", s)
        if not vals:
            out[t] = {"mode": "light", "lum": None, "why": "καμία δήλωση surface"}
            continue
        lums = [lum(unhex(v)) for v in vals]
        L = min(lums)
        out[t] = {"mode": "dark" if L < DARK_MAX_LUM else "light",
                  "lum": round(L, 4), "file": css.name}
    return out


def main() -> None:
    check = "--check" in sys.argv
    dark = {n: build_dark(n) for n in FAMILY_ACCENT}

    fails = [(p, fg, bg, round(ratio(unhex(v[fg]), unhex(v[bg])), 2), need)
             for p, v in dark.items() for fg, bg, need in PAIRS
             if ratio(unhex(v[fg]), unhex(v[bg])) < need]
    print(f"DARK_PALETTE_CONTRACT: {'PASS' if not fails else 'FAIL'} "
          f"({len(PAIRS) * len(dark) - len(fails)}/{len(PAIRS) * len(dark)} ζεύγη)")
    for f in fails:
        print("   ✗", f)
    if fails:
        sys.exit(1)

    modes = theme_modes()
    dark_themes = sorted(t for t, v in modes.items() if v["mode"] == "dark")
    print(f"\nΣΚΟΥΡΑ THEMES (μετρημένα, φωτεινότητα < {DARK_MAX_LUM}): {len(dark_themes)}")
    for t in dark_themes:
        print(f"   {t:<22} {modes[t]['lum']:.4f}  {modes[t].get('file','')}")

    if check:
        print("\n(έλεγχος μόνο — καμία εγγραφή)")
        return

    # ── 1. CSS ────────────────────────────────────────────────────────────
    css = io.open(THEME_CSS, encoding="utf-8").read()
    MARK = "/* ── ΣΚΟΥΡΟ MODE ─"
    if MARK not in css:
        block = ["", MARK + "──────────────────────────────────────────────────",
                 "   Η παλέτα δίνει ΑΠΟΧΡΩΣΗ, το theme δίνει ΦΩΤΕΙΝΟΤΗΤΑ.",
                 "",
                 "   Επτά themes είναι εγγενώς σκούρα (μετρημένη φωτεινότητα επιφάνειας",
                 "   0,004-0,017). Οι ανοιχτές παλέτες τα ΑΝΤΕΣΤΡΕΦΑΝ: τα σκληρογραμμένα",
                 "   σκούρα πάνελ έμεναν σκούρα ενώ οι ρόλοι κειμένου γίνονταν σκούροι.",
                 "   Μετρήθηκε 1:1 σε dispatch, motor, cinematic — αόρατο κείμενο.",
                 "",
                 "   Ίδιοι ρόλοι, ίδιες οικογένειες, δεύτερη σειρά τιμών. Η απόχρωση",
                 "   διατηρείται μέσα σε 1 μοίρα· αλλάζει μόνο η φωτεινότητα.",
                 "   Και τα 45 ζεύγη ρόλων επαληθεύτηκαν σε WCAG AA.",
                 "   Παράγεται από scripts/build_dark_mode.py — μην το γράψεις στο χέρι.",
                 "   ───────────────────────────────────────────────────────────────── */"]
        for name, v in dark.items():
            decls = " ".join(f"--vt-{k}:{v[k]};" for k in ROLES)
            block.append(f".scope[data-mode='dark'][data-palette='{name}'] > :first-child {{ {decls} }}")
        io.open(THEME_CSS, "w", encoding="utf-8").write(css.rstrip() + "\n" + "\n".join(block) + "\n")
        print(f"\n✓ {THEME_CSS.name}: +{len(dark)} σκούρες παλέτες")
    else:
        print(f"\n↷ {THEME_CSS.name}: υπάρχει ήδη")

    # ── 2. χάρτης mode ────────────────────────────────────────────────────
    lines = [
        "// ΠΑΡΑΓΟΜΕΝΟ — scripts/build_dark_mode.py. Μην το γράψεις στο χέρι.",
        "//",
        "// Το mode ΔΕΝ βγαίνει από όνομα theme. Βγαίνει από τη φωτεινότητα της",
        "// επιφάνειας που δηλώνει το ίδιο το CSS του theme. Το tests/themeMode.mjs",
        "// την ξαναϋπολογίζει και κόβει αν ο χάρτης αποκλίνει.",
        "export const THEME_MODE = {",
    ]
    for t in sorted(modes):
        v = modes[t]
        lu = "null" if v["lum"] is None else f"{v['lum']:.4f}"
        lines.append(f"  '{t}': '{v['mode']}',   // {lu}")
    lines += ["}", "",
              "export function themeMode(key) {",
              "  return THEME_MODE[key] === 'dark' ? 'dark' : 'light'",
              "}", ""]
    io.open(MODE_JS, "w", encoding="utf-8").write("\n".join(lines))
    print(f"✓ {MODE_JS.name}: {len(modes)} themes ({len(dark_themes)} σκούρα)")


if __name__ == "__main__":
    main()
