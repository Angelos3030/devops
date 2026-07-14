"""Generate the 3 premium Vitrina site variants + approve page for a client.

Usage:
    python -m scripts.generate_client_site            # runs the Koutrakis demo
    (or import build_gallery_page with your own intake)

Proves the automatic template pipeline: intake dict -> 3 static HTML sites +
a chooser page where the client presses "Approve". Zero API tokens.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.premium_generator import build_gallery_page, recommend_layout  # noqa: E402

OUT_DIR = ROOT / "web" / "clients"
# Koutrakis assets already live here; auto output reuses them via relative path.
ASSET = "../koutrakis-xylourgos/assets"

KOUTRAKIS = {
    "name": "Κουτράκης",
    "type": "Ξυλουργός / Έπιπλα",
    "trade": "Ξυλουργικό εργαστήριο",
    "city": "Γέρακας",
    "phone": "6956297670",
    "site_url": "https://koutrakiskouzines.gr",
    "tagline": "Χειροποίητες κουζίνες, ντουλάπες και έπιπλα στα μέτρα σου — με φυσικά υλικά και φινίρισμα που κρατάει χρόνια.",
    "intro": "Σχεδιάζουμε και κατασκευάζουμε κουζίνες, ντουλάπες και έπιπλα στα μέτρα σου — με καθαρές γραμμές και προσοχή στη λεπτομέρεια.",
    "story_title": "Ένας μάστορας, από την ιδέα ως την τοποθέτηση.",
    "story_paragraphs": [
        "Ο Κώστας Κουτράκης δουλεύει το ξύλο με μεράκι στον Γέρακα. Κάθε κατασκευή ξεκινά με μια κουβέντα για το πώς ζεις τον χώρο σου.",
        "Χωρίς έτοιμες λύσεις, χωρίς κρυφές χρεώσεις — καθαρή τιμή, φυσικά υλικά και συνέπεια στον χρόνο παράδοσης.",
    ],
    "cta_title": "Πες μας τι έχεις στο μυαλό σου.",
    "areas": ["Γέρακας", "Παλλήνη", "Γλυκά Νερά", "Ανατολικά Προάστια"],
    "services": [
        {"name": "Εντοιχισμός κουζίνας", "description": "Τοποθέτηση με σωστές ενώσεις και πρακτική διάταξη για καθημερινή χρήση."},
        {"name": "Ντουλάπες & αποθηκευτικοί χώροι", "description": "Λύσεις που αξιοποιούν κάθε εκατοστό, στα μέτρα του χώρου σου."},
        {"name": "Ξύλινα κρεβάτια & έπιπλα", "description": "Ανθεκτικές, ιδιαίτερες κατασκευές που δεν βρίσκεις έτοιμες."},
        {"name": "Πόρτες & παράθυρα", "description": "Κατασκευή, επισκευή και συντήρηση ξύλινων πορτών και παραθύρων."},
        {"name": "Μερεμέτια & λουστράρισμα", "description": "Μικρές επισκευές και ανανεώσεις σε έπιπλα, πόρτες και ράφια."},
    ],
    "hero_image": f"{ASSET}/modern-kitchen.jpg",
    "workshop_image": f"{ASSET}/wood-table-workshop.jpg",
    "gallery": [
        {"image": f"{ASSET}/marble-kitchen.jpg", "title": "Ανακαίνιση κουζίνας", "sub": "Γέρακας"},
        {"image": f"{ASSET}/carved-sideboard.jpg", "title": "Σκαλιστή πρόσοψη", "sub": "Custom έπιπλο"},
        {"image": f"{ASSET}/walnut-sideboard.jpg", "title": "Μπουφές καρυδιάς", "sub": "Σαλόνι"},
        {"image": f"{ASSET}/kids-bunk-bed.jpg", "title": "Παιδική κουκέτα", "sub": "Παιδικό δωμάτιο"},
        {"image": f"{ASSET}/wardrobe-built-in.jpg", "title": "Εντοιχισμένη ντουλάπα", "sub": "Υπνοδωμάτιο"},
        {"image": f"{ASSET}/study-desk.jpg", "title": "Γραφείο & ράφια", "sub": "Γραφείο"},
        {"image": f"{ASSET}/rounded-cabinet.jpg", "title": "Καμπύλο έπιπλο", "sub": "Σαλόνι"},
        {"image": f"{ASSET}/classic-table.jpg", "title": "Κλασική τραπεζαρία", "sub": "Τραπεζαρία"},
    ],
}


def main() -> int:
    slug = "koutrakis-auto"
    chooser = build_gallery_page(KOUTRAKIS, slug, OUT_DIR)
    print(f"Recommended layout: {recommend_layout(KOUTRAKIS)}")
    print(f"Generated variants in: {OUT_DIR / slug}")
    print(f"Chooser/approve page:    {chooser}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
