#!/usr/bin/env python3
"""Κανονικός κατάλογος themes: ταξινόμηση, ελληνικά ονόματα, κατηγορίες.

    python scripts/theme_library.py            # παράγει research/theme-library/library.json
    python scripts/theme_library.py --apply    # + γράφει frontend META και backend λίστες

Πηγή αλήθειας για το ΤΙ βλέπει ο πελάτης. Κάθε απόφαση εδώ είναι τεκμηριωμένη:
τα αρχέτυπα μένουν εσωτερικά, τα εμπορικά themes αποκτούν όνομα και κατηγορία.
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "theme-library"
IDX = ROOT / "sites" / "lib" / "templates" / "index.js"

# ── B. Αρχέτυπα συμβατότητας ────────────────────────────────────────────
# Στόχοι του MAP για τα legacy backend layout names. Είναι υποδομή, όχι
# προϊόν: ένα id σαν «grid» ή «sidebar» δεν είναι όνομα σχεδίου για πελάτη,
# και τα ίδια components εξυπηρετούν το fallback του pickTemplate().
ARCHETYPES = {
    "editorial", "split", "showcase", "bento", "longform",
    "corporate", "poster", "sidebar", "grid", "magazine",
}

# `warmth` και `coast` είναι ΕΠΙΣΗΣ τιμές του MAP, αλλά ονομάζονται από
# διάθεση και όχι από δομή, αποδίδουν διακριτή ταυτότητα, και το `warmth`
# χρησιμοποιείται ήδη ως showcase στη δημόσια αρχική. Μένουν εμπορικά.

# ── C. Proof / πειραματικά ──────────────────────────────────────────────
MASTER = {"MasterCinematic", "MasterEditorial", "MasterSpatial"}

# ── Ελληνικά ονόματα για όσα εμπορικά τα στερούνταν ─────────────────────
# Περιγράφουν τον οπτικό χαρακτήρα, όχι την υλοποίηση.
NEW_META = {
    "aegean":    ("Αιγαίο", "Κυκλαδίτικο φως, μεγάλη θαλασσινή φωτογραφία και ήρεμη τυπογραφία."),
    "bloom":     ("Άνθιση", "Καθαρό λευκό με στρογγυλή φωτογραφία-ήρωα και ζεστό πράσινο κουμπί."),
    "callout":   ("Επείγουσα Κλήση", "Σκούρο, με το τηλέφωνο βλάβης σε πρώτο πλάνο. Για 24/7 εξυπηρέτηση."),
    "canvas":    ("Καμβάς", "Ήσυχο editorial με μεγάλη εικόνα και serif αφήγηση."),
    "cinematic": ("Κινηματογραφικό", "Σκούρο, γεμάτο φωτογραφία, με μεγάλη χειρόγραφη τυπογραφία."),
    "coast":     ("Ακτή", "Ανοιχτό και θαλασσινό, με ευρύχωρο hero και γαλάζιο τόνο."),
    "dispatch":  ("Βάρδια", "Σκούρο τεχνικό, με τηλέφωνο και λίστα υπηρεσιών σε κάρτα."),
    "ember":     ("Χόβολη", "Πολύ σκούρο με πορτοκαλί λάμψη. Δραματικό για βραδινή εστίαση."),
    "forge":     ("Σφυρήλατο", "Βιομηχανικό, με κίτρινη ταινία και τούβλο. Για τεχνικά επαγγέλματα."),
    "infinite":  ("Συνεχές", "Αδιάκοπη ροή φωτογραφιών, χωρίς ορατές τομές ενοτήτων."),
    "kinetic":   ("Κινητικό", "Έντονο lime και μεγάλα γράμματα. Νεανικό και θορυβώδες."),
    "living":    ("Καθημερινό", "Ζεστό και οικείο, με τη φωτογραφία του προϊόντος μπροστά."),
    "marble":    ("Μάρμαρο", "Λευκό και λιτό, με μία εικόνα και πολύ αέρα γύρω της."),
    "motor":     ("Μοτέρ", "Σκούρο γκαράζ με κόκκινο τόνο και δελτίο εργασιών."),
    "pulse":     ("Παλμός", "Καθαρό και αθλητικό, με εξοπλισμό σε πρώτο πλάνο."),
    "quiet":     ("Ησυχία", "Σχεδόν μόνο τυπογραφία. Ο μέγιστος δυνατός αέρας."),
    "runway":    ("Πασαρέλα", "Ασπρόμαυρη φωτογραφία με χειρόγραφο ροζ accent."),
    "signature": ("Υπογραφή", "Προσωπικό ύφος, με serif όνομα και μία τονισμένη λέξη."),
    "terra":     ("Γη", "Γήινοι τόνοι και χαλαρός ρυθμός. Για ευεξία και φροντίδα."),
    "volt":      ("Βολτ", "Σκούρο και τεχνολογικό, με πράσινο τόνο."),
    "warmth":    ("Ζεστασιά", "Ζεστή φωτογραφία φαγητού και κρεμ ενότητες."),
}

# ── Κατηγορίες, αντλημένες από τα υπαρκτά verticals του backend ─────────
VERTICAL_CATEGORY = {
    "food": "Εστίαση", "cafe": "Εστίαση", "bakery": "Εστίαση",
    "beauty": "Ομορφιά", "aesthetics": "Ομορφιά",
    "dentist": "Υγεία", "doctor": "Υγεία", "pharmacy": "Υγεία", "massage": "Υγεία",
    "trade": "Τεχνικά επαγγέλματα", "wood": "Τεχνικά επαγγέλματα",
    "garage": "Τεχνικά επαγγέλματα",
    "rooms": "Τουρισμός & διαμονή",
    "realestate": "Ακίνητα",
    "retail": "Λιανική", "pet": "Λιανική",
    "gym": "Γυμναστήριο & ευεξία",
    "professional": "Επαγγελματικές υπηρεσίες",
    "education": "Εκπαίδευση", "logistics": "Μεταφορές & Logistics",
    "farm": "Αγροτικά",
}

# Vertical για τα themes που δεν ανήκουν σε κανένα vertical του backend.
# Προκύπτει από την ταυτότητα του ίδιου του theme, όχι αυθαίρετα.
OVERRIDE_VERTICAL = {
    "klassy-cafe": "cafe", "frost-bakery": "bakery", "moso-interior": "wood",
    "barber-shop": "beauty", "billys-barber": "beauty", "thomson-stylist": "beauty",
    "gymso-fitness": "gym", "pulse": "gym", "medic-care": "doctor",
    "villa-agency": "realestate", "coast": "rooms", "clean-work": "trade",
    "blue-onepage": "professional", "corporate": "professional", "showcase": "retail",
    "educenter-campus": "education", "freight-lane": "logistics",
}


def load() -> dict:
    reg = json.loads((OUT / "registry.json").read_text(encoding="utf-8"))
    qa = {r["id"]: r for r in json.loads((OUT / "qa.json").read_text(encoding="utf-8"))}
    src = IDX.read_text(encoding="utf-8")
    meta = {}
    seg = src[src.find("TEMPLATE_META"):]
    for match in re.finditer(r"\n  '?([\w-]+)'?:\s*\{", seg):
        key = match.group(1)
        start = match.end() - 1
        depth = 0
        for end in range(start, len(seg)):
            if seg[end] == "{":
                depth += 1
            elif seg[end] == "}":
                depth -= 1
                if depth == 0:
                    break
        body = seg[start:end]
        lab = re.search(r"label:\s*'([^']*)'", body)
        des = re.search(r"desc:\s*'([^']*)'", body)
        meta[key] = {"label": lab.group(1) if lab else "", "desc": des.group(1) if des else ""}
    return reg, qa, meta


def build() -> dict:
    reg, qa, meta = load()
    vert = dict(OVERRIDE_VERTICAL)
    for v, keys in reg["by_vertical"].items():
        for k in keys:
            vert.setdefault(k, v)

    lib = {}
    for tid in sorted(reg["render_ids"]):
        q = qa.get(tid, {})
        if tid in ARCHETYPES:
            cls = "archetype"
        else:
            cls = "commercial"
        label, desc = "", ""
        if tid in meta and meta[tid]["label"]:
            label, desc = meta[tid]["label"], meta[tid]["desc"]
        elif tid in NEW_META:
            label, desc = NEW_META[tid]
        v = vert.get(tid, "trade")
        entry = {
            "id": tid,
            "class": cls,
            "label": label,
            "desc": desc,
            "vertical": v,
            "category": VERTICAL_CATEGORY.get(v, "Άλλο"),
            "qa": "pass" if q.get("pass") else "fail",
            "qa_fail": q.get("fail", []),
            "preview_url": q.get("url", ""),
            "backend_known": tid in reg["backend_known"],
            "offered_before": tid in reg["backend_launch"],
        }
        if cls == "commercial" and not label:
            entry["class"] = "blocked"
            entry["qa_fail"] = entry["qa_fail"] + ["λείπει ελληνικό όνομα"]
        if entry["qa"] == "fail" and entry["class"] == "commercial":
            entry["class"] = "blocked"
        lib[tid] = entry
    return lib


def main() -> None:
    lib = build()
    OUT.mkdir(parents=True, exist_ok=True)
    io.open(OUT / "library.json", "w", encoding="utf-8").write(
        json.dumps(lib, ensure_ascii=False, indent=1))

    from collections import Counter
    c = Counter(e["class"] for e in lib.values())
    comm = [e for e in lib.values() if e["class"] == "commercial"]
    print("RENDERABLE_IDS      :", len(lib))
    print("COMMERCIAL_THEMES   :", c["commercial"])
    print("ARCHETYPES_INTERNAL :", c["archetype"])
    print("BLOCKED             :", c["blocked"])
    print("QA_PASS (σύνολο)    :", sum(1 for e in lib.values() if e["qa"] == "pass"))
    print()
    cats = Counter(e["category"] for e in comm)
    for k, n in cats.most_common():
        print(f"  {k:26} {n}")
    missing = [e["id"] for e in lib.values() if e["class"] == "commercial" and not e["backend_known"]]
    print()
    print("ΕΜΠΟΡΙΚΑ ΑΓΝΩΣΤΑ ΣΤΟ BACKEND (χρειάζονται εγγραφή):", len(missing))
    print(" ", " ".join(missing))
    blocked = [(e["id"], e["qa_fail"]) for e in lib.values() if e["class"] == "blocked"]
    if blocked:
        print()
        print("BLOCKED:")
        for i, why in blocked:
            print(f"  {i:22} {', '.join(why)}")


if __name__ == "__main__":
    main()
