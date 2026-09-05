#!/usr/bin/env python3
"""Controlled 25-command Greek/Greeklish battery against the real staging model.

This validates provider planning only. Persistence, rollback, refresh, undo and
stale-tab behavior are covered by verify_editor_staging.py and the browser E2E.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.eval_ai_editor_holdout import _evaluate
from src.ai_editor.model import DeepSeekSiteEditingModel
from tests.ai_editor_holdout_v1 import HOLDOUT_CASES


SELECTED = (
    "phone-001", "phone-005", "phone-007",
    "hours-001", "hours-003", "hours-006",
    "followup-001", "followup-005",
    "field-001", "field-004", "field-015",
    "service-001", "service-002", "service-004",
    "palette-001", "palette-003",
    "media-001", "media-002",
    "multi-001", "multi-002", "multi-003",
    "reject-007", "reject-011", "reject-013",
    "undo-001",
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    key = os.getenv("KIMI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("KIMI_API_KEY is missing")
    model = DeepSeekSiteEditingModel(
        base_url="https://api.moonshot.ai/v1",
        api_key=key,
        model_name=os.getenv("KIMI_MODEL") or "kimi-k2.6",
        provider_name="kimi",
    )
    by_id = {case.case_id: case for case in HOLDOUT_CASES}
    base_context = {
        "business_name": "Synthetic QA Studio",
        "vertical": "salon",
        "city": "Αθήνα",
        "phone": "2100000000",
        "hours": "09:00-17:00",
        "services": [{"name": "Κούρεμα", "price": "18€"}],
        "palette": "original",
        "gallery_count": 3,
    }
    rows = []
    for case_id in SELECTED:
        case = by_id[case_id]
        plan = model.plan_edit({**base_context, **case.context}, case.message)
        scores = _evaluate(case, plan)
        rows.append((case, plan, scores))
        verdict = "PASS" if all(scores.values()) else "FAIL"
        print(f"  {verdict:4}  {case.case_id:12} {case.message[:72]}")

    totals = Counter()
    for _, _, scores in rows:
        totals.update({name: int(value) for name, value in scores.items()})
    report = {
        "provider": "kimi",
        "model": model.model_name,
        "commands": len(rows),
        "scores": {
            name: round(100 * passed / len(rows), 2)
            for name, passed in totals.items()
        },
        "failures": [
            {
                "id": case.case_id,
                "message": case.message,
                "failed_metrics": [name for name, ok in scores.items() if not ok],
                "actual": plan.model_dump() if plan else None,
            }
            for case, plan, scores in rows if not all(scores.values())
        ],
    }
    print("\n" + json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
