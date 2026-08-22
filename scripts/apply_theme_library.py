#!/usr/bin/env python3
"""Γράφει τον κατάλογο themes σε frontend και backend.

    python scripts/apply_theme_library.py

Frontend  sites/lib/templates/index.js
  · TEMPLATE_META: ελληνικό `label`, καθαρό `desc`, εμπορική `category`
  · νέο export THEME_LIBRARY + CATEGORIES για την «Επιλογή θέματος»

Backend   src/premium_generator.py
  · REACT_TEMPLATES: κάθε εμπορικό id (αλλιώς /select-design → HTTP 400)
  · LAUNCH_REACT_TEMPLATES: κάθε ΕΓΚΕΚΡΙΜΕΝΟ εμπορικό theme

Τα αρχέτυπα συμβατότητας ΔΕΝ μπαίνουν στη λίστα του πελάτη.
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "research" / "theme-library"
sys.path.insert(0, str(LIB))
from catalog import CATALOG, ARCHETYPE_META  # noqa: E402

IDX = ROOT / "sites" / "lib" / "templates" / "index.js"
PG = ROOT / "src" / "premium_generator.py"

ARCHETYPES = {"editorial", "split", "showcase", "bento", "longform",
              "corporate", "poster", "sidebar", "grid", "magazine"}


def load_state():
    reg = json.loads((LIB / "registry.json").read_text(encoding="utf-8"))
    qa = {r["id"]: r for r in json.loads((LIB / "qa.json").read_text(encoding="utf-8"))}
    return reg, qa


def parse_meta(src: str) -> dict:
    seg = src[src.find("TEMPLATE_META"):]
    out = {}
    for m in re.finditer(r"\n  '([\w-]+)':\s*\{", seg):
        k = m.group(1)
        i = m.end() - 1
        d = 0
        for j in range(i, len(seg)):
            if seg[j] == "{":
                d += 1
            elif seg[j] == "}":
                d -= 1
                if d == 0:
                    break
        body = seg[i:j]
        cust = re.search(r"customizable:\s*(\{[^}]*\})", body)
        out[k] = {"customizable": cust.group(1) if cust else "{ palette: true, fontPair: true }"}
    return out


def js(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def main() -> None:
    reg, qa = load_state()
    ids = set(reg["render_ids"])
    commercial = sorted(i for i in ids if i not in ARCHETYPES)
    approved = [i for i in commercial if qa.get(i, {}).get("pass") and i in CATALOG]
    blocked = [i for i in commercial if i not in approved]

    src = IDX.read_text(encoding="utf-8")
    old = parse_meta(src)

    # ── TEMPLATE_META ξαναγράφεται ολόκληρο ────────────────────────────
    lines = []
    ALL = {**CATALOG, **ARCHETYPE_META}
    for tid in sorted(ALL):
        if tid not in ids:
            continue
        label, desc, cat = ALL[tid]
        cust = old.get(tid, {}).get("customizable", "{ palette: true, fontPair: true }")
        internal = " internal: true," if tid in ARCHETYPES else ""
        # Το templateRegistry test ψάχνει `key:` για ids χωρίς παύλα και
        # `'key':` για όσα την έχουν. Κρατάμε το υπάρχον στιλ.
        k = f"'{tid}'" if "-" in tid else tid
        lines.append(
            f"  {k}: {{ label: '{js(label)}', desc: '{js(desc)}', "
            f"category: '{js(cat)}',{internal} customizable: {cust} }},")
    meta_block = ("export const TEMPLATE_META = {\n"
                  "  /* Ονόματα και περιγραφές ΠΡΟΣ ΤΟΝ ΠΕΛΑΤΗ. Καμία αναφορά σε\n"
                  "     εσωτερικό id, port ή πηγή template. Παράγεται από\n"
                  "     research/theme-library/catalog.py — μην το γράφεις με το χέρι. */\n"
                  + "\n".join(lines) + "\n}")

    i = src.find("export const TEMPLATE_META = {")
    assert i > 0, "δεν βρέθηκε το TEMPLATE_META"
    d = 0
    for j in range(src.index("{", i), len(src)):
        if src[j] == "{":
            d += 1
        elif src[j] == "}":
            d -= 1
            if d == 0:
                break
    src = src[:i] + meta_block + src[j + 1:]

    # ── εξαγωγές για την «Επιλογή θέματος» ─────────────────────────────
    export = f"""

/**
 * Ό,τι επιτρέπεται να δει ο πελάτης στην «Επιλογή θέματος».
 *
 * Δεν είναι κάθε renderable id: τα αρχέτυπα συμβατότητας
 * ({', '.join(sorted(ARCHETYPES))})
 * είναι στόχοι του MAP για τα legacy layout names — υποδομή, όχι προϊόν.
 */
export const COMMERCIAL_THEMES = {json.dumps(approved, ensure_ascii=False)}

export const THEME_LIBRARY = COMMERCIAL_THEMES.map((id) => ({{
  id,
  label: TEMPLATE_META[id].label,
  desc: TEMPLATE_META[id].desc,
  category: TEMPLATE_META[id].category,
}}))

export const THEME_CATEGORIES = [...new Set(THEME_LIBRARY.map((t) => t.category))].sort()

export function themesByCategory(category) {{
  return category ? THEME_LIBRARY.filter((t) => t.category === category) : THEME_LIBRARY
}}
"""
    if "COMMERCIAL_THEMES" in src:
        src = re.sub(r"\n\n/\*\*\n \* Ό,τι επιτρέπεται.*$", export, src, flags=re.S)
    else:
        src = src.rstrip() + export
    IDX.write_text(src, encoding="utf-8")

    # ── backend ────────────────────────────────────────────────────────
    pg = PG.read_text(encoding="utf-8")

    def repl_tuple(name: str, values: list[str], comment: str) -> None:
        nonlocal pg
        m = re.search(r"^%s\s*=\s*\(" % name, pg, re.M)
        assert m, name
        k = pg.index("(", m.start())
        d = 0
        for j in range(k, len(pg)):
            if pg[j] == "(":
                d += 1
            elif pg[j] == ")":
                d -= 1
                if d == 0:
                    break
        body = "".join(f'    "{v}",\n' for v in values)
        pg = pg[:m.start()] + f"{comment}\n{name} = (\n{body})" + pg[j + 1:]

    known = sorted(set(reg["backend_known"]) | set(approved))
    repl_tuple("REACT_TEMPLATES", known,
               "# Κάθε id που μπορεί να επιλεγεί. Αν λείπει, το /select-design\n"
               "# απαντά HTTP 400 ακόμη κι αν το theme αποδίδεται κανονικά.")
    repl_tuple("LAUNCH_REACT_TEMPLATES", approved,
               "# Ο κατάλογος που βλέπει ο πελάτης: κάθε εμπορικό theme που πέρασε QA.\n"
               "# ΔΕΝ περιλαμβάνει τα αρχέτυπα συμβατότητας του MAP.")
    PG.write_text(pg, encoding="utf-8")

    print("COMMERCIAL_THEMES :", len(commercial))
    print("APPROVED (QA+name):", len(approved))
    print("BLOCKED           :", blocked or "—")
    print("REACT_TEMPLATES   :", len(known))
    print("LAUNCH            :", len(approved))
    cats = sorted({CATALOG[i][2] for i in approved})
    print("ΚΑΤΗΓΟΡΙΕΣ        :", len(cats))
    for c in cats:
        print(f"   {c:26} {sum(1 for i in approved if CATALOG[i][2] == c)}")


if __name__ == "__main__":
    main()
