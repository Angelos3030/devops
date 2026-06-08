"""
Φτιάχνει το App Icon της Vitrina (storefront) σε PNG.

  pip install pillow
  python -m src.make_icon

Βγάζει στο web/:
  - icon-1024.png   → App Icon για Meta App Dashboard (1024x1024)
  - favicon-180.png → apple-touch-icon
  - favicon-32.png  → favicon
"""

import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "web")

# Χρώματα brand
WHITE   = (255, 255, 255, 255)
BG      = (255, 247, 240, 255)   # απαλό warm-white φόντο
INK     = (10, 10, 11, 255)      # κτίριο
ORANGE  = (255, 122, 26, 255)    # τέντα
ORANGE2 = (255, 178, 122, 255)   # scallops (ανοιχτό)


def _draw(size: int) -> Image.Image:
    # Σχεδιάζουμε σε μεγάλη ανάλυση και κάνουμε downscale (anti-alias).
    S = 1024
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Φόντο: γεμάτο τετράγωνο με στρογγυλεμένες γωνίες (η Meta δεν θέλει διαφάνεια).
    d.rounded_rectangle([0, 0, S, S], radius=int(S * 0.22), fill=BG)

    # Mapping του art (viewBox 0..32) σε κεντραρισμένο κουτί.
    scale = 22.0
    art_w = 32 * scale
    ox = (S - art_w) / 2
    oy = (S - art_w) / 2 + S * 0.02

    def P(x, y):
        return (ox + x * scale, oy + y * scale)

    # Κτίριο (σκούρο, στρογγυλεμένο)
    d.rounded_rectangle([P(6, 14), P(26, 28)], radius=int(2 * scale), fill=INK)

    # Τέντα (πορτοκαλί τραπέζιο)
    d.polygon([P(3, 14), P(6, 7), P(26, 7), P(29, 7 + 7)], fill=ORANGE)
    d.polygon([P(3, 14), P(6, 7), P(26, 7), P(29, 14)], fill=ORANGE)

    # Scallops στο κάτω χείλος της τέντας (6 μισοφέγγαρα, ανοιχτό πορτοκαλί)
    n = 6
    x0, x1 = 3, 29
    seg = (x1 - x0) / n
    r = seg / 2
    for i in range(n):
        cx = x0 + seg * i + r
        bbox = [P(cx - r, 14 - r), P(cx + r, 14 + r)]
        d.pieslice(bbox, start=0, end=180, fill=ORANGE2)

    # Πόρτα (λευκή, στρογγυλεμένη)
    d.rounded_rectangle([P(13, 20), P(19, 28)], radius=int(1 * scale), fill=WHITE)

    if size != S:
        img = img.resize((size, size), Image.LANCZOS)
    return img


def main() -> None:
    targets = [("icon-1024.png", 1024), ("favicon-180.png", 180), ("favicon-32.png", 32)]
    for name, size in targets:
        path = os.path.join(OUT, name)
        # Για το app icon: flatten σε αδιαφανές (Meta δεν δέχεται alpha).
        icon = _draw(size)
        if name == "icon-1024.png":
            flat = Image.new("RGB", icon.size, (255, 255, 255))
            flat.paste(icon, mask=icon.split()[3])
            flat.save(path, "PNG")
        else:
            icon.save(path, "PNG")
        print(f"  ✅ {name} ({size}x{size})")
    print("\n📁 Όλα στο web/. Ανέβασε το icon-1024.png στο Meta App → Settings → Basic.")


if __name__ == "__main__":
    main()
