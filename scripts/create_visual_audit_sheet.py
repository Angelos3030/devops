#!/usr/bin/env python3
"""Create manageable PNG contact sheets from full-page audit screenshots."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research" / "visual-theme-audit"


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else "before"
    payload = json.loads((AUDIT / phase / "measurements.json").read_text(encoding="utf-8"))
    out = AUDIT / phase / "contact-sheets"
    out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=18)
    rows_per_sheet, card_w, card_h = 6, 1400, 520
    for page_no in range(math.ceil(len(payload["themes"]) / rows_per_sheet)):
        themes = payload["themes"][page_no * rows_per_sheet:(page_no + 1) * rows_per_sheet]
        sheet = Image.new("RGB", (card_w, card_h * len(themes)), "#111318")
        draw = ImageDraw.Draw(sheet)
        for row, theme in enumerate(themes):
            y = row * card_h
            draw.text((20, y + 18), f"{theme['id']}  |  {theme['vertical']} / {theme['biz']}", fill="white", font=font)
            for col, label in enumerate(("desktop", "mobile")):
                image_path = ROOT / theme["viewports"][label]["screenshot"]
                with Image.open(image_path) as src:
                    src.thumbnail((920 if col == 0 else 380, 440))
                    x = 20 if col == 0 else 1000
                    sheet.paste(src.convert("RGB"), (x, y + 58))
            flags = []
            for label in ("desktop", "mobile"):
                data = theme["viewports"][label]
                if data.get("suspicious"): flags.append(label)
                if data.get("horizontalOverflow", 0) > 2: flags.append(f"{label}:overflow")
                if any(not img.get("naturalWidth") for img in data.get("images", [])): flags.append(f"{label}:broken-image")
            draw.text((1000, y + 18), "flags: " + (", ".join(flags) or "none"), fill="#ffb36b" if flags else "#7ee2a8", font=font)
        sheet.save(out / f"sheet-{page_no + 1:02}.jpg", quality=88)
    combined_count = page_no + 1

    available_viewports = {name for theme in payload["themes"] for name in theme["viewports"]}
    for label, thumb_width in (("desktop", 1180), ("mobile", 420), ("narrow", 350)):
        if label not in available_viewports:
            continue
        label_out = AUDIT / phase / f"{label}-contact-sheets"
        label_out.mkdir(parents=True, exist_ok=True)
        per_sheet = 10 if label == "desktop" else 12
        row_h = 600 if label == "desktop" else 520
        sheet_w = 1280 if label == "desktop" else 720
        for page_no in range(math.ceil(len(payload["themes"]) / per_sheet)):
            themes = payload["themes"][page_no * per_sheet:(page_no + 1) * per_sheet]
            sheet = Image.new("RGB", (sheet_w, row_h * len(themes)), "#111318")
            draw = ImageDraw.Draw(sheet)
            for row, theme in enumerate(themes):
                y = row * row_h
                data = theme["viewports"][label]
                status = "WARN" if data.get("suspicious") else "OK"
                draw.text((20, y + 16), f"{theme['id']} | {theme['vertical']} | {status}", fill="white", font=font)
                with Image.open(ROOT / data["screenshot"]) as src:
                    src.thumbnail((thumb_width, row_h - 60))
                    sheet.paste(src.convert("RGB"), (20, y + 52))
            sheet.save(label_out / f"sheet-{page_no + 1:02}.jpg", quality=90)
    print(f"created {combined_count} combined contact sheets plus desktop/mobile sets in {out.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
