#!/usr/bin/env python3
"""Αντικατάσταση του master σήματος της Vitrina με τη Λ1-A.

    python scripts/swap_master_logo.py

Αγγίζει ΜΟΝΟ το σήμα της Vitrina. Δεν πειράζει λογότυπα πελατών, ούτε
τυπογραφία, χρώματα, κείμενα ή διατάξεις.

Στην παραγωγή υπήρχαν ΔΥΟ διαφορετικά παλιά σήματα:
  · web/index.html            — κάθετο μοντάζ (κατεύθυνση Ε, βαθμολογία 6.4)
  · 6 δευτερεύουσες σελίδες   — μαγαζί με πορτοκαλί τέντα

Και τα δύο γίνονται Λ1-A: πλαίσιο βιτρίνας με ένα φωτισμένο τζάμι που
ακουμπά την κάτω δεξιά εσωτερική γωνία.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"

INK, CORAL = "#171714", "#E85D3F"


def stroke_for(px: int) -> float:
    """Optical sizing: λεπτότερη γραμμή σβήνει σε πραγματικά pixel."""
    return 3 if px <= 20 else 2.8 if px <= 40 else 2.6


def mark(px: int, cls: str = "", ink: str = "currentColor", pane: str = CORAL) -> str:
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 26 26" width="{px}" height="{px}" '
            f'aria-hidden="true" focusable="false">'
            f'<rect x="2" y="2" width="22" height="22" rx="4.4" fill="none" '
            f'stroke="{ink}" stroke-width="{stroke_for(px)}"/>'
            f'<path d="M13 13H22.7v6.5a3.1 3.1 0 0 1-3.1 3.1H13z" fill="{pane}"/></svg>')


def main() -> None:
    changed = []

    # ── 1. Η αρχική: το inline σήμα του header ─────────────────────────
    p = WEB / "index.html"
    s = io.open(p, encoding="utf-8").read()
    new, n = re.subn(r'<svg class="logo-mark".*?</svg>', mark(17, "logo-mark"), s, flags=re.S)
    assert n == 1, f"index.html: {n} σήματα, περίμενα 1"
    # το mobile μέγεθος ορίζεται στο CSS· δεν το αγγίζουμε
    assert 'Φτιάχνουμε το site.' in new, "χάθηκε το hero"
    io.open(p, "w", encoding="utf-8").write(new)
    changed.append(("index.html", 1))

    # ── 2. Οι δευτερεύουσες σελίδες: το παλιό σήμα με την τέντα ───────
    OLD = re.compile(
        r'<svg viewBox="0 0 32 32" width="(\d+)" height="\d+" aria-hidden="true">\s*'
        r'<rect x="6" y="14".*?</svg>', re.S)
    for name in ("start.html", "connect.html", "privacy.html", "terms.html",
                 "refunds.html", "data-deletion.html"):
        f = WEB / name
        if not f.exists():
            continue
        t = io.open(f, encoding="utf-8").read()
        hits = OLD.findall(t)
        if not hits:
            continue
        t2 = OLD.sub(lambda m: mark(int(m.group(1))), t)
        io.open(f, "w", encoding="utf-8").write(t2)
        changed.append((name, len(hits)))

    # ── 3. Αυτόνομο logo.svg ───────────────────────────────────────────
    io.open(WEB / "logo.svg", "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 26 26" width="64" height="64" '
        'role="img" aria-label="Vitrina"><title>Vitrina</title>'
        '<rect x="2" y="2" width="22" height="22" rx="4.4" fill="none" '
        f'stroke="{INK}" stroke-width="2.6"/>'
        f'<path d="M13 13H22.7v6.5a3.1 3.1 0 0 1-3.1 3.1H13z" fill="{CORAL}"/></svg>\n')
    changed.append(("logo.svg", 1))

    # ── 4. Ο γεννήτορας της αρχικής να παράγει Λ1-A στο εξής ──────────
    g = ROOT / "scripts" / "integrate_homepage.py"
    gs = io.open(g, encoding="utf-8").read()
    old_logo = re.search(r"LOGO = '''<span class=\"logo\".*?'''", gs, re.S)
    if old_logo:
        new_logo = ("LOGO = '''<span class=\"logo\" aria-label=\"Vitrina\">\n      "
                    + mark(17, "logo-mark") + "vitrina</span>'''")
        io.open(g, "w", encoding="utf-8").write(gs.replace(old_logo.group(0), new_logo, 1))
        changed.append(("scripts/integrate_homepage.py", 1))

    for name, n in changed:
        print(f"  ✓ {name:34} {n}")

    # ── 5. Καμία υπολειπόμενη αναφορά στα παλιά σήματα ────────────────
    leftovers = []
    for f in sorted(WEB.glob("*.html")):
        t = io.open(f, encoding="utf-8", errors="ignore").read()
        if re.search(r'<rect x="6" y="14" width="20" height="14"', t):
            leftovers.append((f.name, "τέντα"))
        if re.search(r'viewBox="0 0 22 28"', t):
            leftovers.append((f.name, "κάθετο μοντάζ"))
    print()
    print("υπολείμματα παλιών σημάτων:", leftovers or "κανένα")
    assert not leftovers, leftovers


if __name__ == "__main__":
    main()
