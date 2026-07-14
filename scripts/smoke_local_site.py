from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.local_site_generator import generate_site  # noqa: E402


def main() -> int:
    sample_intake = {
        "name": "Ταβέρνα Η Γωνιά",
        "type": "Ταβέρνα/Εστιατόριο",
        "city": "Θεσσαλονίκη",
        "address": "Τσιμισκή 10, Θεσσαλονίκη",
        "phone": "2310000000",
        "style": "Παραδοσιακές γεύσεις με φιλική ατμόσφαιρα",
    }

    html = generate_site(sample_intake)
    output_path = ROOT / "web" / "local-test-taverna.html"
    output_path.write_text(html, encoding="utf-8")

    if "{{" in html or "}}" in html:
        print("Smoke failed: unresolved placeholders remain", file=sys.stderr)
        return 1

    print(f"Smoke OK: wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
