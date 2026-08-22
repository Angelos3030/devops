#!/usr/bin/env python3
"""Τα πέντε themes που αγνοούσαν το ανεβασμένο λογότυπο.

    python scripts/wire_brand_slot.py

Το `Brand.jsx` υλοποιεί ήδη κεντρικά το συμβόλαιο: αν υπάρχει `d.LOGO` το
δείχνει σε ελεγχόμενο μέγεθος, αλλιώς γράφει το όνομα της επιχείρησης.
54 από τα 59 αρχεία theme το χρησιμοποιούσαν. Πέντε όχι — εκεί ο πελάτης
ανέβαζε λογότυπο και δεν εμφανιζόταν πουθενά.

Το `dark` περνιέται όπου ΜΕΤΡΗΘΗΚΕ σκούρο φόντο πίσω από το brand slot
(cinematic 0.09, dispatch 0.08 φωτεινότητα) ώστε ένα σκούρο λογότυπο να μη
χάνεται· τα υπόλοιπα τρία κάθονται σε ανοιχτό (0.94–0.98).
"""
from __future__ import annotations

import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "sites" / "lib" / "templates"

# αρχείο -> (παλιό απόσπασμα, νέο, dark)
PATCHES = {
    "Canvas.jsx": [
        ('<span className={s.mark}>{d.NAME}</span>',
         '<Brand data={d} className={s.mark} />')],
    "Cinematic.jsx": [
        ('<a className={s.brand} href="#top" aria-label={`${d.NAME} — αρχική`}>{d.NAME}</a>',
         '<a className={s.brand} href="#top" aria-label={`${d.NAME} — αρχική`}>'
         '<Brand data={d} dark /></a>')],
    "Quiet.jsx": [
        ('<a href="#top" className={s.brand}>{d.NAME}</a>',
         '<a href="#top" className={s.brand}><Brand data={d} /></a>')],
    "TypeGallery.jsx": [
        ('<a href="#top" className={s.wordmark}>{d.NAME}</a>',
         '<a href="#top" className={s.wordmark}><Brand data={d} /></a>')],
    # Dispatch: το {d.NAME} εδώ είναι το h1 του hero, όχι brand slot. Αν
    # μπει εκεί λογότυπο, το 2.1em ενός τεράστιου h1 δίνει σήμα ~126px και
    # καταστρέφει τη διάταξη. Μπαίνει ΠΑΝΩ από τη γραμμή επαγγέλματος, σε
    # δικό του μικρό context, και το h1 μένει κείμενο για το SEO.
    "Dispatch.jsx": [
        ('<header className={s.head}>\n          <span className={s.trade}>{d.TRADE}</span>',
         '<header className={s.head}>\n'
         '          {d.LOGO && <Brand data={d} className={s.logoSlot} dark />}\n'
         '          <span className={s.trade}>{d.TRADE}</span>')],
}

CSS_ADD = {
    "Dispatch.module.css":
        "\n/* Slot λογοτύπου πελάτη: μικρό context ώστε το 2.1em του Brand να\n"
        "   βγάζει ~33px και να μην ανταγωνίζεται το όνομα. */\n"
        ".logoSlot{display:block;margin-bottom:14px;font-size:16px;line-height:0}\n",
}


def main() -> None:
    for fname, subs in PATCHES.items():
        p = T / fname
        s = io.open(p, encoding="utf-8").read()
        for old, new in subs:
            assert old in s, f"{fname}: δεν βρέθηκε\n{old[:80]}"
            s = s.replace(old, new, 1)
        if "from './Brand'" not in s:
            # μετά το τελευταίο import, ώστε να μη σπάσει η σειρά
            m = list(re.finditer(r"^import .*$", s, re.M))[-1]
            s = s[:m.end()] + "\nimport Brand from './Brand'" + s[m.end():]
        io.open(p, "w", encoding="utf-8").write(s)
        print(f"  ✓ {fname}")

    for fname, css in CSS_ADD.items():
        p = T / fname
        s = io.open(p, encoding="utf-8").read()
        if ".logoSlot" not in s:
            io.open(p, "w", encoding="utf-8").write(s.rstrip() + "\n" + css)
            print(f"  ✓ {fname}")

    # έλεγχος: κανένα εμπορικό theme δεν μένει χωρίς Brand
    missing = [f.name for f in T.glob("*.jsx")
               if f.name in PATCHES and "from './Brand'" not in io.open(f, encoding="utf-8").read()]
    assert not missing, missing
    print("\nόλα τα πέντε συνδέθηκαν με το Brand")


if __name__ == "__main__":
    main()
