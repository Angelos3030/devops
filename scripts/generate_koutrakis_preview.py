from __future__ import annotations

import sys
import shutil
import html as html_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.local_site_generator import generate_site_variants, theme_description, theme_label  # noqa: E402


CLIENT_SLUG = "koutrakis-xylourgos"
SOURCE_ASSETS = Path(r"C:\Users\pbadmin\Desktop\KOSTAS")
ASSET_FILES = {
    "chair-detail.jpg": "2acbba91-fe86-4d8d-afe7-8267fc8af86e.jpg",
    "carved-sideboard.jpg": "80db1629-b788-4a78-b386-8e940d34b594.jpg",
    "chair-finished.jpg": "0684bcf7-fae2-4e15-aa43-a30204956e03.jpg",
    "custom-bike.jpg": "475773482_940642238264248_4365404315656711153_n.jpg",
    "rounded-cabinet.jpg": "d10bded2-83a6-43a7-bd91-e6308cee4287.jpg",
    "wood-bike-frame.jpg": "download (1).jpg",
    "classic-table.jpg": "download.jpg",
    "kids-bunk-bed.jpg": "2c6ffe95-eb87-4d94-bf52-ad39166a0cc5.jpg",
    "modern-kitchen.jpg": "download (10).jpg",
    "custom-chair-pair.jpg": "download (11).jpg",
    "wood-table-workshop.jpg": "download (12).jpg",
    "glass-cabinet.jpg": "download (13).jpg",
    "walnut-sideboard.jpg": "download (14).jpg",
    "white-kitchen.jpg": "download (15).jpg",
    "classic-kitchen.jpg": "download (19).jpg",
    "marble-kitchen.jpg": "download (21).jpg",
    "wardrobe-built-in.jpg": "download (22).jpg",
    "retro-corner.jpg": "download (24).jpg",
    "pink-nightstand.jpg": "download (26).jpg",
    "dining-set.jpg": "download (27).jpg",
    "kids-desk.jpg": "download (28).jpg",
    "wood-cart.jpg": "download (31).jpg",
    "country-kitchen.jpg": "download (4).jpg",
    "study-desk.jpg": "download (8).jpg",
    "retro-nightstand.jpg": "download (9).jpg",
}

KOUTRAKIS_ROUTE_COPY = {
    "premium": {
        "label": "Construction Pro",
        "description": "Σαν contractor site: δυνατό hero, έργα μπροστά, καθαρή αίσθηση επαγγελματία.",
    },
    "trust": {
        "label": "Handyman Call-first",
        "description": "Σαν μάστορας/υπηρεσίες: τηλέφωνο πρώτο, υπηρεσίες καθαρές, γρήγορη εμπιστοσύνη.",
    },
    "editorial": {
        "label": "Interior Portfolio",
        "description": "Σαν interior/furniture portfolio: πιο premium, πιο φωτογραφικό, για να πουλάει τη δουλειά.",
    },
}


def main() -> int:
    output_dir = ROOT / "web" / "clients" / CLIENT_SLUG
    asset_dir = output_dir / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    for target_name, source_name in ASSET_FILES.items():
        source_path = SOURCE_ASSETS / source_name
        if not source_path.exists():
            print(f"Missing source image: {source_path}", file=sys.stderr)
            return 1
        shutil.copyfile(source_path, asset_dir / target_name)

    intake = {
        "name": "Κώστας Κουτράκης",
        "type": "Ξυλουργός / Μαραγκός",
        "trade": "Ξυλουργός",
        "city": "Αθήνα",
        "address": "Γέρακας 15344, Αθήνα, Ελλάδα",
        "phone": "6956297670",
        "site_url": "https://koutrakiskouzines.gr",
        "style": "Ξυλουργικές κατασκευές στα μέτρα σου, με καθαρή συνεννόηση και προσεγμένο φινίρισμα",
        "areas": ["Γέρακας", "Αθήνα", "Ανατολικά Προάστια", "Γύρω περιοχές"],
        "services": [
            {
                "SERVICE_NAME": "Εντοιχισμός κουζίνας",
                "SERVICE_DESC": "Τοποθέτηση και προσαρμογή κουζίνας με σωστή εφαρμογή στον χώρο.",
            },
            {
                "SERVICE_NAME": "Ανακαίνιση ντουλαπιών κουζίνας",
                "SERVICE_DESC": "Ανανέωση, επισκευή ή αλλαγές σε ντουλάπια, μεντεσέδες, προσόψεις και αποθηκευτικούς χώρους.",
            },
            {
                "SERVICE_NAME": "Ξυλουργικά μερεμέτια",
                "SERVICE_DESC": "Μικρές επισκευές και βελτιώσεις σε έπιπλα, πόρτες, ράφια και ξύλινες κατασκευές στην Αθήνα.",
            },
            {
                "SERVICE_NAME": "Ξύλινα ράφια και πάγκοι κουζίνας",
                "SERVICE_DESC": "Κατασκευή διακοσμητικών συνθέσεων, ξύλινων στηριγμάτων και πάγκων στα μέτρα σου.",
            },
            {
                "SERVICE_NAME": "Ξύλινα κρεβάτια",
                "SERVICE_DESC": "Κατασκευή και προσαρμογή ξύλινων κρεβατιών με πρακτική και ανθεκτική λύση.",
            },
            {
                "SERVICE_NAME": "Ντουλάπες",
                "SERVICE_DESC": "Εγκατάσταση, επισκευή και προσαρμογή ντουλάπας για καλύτερη οργάνωση χώρου.",
            },
            {
                "SERVICE_NAME": "Ξύλινες πόρτες και παράθυρα",
                "SERVICE_DESC": "Κατασκευή, επισκευή και συντήρηση για ξύλινες πόρτες και παράθυρα.",
            },
            {
                "SERVICE_NAME": "Λουστράρισμα και ξύλινες συνθέσεις",
                "SERVICE_DESC": "Λουστράρισμα επίπλων και σύνθετες ξυλουργικές εργασίες όπως τραπέζια, καρέκλες και βιβλιοθήκες.",
            },
        ],
        "seo_keywords": [
            "Εντοιχισμός κουζίνας Αθήνα",
            "Ανακαίνιση ντουλαπιών κουζίνας",
            "Ξυλουργικά μερεμέτια Αθήνα",
            "Ξύλινα ράφια κουζίνας",
            "Ξύλινοι πάγκοι κουζίνας",
            "Κατασκευή ξύλινων κρεβατιών",
            "Επισκευή ντουλάπας Αθήνα",
            "Ξύλινες πόρτες Αθήνα",
            "Ξύλινα παράθυρα Αθήνα",
            "Λουστράρισμα επίπλων",
            "Ξύλινες συνθέσεις",
            "Κατασκευή ξύλινων επίπλων",
        ],
        "hero_image": "assets/rounded-cabinet.jpg",
        "workshop_image": "assets/carved-sideboard.jpg",
        "slides": [
            {
                "image": "assets/modern-kitchen.jpg",
                "title": "Εντοιχισμός κουζίνας",
                "description": "Καθαρή τοποθέτηση, σωστές ενώσεις και πρακτική διάταξη για καθημερινή χρήση.",
                "alt": "Μοντέρνα εντοιχισμένη κουζίνα σε ξύλο και λευκά ντουλάπια",
            },
            {
                "image": "assets/marble-kitchen.jpg",
                "title": "Ανακαίνιση κουζίνας",
                "description": "Ανανέωση ντουλαπιών, πάγκων και αποθηκευτικών χώρων με προσεγμένο φινίρισμα.",
                "alt": "Ανακαινισμένη λευκή κουζίνα με ξύλινα στοιχεία",
            },
            {
                "image": "assets/kids-bunk-bed.jpg",
                "title": "Ξύλινα κρεβάτια στα μέτρα σου",
                "description": "Custom λύσεις για παιδικό δωμάτιο, με έμφαση στην αντοχή και τη λειτουργικότητα.",
                "alt": "Ξύλινη κουκέτα σε παιδικό δωμάτιο",
            },
            {
                "image": "assets/walnut-sideboard.jpg",
                "title": "Κατασκευή ξύλινων επίπλων",
                "description": "Σκαλιστές προσόψεις, ιδιαίτερα έπιπλα και λύσεις που ταιριάζουν στο ύφος του χώρου.",
                "alt": "Ξύλινος μπουφές με σκαλιστή πρόσοψη",
            },
            {
                "image": "assets/wood-cart.jpg",
                "title": "Ειδικές ξύλινες κατασκευές",
                "description": "Όταν η δουλειά δεν είναι τυποποιημένη, σχεδιάζεται και φτιάχνεται από την αρχή.",
                "alt": "Ειδική ξύλινη κατασκευή με ρόδες",
            },
            {
                "image": "assets/custom-bike.jpg",
                "title": "Custom ξύλινες λύσεις",
                "description": "Ξύλινες συνθέσεις και εφαρμογές με χαρακτήρα, για σπίτι ή ιδιαίτερο project.",
                "alt": "Custom ξύλινη κατασκευή πάνω σε ποδήλατο",
            },
            {
                "image": "assets/study-desk.jpg",
                "title": "Γραφεία και ράφια",
                "description": "Πάγκοι, γραφεία και ράφια που αξιοποιούν σωστά τον χώρο.",
                "alt": "Ξύλινο γραφείο με καρέκλα και laptop",
            },
            {
                "image": "assets/chair-finished.jpg",
                "title": "Επισκευή και ανανέωση καρέκλας",
                "description": "Ξυλουργικά μερεμέτια και ανανεώσεις που κρατούν τα έπιπλα ζωντανά.",
                "alt": "Ανανεωμένη ξύλινη καρέκλα με υφασμάτινο κάθισμα",
            },
        ],
        "gallery": [
            {
                "image": "assets/rounded-cabinet.jpg",
                "title": "Καμπύλο έπιπλο με ιδιαίτερο φινίρισμα",
                "alt": "Καμπύλο ξύλινο έπιπλο με μαύρες πόρτες και ζεστό φινίρισμα",
            },
            {
                "image": "assets/carved-sideboard.jpg",
                "title": "Σκαλιστή πρόσοψη και custom αποθηκευτικός χώρος",
                "alt": "Ξύλινο έπιπλο με σκαλιστή πρόσοψη και μεταλλικό πλαίσιο",
            },
            {
                "image": "assets/custom-bike.jpg",
                "title": "Ειδική ξύλινη κατασκευή για ποδήλατο",
                "alt": "Custom ξύλινη κατασκευή πάνω σε ποδήλατο",
            },
            {
                "image": "assets/chair-finished.jpg",
                "title": "Επισκευή και ανανέωση καρέκλας",
                "alt": "Καρέκλα με ξύλινο σκελετό και υφασμάτινο κάθισμα",
            },
            {
                "image": "assets/chair-detail.jpg",
                "title": "Λεπτομέρεια σε καμπύλο σκελετό",
                "alt": "Λεπτομέρεια ξύλινου καμπύλου σκελετού καρέκλας",
            },
            {
                "image": "assets/classic-table.jpg",
                "title": "Κλασική ξύλινη τραπεζαρία",
                "alt": "Κλασικό ξύλινο τραπέζι με καρέκλα",
            },
            {
                "image": "assets/modern-kitchen.jpg",
                "title": "Εντοιχισμένη κουζίνα",
                "alt": "Μοντέρνα εντοιχισμένη κουζίνα",
            },
            {
                "image": "assets/marble-kitchen.jpg",
                "title": "Ανακαίνιση κουζίνας",
                "alt": "Ανακαινισμένη λευκή κουζίνα",
            },
            {
                "image": "assets/wardrobe-built-in.jpg",
                "title": "Εγκατάσταση ντουλάπας",
                "alt": "Εντοιχισμένη ντουλάπα σε υπνοδωμάτιο",
            },
            {
                "image": "assets/kids-bunk-bed.jpg",
                "title": "Ξύλινο παιδικό κρεβάτι",
                "alt": "Ξύλινο παιδικό κρεβάτι κουκέτα",
            },
            {
                "image": "assets/study-desk.jpg",
                "title": "Ξύλινο γραφείο",
                "alt": "Ξύλινο γραφείο με καρέκλα",
            },
            {
                "image": "assets/wood-cart.jpg",
                "title": "Ειδική ξύλινη κατασκευή",
                "alt": "Ειδική ξύλινη κατασκευή με ρόδες",
            },
        ],
    }

    variants = generate_site_variants(intake)
    cards: list[str] = []
    for route, html in variants.items():
        if "{{" in html or "}}" in html:
            print(f"Smoke failed for {route}: unresolved placeholders remain", file=sys.stderr)
            return 1
        filename = f"{route}.html"
        (output_dir / filename).write_text(html, encoding="utf-8")
        route_copy = KOUTRAKIS_ROUTE_COPY.get(
            route,
            {"label": theme_label(route), "description": theme_description(route)},
        )
        cards.append(
            f'<a class="card card-{route}" href="{CLIENT_SLUG}/{filename}">'
            f'<span>{html_module.escape(route_copy["label"])}</span>'
            f'<p>{html_module.escape(route_copy["description"])}</p>'
            f'<strong>Δες το site</strong></a>'
        )

    gallery = f"""<!DOCTYPE html>
<html lang="el">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Κώστας Κουτράκης — Vitrina previews</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: #11151d; color: #fff; }}
    main {{ width: min(1040px, calc(100% - 32px)); margin: 0 auto; padding: 70px 0; }}
    .eyebrow {{ color: #ff7a1a; font-weight: 900; text-transform: uppercase; letter-spacing: .14em; font-size: .82rem; }}
    h1 {{ font-size: clamp(2.5rem, 8vw, 5rem); line-height: .95; margin: 14px 0 16px; }}
    p {{ color: rgba(255,255,255,.72); font-size: 1.08rem; max-width: 720px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 34px; }}
    .card {{ min-height: 250px; border: 1px solid rgba(255,255,255,.14); border-radius: 8px; padding: 22px; color: #fff; text-decoration: none; display: flex; flex-direction: column; justify-content: space-between; background: rgba(255,255,255,.07); transition: transform .18s ease, background .18s ease; }}
    .card-premium {{ background: linear-gradient(145deg, rgba(255,122,26,.22), rgba(255,255,255,.06)); }}
    .card-trust {{ background: linear-gradient(145deg, rgba(38,162,105,.22), rgba(255,255,255,.06)); }}
    .card-editorial {{ background: linear-gradient(145deg, rgba(197,145,93,.24), rgba(255,255,255,.06)); }}
    .card:hover {{ transform: translateY(-3px); background-color: rgba(255,255,255,.12); }}
    .card span {{ text-transform: uppercase; letter-spacing: .14em; font-weight: 900; color: #ff7a1a; }}
    .card p {{ margin: 18px 0 28px; font-size: .98rem; color: rgba(255,255,255,.72); }}
    .card strong {{ font-size: 1.35rem; }}
    .todo {{ margin-top: 34px; border: 1px solid rgba(255,255,255,.12); border-radius: 8px; padding: 18px; background: rgba(255,255,255,.06); }}
    .todo strong {{ display: block; margin-bottom: 8px; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">Πρώτος πραγματικός πελάτης demo</div>
    <h1>Κώστας Κουτράκης</h1>
    <p>Τρία Vitrina theme routes εμπνευσμένα από τη λογική prebuilt websites: contractor, call-first μάστορας και interior portfolio. Το περιεχόμενο είναι ίδιο, αλλά αλλάζουν ύφος, χρώματα, γραμματοσειρά και ένταση πώλησης.</p>
    <div class="grid">
      {"".join(cards)}
    </div>
    <div class="todo">
      <strong>Λείπουν πριν το publish</strong>
      Τηλέφωνο, πόλη/περιοχή, 5-10 φωτογραφίες δουλειών, domain επιλογή, και μετά Facebook/Instagram όταν είναι έτοιμος.
    </div>
  </main>
</body>
</html>
"""
    gallery_path = ROOT / "web" / "clients" / f"{CLIENT_SLUG}.html"
    gallery_path.write_text(gallery, encoding="utf-8")
    print(f"Generated {len(variants)} previews: {gallery_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
