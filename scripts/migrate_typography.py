#!/usr/bin/env python3
"""Μεταφέρει τα themes σε ΔΥΟ σημασιολογικούς ρόλους τυπογραφίας.

    python scripts/migrate_typography.py --check    # τι θα άλλαζε
    python scripts/migrate_typography.py            # γράφει

    --vt-display   επικεφαλίδες / επώνυμα στοιχεία
    --vt-body      τρεχούμενο κείμενο

ΓΙΑΤΙ. Η μέτρηση έδειξε ότι μόνο 23/58 themes άλλαζαν γραμματοσειρά. Η αιτία
ΔΕΝ ήταν ότι «γράφουν σκληρά font-family»: το συμβόλαιο υπερίσχυε σε τρία
ονόματα (--display, --serif, --sans) ενώ η βιβλιοθήκη χρησιμοποιεί ΔΩΔΕΚΑ
(--body, --disp, --cond, --font-body, --font-display, --vt-body,
--vt-font-body, --vt-font-display, --mono, …). Δεκαοκτώ themes ήταν ήδη
παραμετρικά — απλώς με όνομα που κανείς δεν διάβαζε.

ΤΑΥΤΟΤΗΤΑ ΚΑΤΑ ΚΑΤΑΣΚΕΥΗ. Κάθε αντικατάσταση κρατά την αρχική τιμή ως
fallback: `var(--vt-body, <ό,τι έγραφε πριν>)`. Χωρίς επιλεγμένο ζεύγος, ο
ρόλος είναι ακαθόριστος και αποδίδεται ΑΚΡΙΒΩΣ η παλιά τιμή. Το default δεν
μπορεί να αλλάξει — δεν είναι ελπίδα, είναι ιδιότητα του `var()`.

ΤΙ ΔΕΝ ΑΓΓΙΖΕΤΑΙ. Ούτε mono, ούτε condensed δεύτερη όψη, ούτε `inherit`, ούτε
διακοσμητικά one-off. Αυτά είναι ιεραρχία, όχι «η γραμματοσειρά του site»:
στο MasterEditorial η condensed μαστίγα ΔΙΠΛΑ σε serif σώμα είναι η σύνθεση.
Αν τα ισοπεδώναμε όλα σε έναν ρόλο, το ζεύγος γραμματοσειρών θα «δούλευε»
στη μέτρηση και θα κατέστρεφε τη σχεδίαση. Όποιο theme μένει έτσι με
ανεπαίσθητη αλλαγή, ταξινομείται T-C — δεν πιέζεται.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "sites" / "lib" / "templates"

# ── 1. Ονόματα που είναι ΗΔΗ παραμετρικά, απλώς με άλλο όνομα ──────────────
# Η σημασιολογία επαληθεύτηκε ανά αρχείο: παντού display-vs-body, ποτέ κάτι
# άλλο. Το --cond και το --mono ΔΕΝ μπαίνουν: είναι δεύτερη όψη, όχι ρόλος.
ALIAS = {
    "--display": "--vt-display", "--disp": "--vt-display",
    "--serif": "--vt-display", "--font-display": "--vt-display",
    "--vt-font-display": "--vt-display",
    "--sans": "--vt-body", "--body": "--vt-body",
    "--font-body": "--vt-body", "--vt-font-body": "--vt-body",
}

# ── 2. Πότε μια ΣΚΛΗΡΗ δήλωση είναι τίτλος και πότε κείμενο ────────────────
HEAD = re.compile(r"\b(h1|h2|h3|h4|h5|h6)\b|brand|monogram|\.title\b")
ROOTSEL = re.compile(r"^\.(root|wrap|bar|patisserie|urban|greekBakery|brunch|micro|"
                     r"nordic|scandi|heritage|directory)\b[^,]*$")
# Ό,τι δεν πιάνεται από τα δύο παραπάνω μένει ΑΘΙΚΤΟ επίτηδες.
SKIP = re.compile(r"mono|inherit|Narrow|Condensed", re.I)


def selector_before(css: str, pos: int) -> str:
    # Τα σχόλια πριν από τον selector τον έκρυβαν: το CafeCollection γράφει
    # «/* … */ .patisserie {» και το «^\.» δεν έπιανε ποτέ.
    head = re.sub(r"/\*.*?\*/", " ", css[:pos], flags=re.S)
    m = re.findall(r"([^{};]+)\{[^{}]*$", head)
    return m[-1].strip().replace("\n", " ") if m else ""


def migrate(path: Path) -> tuple[str, list[str]]:
    css = io.open(path, encoding="utf-8").read()
    log: list[str] = []

    # 2α. Ορισμοί τοπικών ονομάτων -> παίρνουν τον ρόλο ως fallback
    for local, role in ALIAS.items():
        pat = re.compile(r"(" + re.escape(local) + r")\s*:\s*([^;}]+?)\s*(?=[;}])")
        def sub(m):
            val = m.group(2)
            if val.startswith("var(--vt-"):
                return m.group(0)
            log.append(f"ορισμός {local} -> var({role}, …)")
            return f"{m.group(1)}: var({role}, {val})"
        css = pat.sub(sub, css)

    # 2β. Χρήσεις ακαθόριστων ονομάτων -> ο ρόλος ΜΠΡΟΣΤΑ, με το αρχικό
    #     var() ως fallback, ώστε να διατηρηθεί το per-site fallback αυτούσιο.
    for local, role in ALIAS.items():
        pat = re.compile(r"font-family\s*:\s*var\(\s*" + re.escape(local) + r"\s*,\s*([^)]+)\)")
        def sub2(m):
            log.append(f"χρήση var({local}) -> var({role}, var({local}, …))")
            return f"font-family: var({role}, var({local}, {m.group(1)}))"
        css = pat.sub(sub2, css)

    # 2γ. Σκληρές δηλώσεις -> ρόλος με την αρχική τιμή ως fallback
    out, last = [], 0
    for m in re.finditer(r"font-family\s*:\s*([^;}]+)", css):
        val = m.group(1).strip()
        if "var(" in val:
            continue
        sel = selector_before(css, m.start())
        # Το SKIP προστατεύει ΔΕΥΤΕΡΗ όψη (condensed δίπλα σε serif, mono για
        # αριθμούς). Στη ρίζα δεν υπάρχει δεύτερη όψη — εκεί είναι η
        # γραμματοσειρά σώματος. Το moso-interior γράφει condensed ΩΣ σώμα και
        # έμενε αμετάβλητο: μετρήθηκε 0.0% σε κάθε ζεύγος.
        if SKIP.search(val) and not ROOTSEL.match(sel):
            continue
        role = ("--vt-display" if HEAD.search(sel)
                else "--vt-body" if ROOTSEL.match(sel) else None)
        if not role:
            continue
        out.append((m.start(), m.end(), f"font-family: var({role}, {val})"))
        log.append(f"σκληρό «{sel[:34]}» -> {role}")
    for s, e, rep in reversed(out):
        css = css[:s] + rep + css[e:]

    return css, log


def main() -> None:
    check = "--check" in sys.argv
    total = 0
    for path in sorted(TPL.glob("*.module.css")):
        new, log = migrate(path)
        if not log:
            continue
        total += len(log)
        print(f"\n  {path.name}  ({len(log)})")
        for line in log[:6]:
            print(f"      {line}")
        if len(log) > 6:
            print(f"      … +{len(log) - 6}")
        if not check:
            io.open(path, "w", encoding="utf-8").write(new)
    print(f"\n  ΣΥΝΟΛΟ {total} αντικαταστάσεις" + ("  (έλεγχος μόνο)" if check else "  ΓΡΑΦΤΗΚΑΝ"))


if __name__ == "__main__":
    main()
