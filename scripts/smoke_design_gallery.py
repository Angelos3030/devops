from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.local_site_generator import generate_site_variants  # noqa: E402


def main() -> int:
    sample_intake = {
        "name": "Ταβέρνα Η Γωνιά",
        "type": "Ταβέρνα/Εστιατόριο",
        "city": "Θεσσαλονίκη",
        "address": "Τσιμισκή 10, Θεσσαλονίκη",
        "phone": "2310000000",
        "style": "Παραδοσιακές γεύσεις με φιλική ατμόσφαιρα",
    }

    output_dir = ROOT / "web" / "previews"
    output_dir.mkdir(parents=True, exist_ok=True)

    variants = generate_site_variants(sample_intake)
    links: list[str] = []
    for route, html in variants.items():
        if "{{" in html or "}}" in html:
            print(f"Smoke failed for {route}: unresolved placeholders remain", file=sys.stderr)
            return 1
        filename = f"taverna-{route}.html"
        (output_dir / filename).write_text(html, encoding="utf-8")
        links.append(f'<a class="card" href="previews/{filename}"><span>{route}</span><strong>Άνοιγμα preview</strong></a>')

    chooser = f"""<!DOCTYPE html>
<html lang="el">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vitrina Preview Gallery</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: #101612; color: #fff; }}
    main {{ width: min(1040px, calc(100% - 32px)); margin: 0 auto; padding: 70px 0; }}
    h1 {{ font-size: clamp(2.5rem, 8vw, 5rem); line-height: .95; margin: 0 0 16px; }}
    p {{ color: rgba(255,255,255,.72); font-size: 1.1rem; max-width: 650px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 34px; }}
    .card {{ min-height: 210px; border: 1px solid rgba(255,255,255,.14); border-radius: 8px; padding: 22px; color: #fff; text-decoration: none; display: flex; flex-direction: column; justify-content: space-between; background: rgba(255,255,255,.07); }}
    .card:hover {{ background: rgba(255,255,255,.12); }}
    .card span {{ text-transform: uppercase; letter-spacing: .14em; font-weight: 800; color: #e86f2a; }}
    .card strong {{ font-size: 1.35rem; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <h1>Vitrina style chooser</h1>
    <p>Τρία άμεσα previews από το ίδιο intake. Αυτό είναι το πρώτο βήμα για Lovable-like επιλογή ύφους πριν το publish.</p>
    <div class="grid">
      {"".join(links)}
    </div>
  </main>
</body>
</html>
"""
    (ROOT / "web" / "preview-gallery.html").write_text(chooser, encoding="utf-8")
    print(f"Smoke OK: wrote {len(variants)} previews and web/preview-gallery.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
