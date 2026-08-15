#!/usr/bin/env python3
"""CLI για τον port worker.

    python scripts/port_worker.py --source-id frost-bakery
    python scripts/port_worker.py --next
    python scripts/port_worker.py --status

ΔΕΝ υπάρχει --all και δεν υπάρχει βρόχος. Το bulk mode ενεργοποιείται μόνο
μετά από ρητή έγκριση, αφού ένα πραγματικό port περάσει από validator.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from src.port_worker import PortWorkerError, _load_queue, next_pending, port_source  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Port worker — ένα source τη φορά")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--source-id", help="ποιο canonical PORT_OK record")
    g.add_argument("--next", action="store_true", help="το επόμενο PENDING PORT_OK")
    g.add_argument("--status", action="store_true", help="κατάσταση ουράς")
    args = ap.parse_args()

    if args.status:
        q = _load_queue()
        for sid, rec in q["sources"].items():
            print(f"{sid:20} {rec.get('decision','?'):10} {rec.get('status','?')}")
        return 0

    sid = args.source_id or next_pending()
    if not sid:
        print("Καμία PENDING εγγραφή με decision=PORT_OK.")
        return 0

    try:
        res = port_source(sid)
    except PortWorkerError as exc:
        print(f"ΣΤΑΜΑΤΗΣΕ: {exc}")
        return 1

    print(json.dumps({k: v for k, v in res.items()
                      if k not in ("original_metrics", "deviations")},
                     indent=1, ensure_ascii=False))
    if res.get("deviations"):
        print("\nΑποκλίσεις που δήλωσε το DeepSeek:")
        for d in res["deviations"]:
            print(f"  - {d.get('what')}: {d.get('why')}")
    print(f"\nΚΑΤΑΣΤΑΣΗ: {res.get('status')}"
          + ("  → χρειάζεται οπτικό review από Claude" if res.get("status") == "READY_FOR_REVIEW" else ""))
    return 0 if res.get("status") in ("READY_FOR_REVIEW", "SKIPPED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
