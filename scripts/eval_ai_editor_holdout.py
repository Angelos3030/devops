"""Run the frozen holdout against the configured real editing provider.

No production or staging data is read or written. Results are printed as JSON.
The script stops after one preflight failure to avoid hundreds of invalid or
billable requests when provider credentials/configuration are broken.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_editor.engine import EditingEngine
from src.ai_editor.model import DeepSeekSiteEditingModel, EditPlan
from src.ai_editor.store import InMemoryEditorStore
from tests.ai_editor_holdout_v1 import HOLDOUT_CASES, HoldoutCase


def _norm(value: Any) -> Any:
    if isinstance(value, str):
        text = value.lower().strip().replace("ευρω", "€").replace("euro", "€")
        text = re.sub(r"\s+", " ", text)
        return text
    if isinstance(value, list):
        return [_norm(item) for item in value]
    if isinstance(value, dict):
        return {key: _norm(item) for key, item in value.items()}
    return value


def _evaluate(case: HoldoutCase, plan: EditPlan | None) -> Dict[str, bool]:
    schema = plan is not None
    expected_ops = list(case.operations)
    actual_ops = list(plan.operations) if plan else []
    rejected = bool(plan is not None and not actual_ops)
    operation_accuracy = schema and [op.op for op in actual_ops] == [op.op for op in expected_ops]
    argument_accuracy = operation_accuracy and all(
        _norm(actual.params) == _norm(expected.params)
        for actual, expected in zip(actual_ops, expected_ops)
    )
    intent_accuracy = schema and plan.intent == case.intent
    unsupported_rejection = (not case.reject) or rejected
    authorization_rejection = (not case.authorization_reject) or rejected
    multi_accuracy = (len(expected_ops) <= 1) or (operation_accuracy and argument_accuracy)

    capability_ok = True
    if plan is not None and actual_ops and case.capabilities:
        store = InMemoryEditorStore()
        store.add_client(
            case.case_id,
            {"name": "Synthetic", "services": [], "palette": "original"},
            [{"id": f"p{i}", "type": "photo"} for i in range(3)],
        )
        result = EditingEngine.execute_plan(
            case.case_id, plan, store=store, capabilities=case.capabilities, persist=False
        )
        capability_ok = not result.success

    return {
        "schema_validity": schema,
        "intent_accuracy": intent_accuracy,
        "operation_accuracy": operation_accuracy,
        "argument_accuracy": argument_accuracy,
        "unsupported_rejection": unsupported_rejection,
        "authorization_rejection": authorization_rejection,
        "capability_enforcement": capability_ok,
        "multi_operation_accuracy": multi_accuracy,
    }


def main() -> int:
    provider = os.getenv("AI_EDITOR_EVAL_PROVIDER", "deepseek").strip().lower()
    if provider == "kimi":
        from dotenv import load_dotenv
        load_dotenv()
        model = DeepSeekSiteEditingModel(
            base_url="https://api.moonshot.ai/v1",
            api_key=os.getenv("KIMI_API_KEY"),
            model_name=os.getenv("KIMI_MODEL") or "kimi-k3",
            temperature=1.0,
            provider_name="kimi",
            tool_choice="auto",
        )
    else:
        model = DeepSeekSiteEditingModel()
    preflight_case = HOLDOUT_CASES[0]
    preflight = model.plan_edit(preflight_case.context, preflight_case.message)
    if preflight is None:
        print(json.dumps({
            "status": "BLOCKED_PROVIDER_UNAVAILABLE",
            "provider": provider,
            "holdout_queries": len(HOLDOUT_CASES),
            "scores": None,
            "reason": "Provider preflight did not return a valid structured EditPlan.",
        }, ensure_ascii=False, indent=2))
        return 2

    rows = [(preflight_case, preflight)]
    remaining = HOLDOUT_CASES[1:]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(model.plan_edit, case.context, case.message): case
            for case in remaining
        }
        for future in as_completed(futures):
            case = futures[future]
            try:
                rows.append((case, future.result()))
            except Exception:
                rows.append((case, None))

    scored = [(case, _evaluate(case, result)) for case, result in rows]
    metrics = Counter()
    for _, result in scored:
        metrics.update({key: int(value) for key, value in result.items()})
    total = len(scored)
    failures = {
        metric: [case.case_id for case, result in scored if not result[metric]][:25]
        for metric in metrics
    }
    print(json.dumps({
        "status": "COMPLETE",
        "provider": provider,
        "holdout_queries": total,
        "scores": {key: round(100 * count / total, 2) for key, count in metrics.items()},
        "failure_examples": failures,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
