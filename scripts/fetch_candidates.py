"""Κατέβασμα + αποσυμπίεση των επιλεγμένων υποψηφίων και εντοπισμός entry point.

Τα download URL ΠΑΡΑΓΟΝΤΑΙ από το επαληθευμένο URL σελίδας, δεν μαντεύονται:
  templatemo  /tm-417-grill        -> /download/templatemo_417_grill
  tooplate    /view/2168-sweet-... -> /zip-templates/2168_sweet_....zip
Κάθε αποτυχία τυπώνεται· τίποτα δεν παραλείπεται σιωπηλά.
"""
from __future__ import annotations

import io
import json
import pathlib
import re
import sys
import zipfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
DEST = pathlib.Path("sites/artifacts/cand-src")


def download_url(row: dict) -> str | None:
    slug = row["slug"]
    if row["studio"] == "templatemo":
        m = re.match(r"tm-(\d+)-(.+)", slug)
        return f"https://templatemo.com/download/templatemo_{m.group(1)}_{m.group(2).replace('-', '_')}" if m else None
    m = re.match(r"(\d+)-(.+)", slug)
    return f"https://www.tooplate.com/zip-templates/{m.group(1)}_{m.group(2).replace('-', '_')}.zip" if m else None


def grab(row: dict) -> tuple[str, str]:
    name = re.sub(r"[^a-z0-9]+", "_", row["name"].lower()).strip("_")
    url = download_url(row)
    if not url:
        return name, "ΧΩΡΙΣ URL"
    out = DEST / name
    if out.exists() and any(out.rglob("index.html")):
        return name, "ήδη υπάρχει"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            blob = r.read()
        zipfile.ZipFile(io.BytesIO(blob)).extractall(out)
    except Exception as e:
        return name, f"ΑΠΟΤΥΧΙΑ {type(e).__name__}"
    return name, f"{len(blob) // 1024}KB"


def main() -> None:
    rows = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    DEST.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(grab, rows))
    for name, status in results:
        print(f"  {name:24} {status}")

    mapping: dict[str, str] = {}
    for row, (name, status) in zip(rows, results):
        idx = [p for p in (DEST / name).rglob("index.html") if "node_modules" not in str(p)]
        if idx:
            best = min(idx, key=lambda p: len(p.parts))
            mapping[name] = str(best.relative_to(DEST)).replace("\\", "/")
        else:
            print(f"  ! {name}: χωρίς index.html ({status})")
    (DEST / "map.json").write_text(json.dumps(mapping, indent=1), encoding="utf-8")
    meta = {re.sub(r"[^a-z0-9]+", "_", r["name"].lower()).strip("_"): r for r in rows}
    (DEST / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nέτοιμα για απόδοση: {len(mapping)}/{len(rows)}")


if __name__ == "__main__":
    main()
