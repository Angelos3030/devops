#!/usr/bin/env python3
"""
Κατεβάζει τα Google Fonts ΤΟΠΙΚΑ, ώστε τα sites των πελατών να μη ζητάνε τίποτα
από την Google.

    python scripts/selfhost_fonts.py

Δύο λόγοι:
  1. **GDPR** — κάθε φόρτωση από fonts.googleapis.com στέλνει την IP του
     επισκέπτη στην Google χωρίς συγκατάθεση. Γερμανικό δικαστήριο το έκρινε
     παραβίαση (LG München, 2022). Έτσι δεν χρειάζεται καν banner.
  2. **Ταχύτητα** — γλιτώνουμε DNS + TLS προς δύο ξένους servers πριν φανεί
     γράμμα στην οθόνη.

Κρατάμε ΜΟΝΟ ελληνικά + λατινικά. Τα κυριλλικά/βιετναμέζικα που στέλνει η
Google είναι σκέτο βάρος για ελληνικό μαγαζί.

Ξανατρέξ' το μόνο αν αλλάξεις τη λίστα FAMILIES παρακάτω.
"""
from __future__ import annotations

import os
import re
import ssl
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "sites", "public", "fonts")
OUT_CSS = os.path.join(ROOT, "sites", "app", "fonts.css")

# Η πηγή της αλήθειας για το ποια fonts υπάρχουν. Αν προσθέσεις font σε template,
# πρόσθεσέ το ΚΑΙ εδώ και ξανατρέξε — αλλιώς το template πέφτει σιωπηλά σε Arial.
# Το sites/tests/design_guard.mjs το πιάνει αν ξεχαστεί.
FAMILIES = [
    "Anton",
    "Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400",
    "Inter:wght@400;500;600;700",
    "JetBrains+Mono:wght@400;500",
    "Nunito+Sans:wght@400;600;700",
    "Fira+Sans+Condensed:wght@600;700;800",
    "Alegreya:ital,wght@0,400;0,500;0,700;1,500",
    "Noto+Serif+Display:ital,wght@0,300;0,400;0,500;1,300",
    "EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500",
    "Manrope:wght@400;600;800",
    "Roboto+Slab:wght@500;700",
    "Literata:ital,opsz,wght@0,7..72,300;0,7..72,400;1,7..72,300",
    "Comfortaa:wght@500;700",
    "Fira+Sans:wght@400;600",
    "Syne:wght@700;800",
    "Open+Sans:wght@400;600",
    "Roboto+Condensed:wght@400;700",     # Motor — έλειπε, έπεφτε σε Inter
    "Noto+Sans+Display:wght@400;600;700",  # Pulse — έλειπε, έπεφτε σε Arial
]
CSS_URL = ("https://fonts.googleapis.com/css2?"
           + "&".join(f"family={f}" for f in FAMILIES) + "&display=swap")

# Ό,τι δεν είναι εδώ πετιέται. Τα ελληνικά είναι ο λόγος που υπάρχει το project.
KEEP = {"greek", "greek-ext", "latin", "latin-ext"}

# Χωρίς UA σύγχρονου browser η Google στέλνει ttf αντί για woff2 (4x μεγαλύτερα).
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def fetch(url: str) -> bytes:
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(r, timeout=60, context=_ctx).read()


def main() -> int:
    print(f"Κατεβάζω {len(FAMILIES)} οικογένειες από την Google…")
    css = fetch(CSS_URL).decode("utf-8")

    os.makedirs(OUT_DIR, exist_ok=True)
    # Η Google βάζει /* greek */ πριν από κάθε @font-face — έτσι ξεχωρίζουμε subset.
    blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    print(f"Βρήκα {len(blocks)} @font-face· κρατάω {', '.join(sorted(KEEP))}.\n")

    out, kept, skipped, bytes_total = [], 0, 0, 0
    seen: dict[str, str] = {}

    for subset, block in blocks:
        if subset not in KEEP:
            skipped += 1
            continue
        url_m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", block)
        fam_m = re.search(r"font-family:\s*'([^']+)'", block)
        if not url_m or not fam_m:
            continue
        url = url_m.group(1)

        if url in seen:
            local = seen[url]
        else:
            fam = re.sub(r"[^A-Za-z0-9]+", "-", fam_m.group(1)).strip("-").lower()
            wght = (re.search(r"font-weight:\s*([\d ]+)", block) or [None, "400"])[1].replace(" ", "-")
            ital = "i" if "italic" in block else ""
            local = f"{fam}-{subset}-{wght}{ital}-{len(seen)}.woff2"
            data = fetch(url)
            with open(os.path.join(OUT_DIR, local), "wb") as fh:
                fh.write(data)
            bytes_total += len(data)
            seen[url] = local
            print(f"  ✓ {local:<52} {len(data) / 1024:6.1f} KB")

        out.append(block.replace(url, f"/fonts/{local}"))
        kept += 1

    header = (
        "/* ΜΗΝ ΤΟ ΑΛΛΑΞΕΙΣ ΣΤΟ ΧΕΡΙ — παράγεται από scripts/selfhost_fonts.py\n"
        " *\n"
        " * Τα fonts σερβίρονται από εμάς, όχι από την Google: η IP του επισκέπτη\n"
        " * δεν φεύγει ποτέ προς τα έξω (GDPR) και το site φορτώνει πιο γρήγορα.\n"
        " */\n"
    )
    with open(OUT_CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + "\n".join(out) + "\n")

    print(f"\n✅ {kept} @font-face ({len(seen)} αρχεία, {bytes_total / 1024 / 1024:.2f} MB)")
    print(f"   αγνοήθηκαν {skipped} σε γλώσσες που δεν μας αφορούν")
    print(f"   → {os.path.relpath(OUT_CSS, ROOT)}")
    print("\nΜένει: βγάλε το <link> της Google από το layout.jsx και βάλε")
    print("       import './fonts.css'  δίπλα στο import './globals.css'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
