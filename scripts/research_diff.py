#!/usr/bin/env python3
"""
Συγκρίνει δύο research runs στο ίδιο θέμα — π.χ. το πρώτο χειρωνακτικό pass
έναντι ενός πραγματικού DeepSeek run — και παράγει σύντομο delta report.

    python scripts/research_diff.py \\
        --old research/agent-discovery \\
        --new research/agent-discovery/runs/2026-08-12-deepseek

Γράφει ΜΟΝΟ `delta_report.md` μέσα στον φάκελο --new. Ο φάκελος --old
(historical, first-pass αποτέλεσμα) δεν πειράζεται ποτέ. Το report δεν
αποφασίζει ποιο γίνεται canonical — αυτό μένει ανθρώπινη απόφαση μετά την
ανάγνωσή του.

Καλύπτει διαφορετικά schemas: το πρώτο πέρασμα ήταν χειρωνακτικό
(`shortlist.json` με key "shortlist", πεδίο "treatment"), το DeepSeek run
βγαίνει από τον γενικό worker (`findings.json` με key "findings", πεδίο
"recommended_treatment"). Το script δοκιμάζει και τα δύο.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_list(path: Path, *keys: str) -> list[dict]:
    """Φορτώνει λίστα από JSON, δοκιμάζοντας διαδοχικά keys (schema-agnostic)."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return data
    for k in keys:
        if isinstance(data.get(k), list):
            return data[k]
    return []


def _name(entry: dict) -> str:
    return str(entry.get("name") or entry.get("project") or "?").strip()


def _normalize(name: str) -> str:
    """Χαλαρή μορφή ονόματος για matching πέρα από exact string equality.

    Χωρίς αυτό, "PII Sanitization Agent (TrustBoost)" (πρώτο πέρασμα, χειρωνακτικό)
    έναντι "PII Sanitization Agent" (DeepSeek run, χωρίς parenthetical) βγαίνουν σαν
    δύο ΔΙΑΦΟΡΕΤΙΚΑ projects — false "added" + false "removed" ταυτόχρονα για το ΙΔΙΟ
    project. Αφαιρούμε ό,τι είναι σε παρένθεση, πεζά, χωρίς σημεία στίξης/κενά.
    """
    import re

    n = re.sub(r"\([^)]*\)", "", name).lower()
    n = re.sub(r"[^a-z0-9]+", "", n)
    return n


def _match_by_normalized_name(old_by_name: dict, new_by_name: dict) -> tuple[list, list, list]:
    """Επιστρέφει (added, removed, common) χρησιμοποιώντας normalized name matching
    αντί για exact string equality. "common" περιέχει (old_name, new_name) ζεύγη.
    """
    old_norm = {_normalize(n): n for n in old_by_name}
    new_norm = {_normalize(n): n for n in new_by_name}

    common_norm = set(old_norm) & set(new_norm)
    added_norm = set(new_norm) - set(old_norm)
    removed_norm = set(old_norm) - set(new_norm)

    common = sorted((old_norm[n], new_norm[n]) for n in common_norm)
    added = sorted(new_norm[n] for n in added_norm)
    removed = sorted(old_norm[n] for n in removed_norm)
    return added, removed, common


def _treatment(entry: dict) -> str:
    return entry.get("recommended_treatment") or entry.get("treatment") or "?"


def _priority(entry: dict) -> str:
    return entry.get("priority") or "?"


def _license(entry: dict) -> str:
    return entry.get("license") or "?"


def build_delta(old_dir: Path, new_dir: Path) -> str:
    old_findings = _load_list(old_dir / "shortlist.json", "shortlist", "findings")
    new_findings = _load_list(new_dir / "findings.json", "findings", "shortlist")
    old_rejected = _load_list(old_dir / "rejected.json", "rejected")
    new_rejected = _load_list(new_dir / "rejected.json", "rejected")
    new_pending = _load_list(new_dir / "shortlist_pending.json", "pending")

    old_by_name = {_name(e): e for e in old_findings}
    new_by_name = {_name(e): e for e in new_findings}
    pending_norm = {_normalize(_name(e)) for e in new_pending}

    added, removed, common_pairs = _match_by_normalized_name(old_by_name, new_by_name)
    # "removed" που στην πραγματικότητα είναι pass1-only λόγω budget cap δεν είναι το
    # ίδιο σήμα με "DeepSeek το έκρινε άσχετο" — ξεχώρισέ το.
    removed_over_budget = [n for n in removed if _normalize(n) in pending_norm]
    removed_dropped = [n for n in removed if _normalize(n) not in pending_norm]

    treatment_changes, license_changes, priority_changes = [], [], []
    for old_name, new_name in common_pairs:
        o, n = old_by_name[old_name], new_by_name[new_name]
        label = old_name if old_name == new_name else f"{old_name} / {new_name}"
        if _treatment(o) != _treatment(n):
            treatment_changes.append((label, _treatment(o), _treatment(n)))
        if _license(o) != _license(n):
            license_changes.append((label, _license(o), _license(n)))
        if _priority(o) != _priority(n):
            priority_changes.append((label, _priority(o), _priority(n)))

    meta_path = new_dir / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    def _section(title: str, rows: list[str]) -> list[str]:
        return ["", f"## {title}", ""] + (rows or ["_none_"])

    lines = [
        f"# Delta Report",
        "",
        f"**Old:** `{old_dir}` (first pass, manual) — {len(old_findings)} findings, {len(old_rejected)} rejected",
        f"**New:** `{new_dir}` (DeepSeek run) — {len(new_findings)} findings, {len(new_rejected)} rejected, "
        f"{len(new_pending)} pending (HIGH/MEDIUM but over the Pass 2 budget cap — not a rejection)",
        "",
        "_Matching uses normalized names (parentheticals/punctuation stripped) so e.g. "
        '"PII Sanitization Agent (TrustBoost)" and "PII Sanitization Agent" count as the same project._',
    ]
    lines += _section("Projects added (DeepSeek found, first pass missed)", [f"- {n}" for n in added])
    lines += _section(
        "Projects removed — DeepSeek actively dropped (LOW/REJECT this run)",
        [f"- {n}" for n in removed_dropped],
    )
    lines += _section(
        "Projects removed — NOT dropped, just over Pass 2 budget this run (see shortlist_pending.json)",
        [f"- {n}" for n in removed_over_budget],
    )
    lines += _section(
        "Recommendation (treatment) changes",
        [f"- **{n}**: `{o}` → `{v}`" for n, o, v in treatment_changes],
    )
    lines += _section(
        "Priority changes",
        [f"- **{n}**: `{o}` → `{v}`" for n, o, v in priority_changes],
    )
    lines += _section(
        "License verification differences",
        [f"- **{n}**: `{o}` → `{v}`" for n, o, v in license_changes],
    )
    lines += _section(
        "DeepSeek token/cost usage (this run)",
        [
            f"- Models: Pass 1 = {meta.get('pass1_model', '?')} | Pass 2 = {meta.get('pass2_model', '?')}",
            f"- Tokens: in={meta.get('input_tokens', 0):,} out={meta.get('output_tokens', 0):,} "
            f"total={meta.get('total_tokens', 0):,}",
            f"- Estimated cost: ~${meta.get('estimated_cost_usd', 0)} USD",
            f"- Duration: {meta.get('duration_seconds', '?')}s",
            f"- Sources analyzed: {meta.get('sources_analyzed', '?')}  |  "
            f"Pass 1 candidates: {meta.get('pass1_candidates', '?')}  |  "
            f"Pass 2 deep-analysed: {meta.get('pass2_candidates', '?')}",
        ],
    )
    lines += _section(
        "Claude work avoided (estimate)",
        [
            f"- DeepSeek classified {meta.get('pass1_candidates', '?')} candidates from "
            f"{meta.get('sources_analyzed', '?')} source(s) and deep-analysed "
            f"{meta.get('pass2_candidates', '?')} of them — comparable volume of README "
            "reading + comparison that the first pass had Claude do directly.",
            "- Zero Claude tokens were spent on this run's classification/analysis passes; "
            "Claude's role here is limited to running this diff and reviewing the result.",
        ],
    )
    lines += _section(
        "Recommendation",
        [
            "This report does NOT auto-promote the DeepSeek run to canonical. Review the "
            "sections above, then decide by hand whether these artifacts should replace "
            f"`{old_dir}/shortlist.json` etc., or whether a follow-up pass is needed.",
        ],
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Compare two research runs and write a delta report")
    p.add_argument("--old", required=True, help="Παλιός φάκελος (π.χ. research/agent-discovery)")
    p.add_argument("--new", required=True, help="Νέος φάκελος (π.χ. research/agent-discovery/runs/2026-08-12-deepseek)")
    args = p.parse_args()

    old_dir, new_dir = Path(args.old), Path(args.new)
    if not old_dir.exists():
        p.error(f"δεν υπάρχει: {old_dir}")
    if not new_dir.exists():
        p.error(f"δεν υπάρχει: {new_dir}")

    report = build_delta(old_dir, new_dir)
    out_path = new_dir / "delta_report.md"
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n✅ Γράφτηκε: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
