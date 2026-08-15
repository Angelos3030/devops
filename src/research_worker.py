"""
Γενικός read-only research worker για μαζική εξερεύνηση/ταξινόμηση μέσω DeepSeek.

Γιατί υπάρχει: μεγάλες εργασίες ανακάλυψης (GitHub repos, theme references,
ανταγωνιστές, αρχιτεκτονικά patterns) σπαταλάνε πολλά Claude tokens αν τις κάνει
ένα-ένα το ίδιο το Claude. Το DeepSeek είναι φθηνό και αρκετά καλό για ευρεία
ταξινόμηση εκατοντάδων υποψηφίων· το Claude κρατάει την υλοποίηση, τις αποφάσεις
αρχιτεκτονικής, το security review και την τελική επικύρωση.

Ξεχωριστό από το src/ai.py: εκείνο είναι το PRODUCTION κανάλι AI για κείμενα
πελατών (AI_API_KEY/AI_BASE_URL — μπορεί να δείχνει σε Anthropic ή DeepSeek).
Αυτό εδώ διαβάζει ΑΠΟΚΛΕΙΣΤΙΚΑ το δικό του DEEPSEEK_API_KEY και δεν μοιράζεται
ποτέ credentials, quota ή endpoint με το production κανάλι. Ένα research task
που τρέχει ασταμάτητα δεν πρέπει ποτέ να μπορεί να επηρεάσει το site generation.

Δύο περάσματα (βλ. DEFAULT DELEGATION POLICY στο project):
  Pass 1 (φθηνό μοντέλο)   — ευρεία ταξινόμηση HIGH/MEDIUM/LOW/REJECT.
  Pass 2 (ισχυρότερο μοντέλο) — βαθιά ανάλυση ΜΟΝΟ στη shortlist του Pass 1.
Έτσι δεν ξοδεύονται ακριβά reasoning tokens σε εκατοντάδες υποψήφιους που θα
απορριφθούν ούτως ή άλλως.

Έξοδος: πάντα δομημένη, ΠΟΤΕ ελεύθερο conversational κείμενο ως το μόνο αρχείο.
    research/<task_id>/
        findings.json    — αποδεκτοί υποψήφιοι (HIGH/MEDIUM) με πλήρη ανάλυση
        rejected.json     — απορριφθέντες (LOW/REJECT) με λόγο
        evidence.json      — ό,τι πρωτογενές υλικό μαζεύτηκε (URLs, snippets)
        summary.md         — ανθρώπινο summary. ΑΥΤΟ διαβάζει πρώτα το Claude.
        metadata.json       — τηλεμετρία: μοντέλα, tokens, κόστος, διάρκεια.
                              ΠΟΤΕ API key εδώ.

Ασφάλεια:
  - Το κλειδί διαβάζεται μόνο από env (DEEPSEEK_API_KEY). Δεν τυπώνεται, δεν
    γράφεται σε artifact, δεν καταγράφεται σε log.
  - Αρνείται να τρέξει αν το .env δεν είναι στο .gitignore.
  - Η έξοδος γράφεται ΜΟΝΟ κάτω από research/ — ποτέ πάνω από production κώδικα,
    themes, Design System, Theme Builder ή client data.
  - Αυτός ο worker είναι read-only ως προς το Vitrina project: δεν εγγράφει ποτέ
    εκτός research/, δεν κάνει commit, δεν κάνει deploy.

Χρήση απευθείας:

    from src.research_worker import DeepSeekResearchWorker

    worker = DeepSeekResearchWorker(
        task_id="theme-discovery-dentist",
        objective="Find dentist website references worth studying for a new theme",
        context="Vitrina builds Greek SMB sites. See docs/18-VERTICAL-DESIGN-INTELLIGENCE.md",
        sources=["https://raw.githubusercontent.com/.../README.md", "..."],
        output_schema={"purpose": "str", "why_relevant": "str"},  # προαιρετικό
        budget={"max_pass2_candidates": 10},
    )
    result = worker.run()

Για CLI χρήση βλ. `scripts/research.py --help`.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RESEARCH_ROOT = ROOT / "research"
TIMEOUT = 90
MAX_SOURCE_CHARS = 40_000  # ανά πηγή, για να μη σκάει το context του Pass 1
# Το combined string (όλες οι πηγές μαζί) στο Pass 1 ΕΙΧΕ το ίδιο όριο με MAX_SOURCE_CHARS.
# Bug: όταν οι πηγές είναι λίγες αλλά μεγάλες (π.χ. πλήρεις product pages, όχι ένα listing
# page με πολλά items), η πρώτη πηγή μόνη της καταναλώνει όλο το όριο και οι υπόλοιπες
# κόβονται σιωπηλά πριν καν φτάσουν στο μοντέλο — 0 rejected, μόνο 1 finding, χωρίς σφάλμα.
# Το deepseek-chat context window χωράει άνετα πολύ περισσότερο από 40K chars, οπότε το
# combined cap μπαίνει ξεχωριστά και πιο γενναιόδωρο.
MAX_COMBINED_CHARS = 200_000  # όριο για το ΣΥΝΟΛΟ των πηγών μαζί στο Pass 1

# Ενδεικτικό κόστος DeepSeek ($/1M tokens). Δεν είναι επίσημο API — ενημέρωσε αν
# αλλάξει η τιμολόγηση του DeepSeek. Χρησιμοποιείται μόνο για telemetry εκτίμηση,
# ποτέ για απόφαση.
_COST_PER_1M = {
    "deepseek-chat": {"input": 0.27, "output": 1.10},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
}
_DEFAULT_CHEAP_MODEL = "deepseek-chat"
_DEFAULT_STRONG_MODEL = "deepseek-reasoner"


class ResearchWorkerError(RuntimeError):
    """Αποτυχία ασφαλείας ή ρύθμισης — δεν προσπαθούμε να συνεχίσουμε σιωπηλά."""


@dataclass
class _Telemetry:
    provider: str = "deepseek"
    pass1_model: str = ""
    pass2_model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    started_at: str = ""
    finished_at: str = ""
    sources_analyzed: int = 0
    pass1_candidates: int = 0
    pass2_candidates: int = 0
    pass2_evidence_fetched: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        # estimated_cost_usd is filled in by DeepSeekResearchWorker._telemetry_dict(),
        # which knows the per-pass token split; this base dict just reserves the key.
        return {
            "provider": self.provider,
            "pass1_model": self.pass1_model,
            "pass2_model": self.pass2_model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "estimated_cost_usd": 0.0,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "sources_analyzed": self.sources_analyzed,
            "pass1_candidates": self.pass1_candidates,
            "pass2_candidates": self.pass2_candidates,
            "pass2_evidence_fetched": self.pass2_evidence_fetched,
            "errors": self.errors,
        }


_GITHUB_RE = re.compile(r"github\.com/([\w.-]+/[\w.-]+)")


def _parse_github_repo(url: str) -> str | None:
    """'https://github.com/owner/repo/blob/main/x.py' → 'owner/repo'. None αν δεν είναι GitHub URL."""
    m = _GITHUB_RE.search(url or "")
    if not m:
        return None
    return m.group(1).removesuffix(".git")


def _fetch_readme_snippet(repo: str, max_chars: int = 2500, timeout: int = 12) -> str | None:
    for branch in ("main", "master"):
        try:
            r = requests.get(f"https://raw.githubusercontent.com/{repo}/{branch}/README.md", timeout=timeout)
            if r.ok:
                return r.text[:max_chars]
        except Exception:  # noqa: BLE001
            pass
    return None


def _detect_license(repo: str, timeout: int = 12) -> tuple[str, str]:
    """Πραγματική επαλήθευση license από LICENSE file — ΟΧΙ εικασία του LLM.

    Ίδιο pattern με το πρώτο, χειρωνακτικό research pass: fetch LICENSE/LICENSE.md/
    COPYING, pattern-match το κείμενο· fallback στο GitHub API repo metadata· αλλιώς
    LICENSE_UNVERIFIED. Επιστρέφει (spdx_id_ή_περιγραφή, evidence_source).
    """
    for fname in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        for branch in ("main", "master"):
            try:
                r = requests.get(f"https://raw.githubusercontent.com/{repo}/{branch}/{fname}", timeout=timeout)
            except Exception:  # noqa: BLE001
                continue
            if not r.ok:
                continue
            text = r.text[:800].upper()
            source = f"{fname} file in {repo}/{branch}"
            if "MIT LICENSE" in text or "PERMISSION IS HEREBY GRANTED" in text:
                return "MIT", source
            if "APACHE LICENSE" in text:
                return "Apache-2.0", source
            if "GNU GENERAL PUBLIC LICENSE" in text:
                return "GPL", source
            if "BSD" in text:
                return "BSD", source
            return "OTHER (see file)", source
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}", timeout=timeout)
        if r.ok:
            lic = (r.json().get("license") or {}).get("spdx_id")
            if lic and lic != "NOASSERTION":
                return lic, "GitHub API repo metadata"
    except Exception:  # noqa: BLE001
        pass
    return "LICENSE_UNVERIFIED", "No LICENSE file found; GitHub API returned no license"


class DeepSeekResearchWorker:
    """Read-only, δύο-περασμάτων worker για μαζική έρευνα μέσω DeepSeek."""

    def __init__(
        self,
        task_id: str,
        objective: str,
        context: str,
        sources: list[str],
        output_schema: dict[str, Any] | None = None,
        budget: dict[str, Any] | None = None,
        pass1_model: str | None = None,
        pass2_model: str | None = None,
    ) -> None:
        # task_id μπορεί να έχει subpaths (π.χ. "agent-discovery/runs/2026-08-12-deepseek")
        # για versioned runs χωρίς να πατάει πάνω σε προηγούμενα artifacts. Το ".." και
        # τα absolute paths μπλοκάρονται εδώ· η πραγματική ασφάλεια είναι ο έλεγχος
        # RESEARCH_ROOT containment παρακάτω στο _safety_checks().
        if not task_id or ".." in task_id or task_id.startswith("/") or ":" in task_id:
            raise ResearchWorkerError(f"Μη έγκυρο task_id: {task_id!r}")
        self.task_id = task_id
        self.objective = objective
        self.context = context
        self.sources = sources
        self.output_schema = output_schema or {}
        self.budget = {"max_pass2_candidates": 12, **(budget or {})}
        self.out_dir = RESEARCH_ROOT / task_id

        self._api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self._base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self._pass1_model = pass1_model or os.environ.get("DEEPSEEK_MODEL_CHEAP") or _DEFAULT_CHEAP_MODEL
        self._pass2_model = pass2_model or os.environ.get("DEEPSEEK_MODEL_STRONG") or _DEFAULT_STRONG_MODEL

        self.telemetry = _Telemetry(pass1_model=self._pass1_model, pass2_model=self._pass2_model)
        self._pass1_in = self._pass1_out = self._pass2_in = self._pass2_out = 0
        # _pass2() absorbs KeyboardInterrupt internally to keep partial results and returns
        # normally — this flag is how it tells run() "I was cut short" so metadata.interrupted
        # actually reflects reality instead of silently reporting a clean finish.
        self._interrupted = False
        # HIGH/MEDIUM candidates from Pass 1 that didn't fit the Pass 2 budget — set by
        # _pass2(), read by run() to write shortlist_pending.json. Empty list by default so
        # run() can read it safely even when shortlist was empty and _pass2() never ran.
        self._pass2_pending: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ #
    # Ασφάλεια / setup
    # ------------------------------------------------------------------ #
    def _safety_checks(self) -> None:
        if not self._api_key:
            raise ResearchWorkerError(
                "DEEPSEEK_API_KEY δεν βρέθηκε στο .env — abort. "
                "Δες .env.example. Δεν αγγίζουμε το AI_API_KEY (production κανάλι)."
            )
        gitignore = ROOT / ".gitignore"
        if not gitignore.exists() or ".env" not in gitignore.read_text(encoding="utf-8"):
            raise ResearchWorkerError(
                "SAFETY STOP: το .env δεν φαίνεται στο .gitignore. "
                "Διόρθωσε πριν τρέξεις οποιοδήποτε research task."
            )
        try:
            self.out_dir.resolve().relative_to(RESEARCH_ROOT.resolve())
        except ValueError as exc:
            raise ResearchWorkerError(
                f"Η έξοδος πρέπει να μένει κάτω από {RESEARCH_ROOT} — όχι {self.out_dir}"
            ) from exc

    def check_models(self) -> dict[str, Any]:
        """Ρωτάει το DeepSeek ποια μοντέλα υπάρχουν πραγματικά, αντί να υποθέτει.

        Δεν σκάει αν αποτύχει — απλώς προειδοποιεί και συνεχίζει με τα defaults/
        env overrides. Χρήσιμο για `--dry-run` και για CI sanity checks.
        """
        result = {"available": None, "using": [self._pass1_model, self._pass2_model], "warning": None}
        try:
            r = requests.get(
                f"{self._base_url}/models",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=15,
            )
            if r.ok:
                ids = [m.get("id") for m in r.json().get("data", [])]
                result["available"] = ids
                for m in (self._pass1_model, self._pass2_model):
                    if ids and m not in ids:
                        result["warning"] = (
                            f"Μοντέλο '{m}' δεν βρέθηκε στη λίστα του API "
                            f"({', '.join(ids[:6])}…). Ελέγξτε DEEPSEEK_MODEL_CHEAP/STRONG."
                        )
        except Exception as exc:  # noqa: BLE001
            result["warning"] = f"Δεν ήταν δυνατός ο έλεγχος μοντέλων ({exc}) — συνεχίζω με defaults."
        return result

    # ------------------------------------------------------------------ #
    # DeepSeek transport (plain requests — ίδιο πρότυπο με src/ai.py)
    # ------------------------------------------------------------------ #
    def _call(self, model: str, system: str, user: str, json_mode: bool = True, max_tokens: int = 8000) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                r = requests.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=TIMEOUT,
                )
                if not r.ok:
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
                data = r.json()
                usage = data.get("usage", {})
                tok_in = usage.get("prompt_tokens", 0)
                tok_out = usage.get("completion_tokens", 0)
                self.telemetry.input_tokens += tok_in
                self.telemetry.output_tokens += tok_out
                if model == self._pass1_model:
                    self._pass1_in += tok_in
                    self._pass1_out += tok_out
                else:
                    self._pass2_in += tok_in
                    self._pass2_out += tok_out
                return data["choices"][0]["message"]["content"]
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt == 3:
                    break
                time.sleep(2**attempt)
        self.telemetry.errors.append(str(last_exc)[:200])
        raise ResearchWorkerError(f"DeepSeek call απέτυχε μετά από retries: {last_exc}")

    # ------------------------------------------------------------------ #
    # Fetch evidence (sources μπορούν να είναι URLs ή raw κείμενο)
    # ------------------------------------------------------------------ #
    def _gather_evidence(self) -> list[dict[str, Any]]:
        evidence = []
        for src in self.sources:
            entry: dict[str, Any] = {"source": src}
            if src.startswith("http://") or src.startswith("https://"):
                print(f"  fetching {src} …", end=" ", flush=True)
                try:
                    r = requests.get(src, timeout=20)
                    entry["ok"] = r.ok
                    entry["content"] = r.text[:MAX_SOURCE_CHARS] if r.ok else ""
                    entry["truncated"] = r.ok and len(r.text) > MAX_SOURCE_CHARS
                    print("ok" if r.ok else f"HTTP {r.status_code}")
                except Exception as exc:  # noqa: BLE001
                    entry["ok"] = False
                    entry["error"] = str(exc)[:200]
                    entry["content"] = ""
                    print(f"failed: {str(exc)[:80]}")
            else:
                entry["ok"] = True
                entry["content"] = src[:MAX_SOURCE_CHARS]
                entry["truncated"] = len(src) > MAX_SOURCE_CHARS
            evidence.append(entry)
        self.telemetry.sources_analyzed = len(evidence)
        return evidence

    # ------------------------------------------------------------------ #
    # Pass 1 — φθηνή ευρεία ταξινόμηση
    # ------------------------------------------------------------------ #
    def _pass1(self, evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
        combined = "\n\n---\n\n".join(
            f"SOURCE: {e['source']}\n{e['content']}" for e in evidence if e.get("ok")
        )
        # Πηγές σαν το 500-AI-Agents README έχουν εκατοντάδες γραμμές. Με χαλαρό prompt
        # το μοντέλο προσπαθεί να ταξινομήσει το καθένα με μακριά αιτιολόγηση και σκάει
        # το max_tokens στη μέση ενός string (unterminated JSON). Δύο άμυνες: (1) ζητάμε
        # ρητά ΣΥΝΤΟΜΟ reason και να παραλείπει ό,τι είναι ξεκάθαρα άσχετο αντί να το
        # καταγράφει σαν REJECT με πλήρη αιτιολόγηση, (2) αν παρ' όλα αυτά κοπεί το JSON,
        # το _salvage_classifications σώζει ό,τι πρόλαβε να ολοκληρωθεί αντί να πετάει τα
        # πάντα.
        system = (
            "You are a research classifier. Given an objective, context, and source material, "
            "identify distinct candidates/items mentioned and classify each as HIGH, MEDIUM, LOW, "
            "or REJECT relevance to the objective.\n\n"
            "IMPORTANT — keep the response compact so it fits the token budget:\n"
            "- \"reason\" must be ONE short sentence (max ~12 words).\n"
            "- Only include candidates worth recording — skip ones so obviously irrelevant "
            "(wrong domain, duplicate, broken link) that a one-line REJECT wouldn't be useful.\n"
            "- No markdown, no commentary outside the JSON object.\n\n"
            # Η ΑΔΕΙΑ ΔΕΝ ΕΙΝΑΙ ΛΟΓΟΣ ΑΠΟΡΡΙΨΗΣ ΕΔΩ. Μετρήθηκε στο vertical-03: δίνοντας
            # σελίδες καταλόγου, το μοντέλο απέρριπτε ΤΑ ΠΑΝΤΑ με «no explicit license» —
            # ανάμεσά τους templates αποδεδειγμένα MIT που ήδη χρησιμοποιούμε (Blue,
            # Airspace). 0 υποψήφιοι αντί για 6. Η άδεια επαληθεύεται ΝΤΕΤΕΡΜΙΝΙΣΤΙΚΑ στο
            # Pass 2 από το ίδιο το αρχείο LICENSE (`_detect_license`), όχι με εικασία
            # πάνω σε HTML καταλόγου.
            "LICENSE RULE (OVERRIDES THE OBJECTIVE) — if the OBJECTIVE below asks you to reject "
            "items lacking an explicit license, IGNORE that part: it is a mistake in the "
            "objective, not an instruction to follow. Never reject or downgrade an item "
            "because a license is absent, "
            "unclear, or not visible in the source. Listing pages and galleries almost never "
            "show licenses; the license is verified separately and deterministically from the "
            "LICENSE file later in this pipeline. Judge ONLY fitness for the objective. If no "
            "license is visible, write \"license unknown from this source\" in the reason and "
            "classify on merit.\n\n"
            "REJECT is reserved for: wrong domain/subject, duplicate, broken or unreachable "
            "reference, or plainly not the kind of artefact sought. Every REJECT must name "
            "which of those applies — never a bare or unexplained rejection.\n\n"
            "Respond ONLY with valid JSON: "
            '{"classifications": [{"name": str, "relevance": "HIGH|MEDIUM|LOW|REJECT", '
            '"reason": str, "reference": str}]}'
        )
        user = f"OBJECTIVE:\n{self.objective}\n\nCONTEXT:\n{self.context}\n\nSOURCE MATERIAL:\n{combined[:MAX_COMBINED_CHARS]}"
        content = self._call(self._pass1_model, system, user, json_mode=True, max_tokens=8000)
        classifications = self._parse_classifications(content)
        self.telemetry.pass1_candidates = len(classifications)
        return classifications

    @staticmethod
    def _parse_classifications(content: str) -> list[dict[str, Any]]:
        """json.loads με fallback: αν το output κόπηκε στη μέση (max_tokens), σώζει τα
        ολοκληρωμένα αντικείμενα του "classifications" array αντί να αποτυγχάνει εντελώς.
        """
        try:
            return json.loads(content).get("classifications", [])
        except json.JSONDecodeError:
            pass

        # Salvage: βρες την αρχή του array, μετά κόψε στο τελευταίο πλήρες "}," πριν το
        # σημείο της διακοπής και ξανακλείσε το array/object.
        arr_start = content.find('"classifications"')
        if arr_start == -1:
            raise ResearchWorkerError(
                "Pass 1: μη έγκυρο JSON από DeepSeek και δεν βρέθηκε 'classifications' array "
                "για salvage — πιθανό network/model πρόβλημα, όχι απλή περικοπή."
            )
        bracket_start = content.find("[", arr_start)
        last_complete = content.rfind("},", bracket_start)
        if bracket_start == -1 or last_complete == -1:
            raise ResearchWorkerError(
                "Pass 1: το JSON κόπηκε πριν ολοκληρωθεί έστω ένα αντικείμενο — αύξησε "
                "max_tokens ή μείωσε το μέγεθος της πηγής."
            )
        # content[bracket_start:last_complete+1] = "[{...},{...}" (μέχρι και το τελευταίο
        # πλήρες "}", ΧΩΡΙΣ το κόμμα μετά) — κλείνουμε το array και το ξαναντυλίγουμε.
        salvaged_array = content[bracket_start : last_complete + 1] + "]"
        try:
            data = json.loads('{"classifications": ' + salvaged_array + "}")
            return data.get("classifications", [])
        except json.JSONDecodeError as exc:
            raise ResearchWorkerError(
                f"Pass 1: μη έγκυρο JSON από DeepSeek — ούτε το salvage πέτυχε ({exc})."
            ) from exc

    # ------------------------------------------------------------------ #
    # Pass 2 — βαθιά ανάλυση μόνο στη shortlist
    # ------------------------------------------------------------------ #
    def _pass2(self, shortlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cap = self.budget.get("max_pass2_candidates", 12)
        capped = shortlist[:cap]
        # Ό,τι το Pass 1 έκρινε HIGH/MEDIUM αλλά δεν χωράει στο budget του Pass 2 ΔΕΝ πρέπει
        # να εξαφανίζεται σιωπηλά — δεν είναι ούτε findings (δεν αναλύθηκε) ούτε rejected
        # (το Pass 1 το έκρινε σχετικό). Το run() το γράφει σε shortlist_pending.json.
        self._pass2_pending: list[dict[str, Any]] = list(shortlist[cap:])
        if self._pass2_pending:
            print(f"[Pass 2] Budget cap={cap} — {len(self._pass2_pending)} ακόμη HIGH/MEDIUM "
                  f"candidate(s) μένουν pass1-only σε shortlist_pending.json (αύξησε "
                  "--max-pass2 για να τα αναλύσεις κι αυτά).")
        schema_hint = json.dumps(self.output_schema) if self.output_schema else (
            '{"name": str, "purpose": str, "why_relevant": str, "recommended_treatment": '
            '"REUSE|ADAPT|WRAP|STUDY ONLY|REJECT", "confidence": "High|Medium|Low"}'
        )
        system = (
            "You are a senior analyst performing deep due-diligence on shortlisted candidates. "
            "You may be given a real README excerpt as evidence — ground your analysis in it "
            "when present, don't speculate beyond it. Do NOT state a license — that field is "
            "verified programmatically from the actual LICENSE file, not inferred by you.\n\n"
            f"Context:\n{self.context}\n\nReturn ONLY valid JSON matching this shape:\n{schema_hint}"
        )
        results = []
        total = len(capped)
        print(f"[Pass 2] {total} candidate(s) to deep-analyse with {self._pass2_model} "
              f"(sequential — this can take a while, each call is a real API round-trip)…")
        for i, cand in enumerate(capped, start=1):
            name = cand.get("name", "?")
            print(f"[Pass 2] {i}/{total}: {name} …", end=" ", flush=True)
            t0 = time.time()

            # Πραγματική evidence per-candidate: αν το "reference" του Pass 1 είναι GitHub
            # URL, φέρε README snippet + επαλήθευσε license ΝΤΕΤΕΡΜΙΝΙΣΤΙΚΑ (όχι εικασία
            # LLM). Χωρίς αυτό, κάθε "license" στο findings.json ήταν απλά LLM guess πάνω
            # στο ένα-γραμμή Pass-1 reason — αυτό ήταν το κενό που έδειξε το πρώτο live run.
            repo = _parse_github_repo(cand.get("reference", ""))
            readme_snippet = None
            license_id, license_source = "LICENSE_UNVERIFIED", "No GitHub reference to verify against"
            if repo:
                readme_snippet = _fetch_readme_snippet(repo)
                license_id, license_source = _detect_license(repo)
                self.telemetry.pass2_evidence_fetched += 1

            evidence_block = f"\n\nREADME EXCERPT ({repo}):\n{readme_snippet}" if readme_snippet else ""
            user = f"OBJECTIVE:\n{self.objective}\n\nCANDIDATE:\n{json.dumps(cand)}{evidence_block}"
            try:
                content = self._call(self._pass2_model, system, user, json_mode=True)
                analysis = json.loads(content)
                analysis.setdefault("name", cand.get("name"))
                analysis.setdefault("pass1_reason", cand.get("reason"))
                analysis.setdefault("reference", cand.get("reference"))
                # Ground truth υπερισχύει πάντα του LLM guess — overwrite, όχι setdefault.
                analysis["license"] = license_id
                analysis["license_source"] = license_source
                results.append(analysis)
                print(f"done ({time.time() - t0:.1f}s)")
            except (ResearchWorkerError, json.JSONDecodeError) as exc:
                results.append({"name": cand.get("name"), "error": str(exc)[:200]})
                print(f"failed ({time.time() - t0:.1f}s): {str(exc)[:100]}")
            except KeyboardInterrupt:
                # Μη χάνεις τα ήδη ολοκληρωμένα (και πληρωμένα) analyses — σταμάτα εδώ,
                # το run() γράφει ό,τι υπάρχει με metadata.interrupted=True.
                print(f"\n[Pass 2] Διακόπηκε στο {i}/{total} — αποθηκεύω τα {len(results)} "
                      "ολοκληρωμένα analyses αντί να τα χάσω.")
                self.telemetry.errors.append(f"interrupted at pass2 candidate {i}/{total}")
                self._interrupted = True
                # Ό,τι δεν πρόλαβε να αναλυθεί (από το τρέχον cand μέχρι το τέλος του capped)
                # πάει κι αυτό στο pending — δεν είναι ούτε findings ούτε rejected.
                self._pass2_pending = capped[i - 1 :] + self._pass2_pending
                break
        self.telemetry.pass2_candidates = len(results)
        return results

    # ------------------------------------------------------------------ #
    # Δημόσιο entrypoint
    # ------------------------------------------------------------------ #
    def run(self) -> dict[str, Any]:
        self._safety_checks()
        self.telemetry.started_at = datetime.now(timezone.utc).isoformat()

        # Αρχικοποιημένα ΠΡΙΝ το try ώστε, αν σκάσει/διακοπεί οτιδήποτε παρακάτω, να
        # γράψουμε ό,τι πρόλαβε να ολοκληρωθεί αντί να χάσουμε πληρωμένες κλήσεις API.
        evidence: list[dict[str, Any]] = []
        pass1_results: list[dict[str, Any]] = []
        shortlist: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        findings: list[dict[str, Any]] = []
        interrupted = False

        try:
            print("[1/2] Συλλογή evidence…")
            evidence = self._gather_evidence()
            print(f"[1/2] {len(evidence)} πηγή/ές — Pass 1 ({self._pass1_model})…")
            pass1_results = self._pass1(evidence)
            shortlist = [c for c in pass1_results if c.get("relevance") in ("HIGH", "MEDIUM")]
            rejected = [c for c in pass1_results if c.get("relevance") in ("LOW", "REJECT")]
            print(f"[2/2] Pass 1 έδωσε {len(shortlist)} shortlisted / {len(rejected)} rejected.")
            findings = self._pass2(shortlist) if shortlist else []
            if self._interrupted:  # _pass2 absorbed a KeyboardInterrupt internally
                interrupted = True
        except KeyboardInterrupt:
            # Διακοπή έξω από το _pass2 (π.χ. κατά το evidence fetch ή το Pass 1 call).
            interrupted = True
            print("\n⚠ Διακόπηκε από τον χρήστη — αποθηκεύω ό,τι ολοκληρώθηκε πριν σταματήσω.")
        except ResearchWorkerError:
            # Safety/DeepSeek σφάλματα: δεν έχει νόημα να γράψουμε μισά artifacts αν
            # δεν πέρασε ούτε το Pass 1 — άσε το exception να ανέβει καθαρό στο CLI.
            raise

        self.telemetry.finished_at = datetime.now(timezone.utc).isoformat()

        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._write_json("findings.json", {"task_id": self.task_id, "objective": self.objective, "findings": findings})
        self._write_json("rejected.json", {"task_id": self.task_id, "rejected": rejected})
        self._write_json("evidence.json", {"task_id": self.task_id, "evidence": evidence})
        # Pass-1-only HIGH/MEDIUM candidates cut by the Pass 2 budget cap — never silently
        # dropped. Always write the file (even empty) so its absence never has to be inferred.
        self._write_json("shortlist_pending.json", {
            "task_id": self.task_id,
            "note": "HIGH/MEDIUM in Pass 1 but not deep-analysed — over max_pass2_candidates "
                    "budget, or cut short by an interrupt. Rerun with a higher --max-pass2 to "
                    "analyse these too.",
            "pending": self._pass2_pending,
        })
        meta = self._telemetry_dict()
        meta["interrupted"] = interrupted
        meta["pass2_pending_count"] = len(self._pass2_pending)
        self._write_json("metadata.json", meta)
        self._write_summary(findings, rejected)

        if interrupted:
            print(f"\n⚠ Μερικό αποτέλεσμα γραμμένο σε {self.out_dir} "
                  f"({len(findings)} findings ολοκληρωμένα). Ξανατρέξε το ίδιο preset/task_id "
                  "για πλήρες αποτέλεσμα — θα ξαναγράψει αυτόν τον ίδιο run, όχι νέο.")

        return {
            "task_id": self.task_id,
            "out_dir": str(self.out_dir),
            "findings_count": len(findings),
            "rejected_count": len(rejected),
            "pending_count": len(self._pass2_pending),
            "interrupted": interrupted,
            "telemetry": meta,
        }

    # ------------------------------------------------------------------ #
    # Output helpers
    # ------------------------------------------------------------------ #
    def _telemetry_dict(self) -> dict[str, Any]:
        cost = (
            self._pass1_in * _COST_PER_1M.get(self._pass1_model, {}).get("input", 0.5)
            + self._pass1_out * _COST_PER_1M.get(self._pass1_model, {}).get("output", 1.5)
            + self._pass2_in * _COST_PER_1M.get(self._pass2_model, {}).get("input", 0.5)
            + self._pass2_out * _COST_PER_1M.get(self._pass2_model, {}).get("output", 1.5)
        ) / 1_000_000
        d = self.telemetry.to_dict()
        d["estimated_cost_usd"] = round(cost, 4)
        try:
            start = datetime.fromisoformat(self.telemetry.started_at)
            end = datetime.fromisoformat(self.telemetry.finished_at)
            d["duration_seconds"] = round((end - start).total_seconds(), 1)
        except Exception:  # noqa: BLE001
            d["duration_seconds"] = None
        return d

    def _write_json(self, filename: str, data: Any) -> None:
        (self.out_dir / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _write_summary(self, findings: list[dict[str, Any]], rejected: list[dict[str, Any]]) -> None:
        meta = self._telemetry_dict()
        lines = [
            f"# Research Summary — {self.task_id}",
            "",
            f"**Objective:** {self.objective}",
            f"**Generated:** {meta.get('finished_at', '')}",
            f"**Models:** Pass 1 = {self._pass1_model} | Pass 2 = {self._pass2_model}",
            f"**Tokens:** in={meta['input_tokens']:,} out={meta['output_tokens']:,} "
            f"(~${meta['estimated_cost_usd']} USD)",
            f"**Sources analyzed:** {meta['sources_analyzed']}  |  "
            f"**Deep-analysed:** {len(findings)}  |  **Rejected:** {len(rejected)}  |  "
            f"**Pending (over budget):** {len(self._pass2_pending)}",
            "",
            "## Findings (deep-analysed)",
            "",
        ]
        for f in findings:
            name = f.get("name", "?")
            treatment = f.get("recommended_treatment", "?")
            why = f.get("why_relevant", f.get("pass1_reason", ""))
            lines.append(f"- **{name}** — {treatment} — {why}")
        if not findings:
            lines.append("_No candidates cleared Pass 1 shortlist threshold._")
        if self._pass2_pending:
            lines += ["", "## Pending — HIGH/MEDIUM but not deep-analysed (over --max-pass2 budget)", ""]
            for p in self._pass2_pending:
                lines.append(f"- {p.get('name', '?')} — {p.get('reason', '')}")
            lines.append(
                f"\n_Rerun with `--max-pass2 {len(findings) + len(self._pass2_pending)}` "
                "(same task-id) to also deep-analyse these — see shortlist_pending.json._"
            )
        lines += ["", "## Rejected (sample)", ""]
        for r in rejected[:15]:
            lines.append(f"- {r.get('name', '?')} — {r.get('reason', '')}")
        if len(rejected) > 15:
            lines.append(f"- … and {len(rejected) - 15} more (see rejected.json)")
        (self.out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
