#!/usr/bin/env python3
"""
CLI για τον DeepSeekResearchWorker (src/research_worker.py).

    python scripts/research.py --dry-run
        Ελέγχει κλειδί/.gitignore/διαθέσιμα μοντέλα χωρίς να ξοδέψει tokens.

    python scripts/research.py --preset 500-agents
        Ξανατρέχει το αρχικό agent-discovery task πάνω στο
        https://github.com/ashishpatel26/500-AI-Agents-Projects
        (ίδιο αποτέλεσμα με το πρώτο one-off script, τώρα μέσα από τον
        γενικό worker — γράφει σε research/agent-discovery/).

    python scripts/research.py \\
        --task-id theme-discovery-dentist \\
        --objective "Find dentist website references worth studying" \\
        --context "Vitrina builds Greek SMB sites, see docs/18-VERTICAL-DESIGN-INTELLIGENCE.md" \\
        --sources https://example.com/ref1 https://example.com/ref2

Τίποτα εδώ δεν τυπώνει το DEEPSEEK_API_KEY. Η έξοδος γράφεται αποκλειστικά
κάτω από research/<task-id>/ — ποτέ πάνω από production κώδικα ή themes.

Πότε να χρησιμοποιηθεί (βλ. και CLAUDE.md): μεγάλες read-only εργασίες
ανακάλυψης/ταξινόμησης/σύγκρισης — GitHub repos, theme references, ανταγωνιστές,
αρχιτεκτονικά patterns. ΟΧΙ για αλλαγές σε production κώδικα, migrations,
security review ή οτιδήποτε χρειάζεται βαθύ Vitrina context· αυτά μένουν στο Claude.
"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.research_worker import DeepSeekResearchWorker, ResearchWorkerError  # noqa: E402

VITRINA_CONTEXT = """
Vitrina is an autonomous AI digital agency for small businesses (Greek SMB market).
Capabilities of interest: website/theme generation, marketing strategy, social media
generation & scheduling, SEO, local business presence, lead generation & scoring, CRM,
email automation, customer support, reviews/reputation, analytics, advertising,
QA/testing, security, PII protection, agent memory, agent orchestration, workflow
engines, human approval, guardrails, observability, retry/recovery, scheduling,
multi-agent coordination.
""".strip()


def run_500_agents_preset(run_id: str | None = None, max_pass2: int = 15) -> dict:
    """Ξανατρέχει το agent-discovery task μέσα από τον γενικό worker.

    ΔΕΝ γράφει πάνω στο αρχικό `research/agent-discovery/` (εκείνο είναι το
    first-pass, χειρωνακτικά τεκμηριωμένο αποτέλεσμα — historical, κρατιέται
    ως έχει). Κάθε live τρέξιμο πάει σε δικό του versioned subdirectory:
        research/agent-discovery/runs/<run_id>-deepseek/
    ώστε να μπορεί να συγκριθεί με το `scripts/research_diff.py` πριν
    αποφασιστεί αν γίνεται το νέο canonical αποτέλεσμα.
    """
    from datetime import date

    run_id = run_id or date.today().isoformat()
    worker = DeepSeekResearchWorker(
        task_id=f"agent-discovery/runs/{run_id}-deepseek",
        objective=(
            "Discover architectures, workflows, patterns and open-source implementations "
            "that could accelerate the Vitrina autonomous AI digital agency. Identify "
            "replacement opportunities for agents we're planning to build ourselves."
        ),
        context=VITRINA_CONTEXT,
        sources=["https://raw.githubusercontent.com/ashishpatel26/500-AI-Agents-Projects/main/README.md"],
        output_schema={
            "name": "str", "github_url": "str", "purpose": "str", "framework": "str",
            "why_relevant": "str", "integration_difficulty": "Low|Medium|High",
            "recommended_treatment": "REUSE|ADAPT|WRAP|STUDY ONLY|REJECT",
            "priority": "High|Medium|Low",
            "license": "str (verified SPDX id or LICENSE_UNVERIFIED)",
            "license_source": "str (where the license was confirmed)",
        },
        budget={"max_pass2_candidates": max_pass2},
    )
    return worker.run()


def main() -> int:
    p = argparse.ArgumentParser(description="DeepSeek read-only research worker")
    p.add_argument("--preset", choices=["500-agents"], help="Έτοιμο task")
    p.add_argument("--run-id", help="Όνομα versioned run (default: σημερινή ημερομηνία). "
                                     "Μόνο για --preset — γράφει σε research/agent-discovery/runs/<run-id>-deepseek/")
    p.add_argument("--task-id", help="Μοναδικό όνομα φακέλου κάτω από research/")
    p.add_argument("--objective", help="Τι ψάχνουμε")
    p.add_argument("--context", default=VITRINA_CONTEXT, help="Context για DeepSeek (default: Vitrina context)")
    p.add_argument("--sources", nargs="*", default=[], help="URLs ή raw κείμενο πηγών")
    p.add_argument("--max-pass2", type=int, default=None,
                    help="Πλαφόν βαθιάς ανάλυσης (Pass 2). Default: 15 για --preset, 12 για custom task. "
                         "Ό,τι HIGH/MEDIUM ξεπερνά το πλαφόν πάει σε shortlist_pending.json, όχι στο κενό.")
    p.add_argument("--dry-run", action="store_true", help="Μόνο έλεγχος config/μοντέλων, καμία κλήση έρευνας")
    args = p.parse_args()

    if args.dry_run:
        # Ελαφρύ instantiation μόνο για να τρέξουν οι safety checks + model check.
        probe = DeepSeekResearchWorker(
            task_id="dry-run-probe", objective="probe", context="probe", sources=[],
        )
        try:
            probe._safety_checks()  # noqa: SLF001 — εσκεμμένο dry-run probe
        except ResearchWorkerError as exc:
            print(f"❌ {exc}")
            return 1
        info = probe.check_models()
        print("✅ Κλειδί βρέθηκε, .env σωστά αγνοημένο από git.")
        print(f"   Μοντέλα σε χρήση: {info['using']}")
        if info.get("warning"):
            print(f"   ⚠ {info['warning']}")
        if info.get("available"):
            print(f"   Διαθέσιμα από API: {', '.join(info['available'][:10])}")
        return 0

    if args.preset == "500-agents":
        result = run_500_agents_preset(run_id=args.run_id, max_pass2=args.max_pass2 or 15)
    else:
        if not args.task_id or not args.objective or not args.sources:
            p.error("χρειάζονται --task-id, --objective και --sources (ή χρησιμοποίησε --preset / --dry-run)")
        worker = DeepSeekResearchWorker(
            task_id=args.task_id,
            objective=args.objective,
            context=args.context,
            sources=args.sources,
            budget={"max_pass2_candidates": args.max_pass2 or 12},
        )
        result = worker.run()

    print(f"\n✅ research/{result['task_id']}/  —  {result['findings_count']} findings, "
          f"{result['rejected_count']} rejected, {result.get('pending_count', 0)} pending (over budget)")
    if result.get("pending_count"):
        print(f"   ⚠ {result['pending_count']} HIGH/MEDIUM candidate(s) not deep-analysed — "
              "see shortlist_pending.json, or rerun with a higher --max-pass2.")
    t = result["telemetry"]
    print(f"   tokens in={t['input_tokens']:,} out={t['output_tokens']:,}  "
          f"~${t['estimated_cost_usd']} USD  {t.get('duration_seconds')}s")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ResearchWorkerError as exc:
        print(f"❌ {exc}")
        raise SystemExit(1)
