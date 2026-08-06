#!/usr/bin/env python3
"""Run once; Railway Cron can invoke this every minute."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.social_engine import run_due


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    print(json.dumps(run_due(limit=args.limit, dry_run=args.dry_run), ensure_ascii=False))


if __name__ == "__main__":
    main()
