"""Κατανομή του ευρετηρίου σε vertical οικογένειες.

Ντετερμινιστικό πρώτο πέρασμα: ό,τι δηλώνει καθαρά το επάγγελμά του μπαίνει
αμέσως. Ό,τι μένει «αταξινόμητο» ΔΕΝ πετιέται — τυπώνεται, ώστε να κριθεί με
απόδοση ή από το DeepSeek. Σιωπηλή απόρριψη δεν επιτρέπεται πουθενά εδώ.
"""
from __future__ import annotations

import re
import json
import sys
import pathlib

PATH = pathlib.Path("research/verticals/studio-index.json")

FAMILIES: dict[str, list[str]] = {
    "food": ["restaurant", "cafe", "coffee", "bakery", "pizza", "food", "eatery", "grill",
             "dining", "bistro", "kitchen", "chef", "catering", "burger", "sushi", "bar ",
             "brunch", "tavern", "juice", "dessert", "ice cream", "gelato", "patisserie"],
    "medical": ["medical", "health", "clinic", "dental", "dentist", "doctor", "hospital",
                "pharmac", "therapy", "wellness centre", "physio", "care center", "surgeon"],
    "beauty": ["salon", "barber", "spa", "beauty", "hair", "nail", "makeup", "cosmetic",
               "aesthetic", "massage", "skincare"],
    "trades": ["plumb", "electric", "hvac", "handyman", "repair service", "maintenance",
               "technician", "locksmith", "roofing", "cleaning service"],
    "construction": ["construction", "builder", "renovation", "carpenter", "architect",
                     "interior", "furniture", "woodwork", "contractor", "engineering"],
    "professional": ["law", "attorney", "legal", "account", "consult", "finance", "insurance",
                     "advisor", "corporate", "agency", "business", "startup", "saas", "office"],
    "property": ["real estate", "property", "realtor", "apartment", "house listing", "estate"],
    "hospitality": ["hotel", "resort", "villa", "room", "hostel", "bnb", "accommodation", "guest"],
    "fitness": ["gym", "fitness", "yoga", "pilates", "workout", "trainer", "crossfit", "sport"],
    "education": ["education", "school", "course", "academy", "university", "learn", "tutor",
                  "college", "campus", "kindergarten", "training"],
    "retail": ["shop", "store", "ecommerce", "e-commerce", "boutique", "fashion", "jewel",
               "florist", "product", "clothing", "market", "catalog"],
    "automotive": ["car ", "auto", "garage", "mechanic", "vehicle", "motor", "bike", "rental car"],
    "pets": ["pet", "vet", "animal", "dog", "cat ", "grooming"],
    "creative": ["photograph", "video", "artist", "creative", "studio", "portfolio", "design",
                 "gallery", "illustrat", "film", "cinema"],
    "events": ["wedding", "event", "venue", "party", "conference", "celebrat", "dj "],
    "tourism": ["travel", "tour", "trip", "adventure", "boat", "yacht", "vacation", "holiday",
                "destination", "explore"],
    "music": ["music", "band", "album", "song", "record", "concert", "festival", "podcast"],
    "content": ["blog", "magazine", "news", "journal", "article", "editorial", "creator"],
    "landing": ["landing", "app ", "mobile app", "software", "digital marketing", "seo"],
}


# Τα γενικά κρίνονται ΤΕΛΕΥΤΑΙΑ. Αλλιώς οι λέξεις «design/studio/portfolio/agency»
# —που υπάρχουν σχεδόν σε κάθε περιγραφή— καταπίνουν τα ειδικά επαγγέλματα:
# μετρήθηκε 77/226 στο «creative» ενώ το «hospitality» έβγαινε 0.
GENERIC = ("creative", "professional", "landing", "content", "retail")


def hit(keyword: str, text: str) -> bool:
    """Ταίριασμα σε όριο λέξης, όχι substring."""
    return re.search(rf"(?<![a-z]){re.escape(keyword.strip())}(?![a-z])", text) is not None


def bucket(rows: list[dict]) -> tuple[dict[str, list[dict]], list[dict]]:
    out: dict[str, list[dict]] = {k: [] for k in FAMILIES}
    rest: list[dict] = []
    specific = [f for f in FAMILIES if f not in GENERIC]
    for r in rows:
        name = r["name"].lower()
        blob = f"{name} {r.get('desc', '')}".lower()

        def score(fams: list[str]) -> list[tuple[str, int]]:
            # Το όνομα μετράει τριπλά: «gymso fitness» δηλώνει το επάγγελμα,
            # μια αναφορά «gym» μέσα σε παράγραφο συχνά είναι παράδειγμα χρήσης.
            # Με ΟΡΙΟ ΛΕΞΗΣ: χωρίς αυτό το «space dynamic» έμπαινε στο beauty
            # επειδή περιέχει «spa», και το «carousel» στο automotive λόγω «car».
            s = [(f, sum(len(k) * 3 for k in FAMILIES[f] if hit(k, name))
                  + sum(len(k) for k in FAMILIES[f] if hit(k, blob))) for f in fams]
            return [x for x in s if x[1]]

        hits = score(specific) or score(list(GENERIC))
        if hits:
            out[max(hits, key=lambda h: h[1])[0]].append(r)
        else:
            rest.append(r)
    return out, rest


if __name__ == "__main__":
    index = json.loads(PATH.read_text(encoding="utf-8"))
    rows = [dict(r, studio=s) for s, lst in index.items() for r in lst]
    buckets, rest = bucket(rows)
    want = sys.argv[1] if len(sys.argv) > 1 else None
    if want:
        for r in buckets.get(want, []) if want != "rest" else rest:
            print(f"{r['studio'][:4]:5} {r['name'][:32]:34} {r['url']}")
            print(f"      {r.get('desc', '')[:150]}")
    else:
        for fam, lst in sorted(buckets.items(), key=lambda x: -len(x[1])):
            print(f"{fam:15} {len(lst):3}  {', '.join(r['name'][:18] for r in lst[:6])}")
        print(f"{'ΑΤΑΞΙΝΟΜΗΤΑ':15} {len(rest):3}  {', '.join(r['name'][:18] for r in rest[:8])}")
