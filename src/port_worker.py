"""Port worker — μηχανικό πρώτο πέρασμα πιστού port ΕΝΟΣ επαληθευμένου PORT_OK.

Αρχιτεκτονική:

    PORT_OK record → απόδοση πρωτοτύπου → DeepSeek patch proposal
    → έλεγχος ορίων → εφαρμογή → build/tests → απόδοση Vitrina
    → READY_FOR_REVIEW → (Claude) → DONE/BLOCKED

Τρεις κανόνες που κρατούν τον worker ειλικρινή:

1. **Fail closed.** Τρέχει μόνο αν το canonical record λέει `PORT_OK`. Οτιδήποτε
   άλλο — ή απουσία record — σταματά χωρίς να γράψει τίποτα.
2. **Ο worker δεν παράγει ποτέ DONE.** Το ανώτερο που μπορεί να δηλώσει είναι
   `READY_FOR_REVIEW`. Η πιστότητα κρίνεται από άνθρωπο/Claude με τα screenshots,
   ποτέ από το μοντέλο που έγραψε τον κώδικα.
3. **Το DeepSeek δεν αγγίζει το filesystem.** Επιστρέφει δομημένα αρχεία, ο
   worker επικυρώνει διαδρομή/μέγεθος/πλήθος και εφαρμόζει μόνο ό,τι περνά.

Ο DeepSeek transport (κλειδί, retries, κόστος) επαναχρησιμοποιείται από τον
`DeepSeekResearchWorker` — δεν στήνεται δεύτερο agent framework.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.research_worker import DeepSeekResearchWorker, ResearchWorkerError  # noqa: E402
from src.vitrina_contract import as_prompt, extract  # noqa: E402
from src.port_guards import run_all, summarize  # noqa: E402
from src.preview_server import PreviewServer, PreviewServerError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research" / "port-worker" / "queue.json"
OUT_ROOT = ROOT / "research" / "port-worker"
SITES = ROOT / "sites"

# ---------------------------------------------------------------- όρια
MAX_FILES = 4                  # JSX + CSS + το πολύ δύο ακόμη
MAX_FILE_BYTES = 60_000
MAX_TOTAL_BYTES = 140_000
MAX_REPAIR_ATTEMPTS = 2
CALL_TIMEOUT_S = 900
MAX_COST_USD = 1.50
SRC_HTML_BUDGET = 70_000
SRC_CSS_BUDGET = 45_000
PREVIEW_PORT = 3881

# Ό,τι δεν ταιριάζει εδώ ΑΠΟΡΡΙΠΤΕΤΑΙ. Ο έλεγχος γίνεται σε resolved path,
# ώστε ένα "../.." να μην μπορεί να βγει έξω.
ALLOWED_PREFIXES = (
    "sites/lib/templates/",
    "research/port-worker/",
)

STATES = ("PENDING", "IN_PROGRESS_DEEPSEEK", "READY_FOR_REVIEW",
          "IN_REVIEW", "DONE", "BLOCKED", "FAILED")


class PortWorkerError(RuntimeError):
    """Παραβίαση ορίου ή ασφάλειας — δεν συνεχίζουμε σιωπηλά."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ queue
def _load_queue() -> dict[str, Any]:
    if not QUEUE.exists():
        raise PortWorkerError(f"Δεν βρέθηκε canonical queue: {QUEUE}")
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def _save_queue(data: dict[str, Any]) -> None:
    """Ατομική εγγραφή: temp + replace. Διακοπή στη μέση δεν αφήνει μισό JSON."""
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    tmp = QUEUE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, QUEUE)


def _set_state(source_id: str, state: str, **extra: Any) -> None:
    if state not in STATES:
        raise PortWorkerError(f"Άγνωστη κατάσταση: {state}")
    q = _load_queue()
    rec = q["sources"][source_id]
    rec["status"] = state
    rec["updated_at"] = _now()
    rec.update(extra)
    _save_queue(q)


# ------------------------------------------------------ απόδοση/screenshots
def _render(root: str, entry: str, tag: str, out_dir: Path) -> dict[str, Any]:
    """Τρέχει το κοινό shot-one.mjs. Επιστρέφει μετρικές ή {'fail': ...}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            ["node", "tests/shot-one.mjs", root, entry, tag, str(out_dir)],
            cwd=SITES, capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return {"fail": "timeout κατά την απόδοση"}
    if proc.returncode != 0:
        return {"fail": (proc.stderr or proc.stdout)[-400:]}
    try:
        return json.loads((out_dir / f"{tag}-metrics.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"fail": f"δεν διαβάστηκαν μετρικές: {exc}"}


# ----------------------------------------------------------- πηγαίο υλικό
def _read_source(rec: dict[str, Any]) -> tuple[str, str]:
    """Διαβάζει το index.html και το κύριο CSS του πρωτοτύπου, με budget."""
    src_dir = ROOT / rec["local_path"]
    entry = src_dir / rec["entry"]
    if not entry.exists():
        raise PortWorkerError(f"Το πρωτότυπο δεν υπάρχει τοπικά: {entry}")
    html = entry.read_text(encoding="utf-8", errors="ignore")[:SRC_HTML_BUDGET]

    css_files = sorted(
        (p for p in entry.parent.rglob("*.css")
         if "bootstrap" not in p.name.lower() and "font-awesome" not in p.name.lower()),
        key=lambda p: -p.stat().st_size,
    )
    css = ""
    for p in css_files:
        if len(css) >= SRC_CSS_BUDGET:
            break
        css += f"\n/* ---- {p.name} ---- */\n" + p.read_text(encoding="utf-8", errors="ignore")
    return html, css[:SRC_CSS_BUDGET]


# ---------------------------------------------------------------- DeepSeek
class _Chat(DeepSeekResearchWorker):
    """Λεπτός wrapper: επαναχρησιμοποιεί κλειδί, retries, μέτρηση κόστους."""

    def __init__(self, source_id: str) -> None:
        super().__init__(task_id=f"port-worker/{source_id}", objective="port",
                         context="port", sources=[])

    def ask(self, system: str, user: str, max_tokens: int = 16000) -> str:
        return self._call(self._pass2_model, system, user, json_mode=True, max_tokens=max_tokens)


SYSTEM = """You are a senior front-end engineer performing a FAITHFUL PORT.

You are NOT redesigning. You are re-implementing an existing rendered website
in the Vitrina stack while preserving its visual identity.

PRESERVE: composition, section order, proportions, spacing rhythm, typographic
hierarchy, palette relationships, navigation, gallery/card structure, image
aspect ratios, border-radius/shadow language, desktop character and the mobile
transformation.

ADAPT: business data only.

You MUST NOT invent: testimonials, ratings, years of experience, awards,
certifications, customer counts, prices, discounts, stock scarcity, guarantees,
partner or client logos, team members, statistics, credentials. If the original
has such a section and there is no real data for it, OMIT the section and record
it in "deviations". Omitting is correct; faking is a contract violation.

Return ONLY a JSON object:
{
 "theme_key": "kebab-case",
 "component": "PascalCase",
 "files": [{"path": "sites/lib/templates/X.jsx", "content": "..."}],
 "deviations": [{"what": "...", "why": "..."}],
 "notes": "..."
}"""


def _contract(rec: dict[str, Any], contract: dict[str, Any]) -> str:
    """Το data μέρος ΠΑΡΑΓΕΤΑΙ από τον κώδικα (vitrina_contract), δεν γράφεται
    με το χέρι: αυτό ήταν η μοναδική αιτία ΟΛΩΝ των runtime σφαλμάτων στο πρώτο
    proof. Ένα χειρόγραφο συμβόλαιο παλιώνει σιωπηλά· ένα παραγόμενο όχι."""
    return f"""VITRINA TARGET CONTRACT

Framework: Next.js 14 App Router, React SERVER component (no hooks, no
useState/useEffect, no onClick, no 'use client'). CSS Modules only.

File 1: sites/lib/templates/{rec['component']}.jsx
File 2: sites/lib/templates/{rec['component']}.module.css

{as_prompt(contract, rec['component'])}

MEDIA — υποχρεωτικό όταν το πρωτότυπο έχει εικόνες: κάθε θέση εικόνας δένει σε
d.gallery[i].image με alt από d.gallery[i].title. ΠΟΤΕ αρχεία του πρωτοτύπου.

ΚΕΙΜΕΝΟ — κανένας ορατός τίτλος δεν μένει στα αγγλικά του πρωτοτύπου. Κάθε
ορατό κείμενο ή δένει σε d. ή είναι ελληνικό δομικό label. Ονόματα,
διευθύνσεις, τηλέφωνα και τιμές του πρωτοτύπου ΑΠΑΓΟΡΕΥΟΝΤΑΙ αυτούσια.

CSS: κάθε χρώμα περνά από τους 11 spine ρόλους στο .root:
  --vt-surface, --vt-surface-2, --vt-surface-deep, --vt-ink, --vt-ink-soft,
  --vt-on-deep, --vt-accent, --vt-on-accent, --vt-accent-ink,
  --vt-accent-on-deep, --vt-line
Οι ΤΙΜΕΣ τους βγαίνουν από την παλέτα του πρωτοτύπου. Κανένα hex εκτός .root,
κανένα !important. Τα CSS Modules θέλουν pure selectors: `a:focus-visible`
σκέτο ΔΕΝ μεταγλωττίζεται — γράψε `.root a:focus-visible`.

SOURCE: {rec['name']} — {rec['source_url']}
LICENCE (already verified, do not re-litigate): {rec['license']}
TARGET VERTICALS: {', '.join(rec['verticals'])}
FIDELITY NOTES FROM RESEARCH: {rec['fidelity_notes']}
REQUIRED REMOVALS (truth contract): {'; '.join(rec['required_removals'])}"""


# ----------------------------------------------------------- patch control
def _validate(files: list[dict[str, str]], rec: dict[str, Any]) -> list[dict[str, str]]:
    if not files:
        raise PortWorkerError("Το DeepSeek δεν επέστρεψε αρχεία")
    if len(files) > MAX_FILES:
        raise PortWorkerError(f"{len(files)} αρχεία > όριο {MAX_FILES}")
    total = 0
    clean: list[dict[str, str]] = []
    for f in files:
        path, content = f.get("path", ""), f.get("content", "")
        norm = path.replace("\\", "/").lstrip("./")
        if not any(norm.startswith(p) for p in ALLOWED_PREFIXES):
            raise PortWorkerError(f"Διαδρομή εκτός allowlist: {path!r}")
        resolved = (ROOT / norm).resolve()
        if not str(resolved).startswith(str(ROOT.resolve())):
            raise PortWorkerError(f"Διαδρομή δραπετεύει από το repo: {path!r}")
        if resolved.exists() and rec["component"] not in resolved.name:
            raise PortWorkerError(f"Απόπειρα αλλαγής ξένου αρχείου: {norm}")
        size = len(content.encode("utf-8"))
        if size > MAX_FILE_BYTES:
            raise PortWorkerError(f"{norm}: {size}B > όριο {MAX_FILE_BYTES}")
        if "'use client'" in content or '"use client"' in content:
            raise PortWorkerError(f"{norm}: server component, δεν επιτρέπεται 'use client'")
        if "!important" in content:
            raise PortWorkerError(f"{norm}: !important σπάει το colour spine")
        total += size
        clean.append({"path": norm, "content": content})
    if total > MAX_TOTAL_BYTES:
        raise PortWorkerError(f"σύνολο {total}B > όριο {MAX_TOTAL_BYTES}")
    return clean


def _apply(files: list[dict[str, str]]) -> list[str]:
    written = []
    for f in files:
        p = ROOT / f["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f["content"], encoding="utf-8")
        written.append(f["path"])
    return written


def _q(s: str) -> str:
    """Τιμή για μονά εισαγωγικά σε JS literal."""
    return s.replace("\\", "\\\\").replace("'", "\'")


def _register(rec: dict[str, Any]) -> bool:
    """Εγγραφή στο registry — από τον WORKER, όχι από το DeepSeek.

    Προσθετική και μόνο: δεν ξαναγράφει το αρχείο και δεν πειράζει υπάρχουσες
    εγγραφές, γιατί το index.js έχει ταυτόχρονα αλλαγές άλλου agent.
    """
    idx = SITES / "lib" / "templates" / "index.js"
    txt = idx.read_text(encoding="utf-8")
    key, comp = rec["theme_key"], rec["component"]
    if f"'{key}'" in txt:
        return False
    imp = f"import {comp} from './{comp}'\n"
    txt = imp + txt if not txt.startswith("import") else txt.replace("\n", "\n" + imp, 1)
    txt = txt.replace("export const TEMPLATES = {", f"export const TEMPLATES = {{ '{key}': {comp},", 1)
    txt = txt.replace("export const TEMPLATE_KEYS = [", f"export const TEMPLATE_KEYS = ['{key}', ", 1)
    txt = txt.replace("export const TEMPLATE_META = {",
                      "export const TEMPLATE_META = {\n"
                      f"  '{key}': {{ label: '{_q(rec['label'])}', "
                      f"desc: '{_q(rec['desc'])}', "
                      f"category: '{rec['verticals'][0]}', "
                      "customizable: { palette: false, fontPair: false } },", 1)
    idx.write_text(txt, encoding="utf-8")

    # Το spine_guard απαιτεί κάθε component να δηλώνεται migrated ή pending.
    sg = SITES / "tests" / "spine_guard.mjs"
    stxt = sg.read_text(encoding="utf-8")
    if f"'{comp}'" not in stxt:
        # Χωρίς backreference: ένα χαμένο  σε προηγούμενη έκδοση ΔΙΕΓΡΑΨΕ τη
        # δήλωση αντί να προσθέσει, και το spine_guard.mjs έσπαγε με SyntaxError.
        anchor = "export const MIGRATED = ["
        stxt = stxt.replace(anchor, f"{anchor}'{comp}', ", 1)
        sg.write_text(stxt, encoding="utf-8")

    # Το templateRegistry.mjs απαιτεί ΓΡΑΠΤΟ λόγο για κάθε theme εκτός profiles.
    reg = SITES / "tests" / "templateRegistry.mjs"
    rtxt = reg.read_text(encoding="utf-8")
    if f"'{key}':" not in rtxt:
        rtxt = rtxt.replace("const UNPROFILED = {",
                            f"const UNPROFILED = {{\n  '{key}': 'Port worker proof — "
                            "εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',", 1)
        reg.write_text(rtxt, encoding="utf-8")
    return True


def _run(cmd: list[str], cwd: Path, timeout: int = 600,
         env: dict[str, str] | None = None) -> tuple[bool, str]:
    exe = shutil.which(cmd[0]) or cmd[0]
    try:
        p = subprocess.run([exe, *cmd[1:]], cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace", env=env)
        return p.returncode == 0, (p.stdout + p.stderr)[-2500:]
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except OSError as exc:
        return False, f"δεν εκτελέστηκε: {exc}"


# ------------------------------------------------------------------ ροή
def _actionable(name: str, log: str) -> str:
    """Μόνο οι γραμμές που λένε ΤΙ να διορθωθεί.

    Το spine_guard τυπώνει ~250 γραμμές, από τις οποίες μία είναι η παράβαση.
    Στο 4ο proof το μοντέλο πήρε 900 χαρακτήρες ουράς — δηλαδή τα ✓ του τέλους —
    και δεν είδε ποτέ το `✗ MedicCare: accent-ink/surface 1.00<4.5`. Τρεις
    επιδιορθώσεις χάθηκαν σε θόρυβο, όχι σε δυσκολία.
    """
    lines = log.splitlines()
    hits = [l.strip() for l in lines
            if "✗" in l or "Syntax error" in l or "Module not found" in l
            or "AssertionError" in l or "Failed to compile" in l
            or "αντίθεση" in l or "παραβάσ" in l]
    if not hits:
        hits = [l.strip() for l in lines if l.strip()][-12:]
    body = "\n".join(dict.fromkeys(hits))[:1200]
    return f"--- {name} ΑΠΕΤΥΧΕ ---\n{body}"


def port_source(source_id: str) -> dict[str, Any]:
    q = _load_queue()
    rec = q["sources"].get(source_id)
    if rec is None:
        raise PortWorkerError(f"Άγνωστο source_id: {source_id!r}")

    # ---- fail closed
    if rec.get("decision") != "PORT_OK":
        raise PortWorkerError(
            f"{source_id}: decision={rec.get('decision')!r} — μόνο PORT_OK επιτρέπεται")
    if rec.get("status") in ("DONE", "READY_FOR_REVIEW", "IN_REVIEW"):
        return {"source_id": source_id, "status": rec["status"], "skipped": "ήδη επεξεργασμένο"}
    if (SITES / "lib" / "templates" / f"{rec['component']}.jsx").exists():
        return {"source_id": source_id, "status": "SKIPPED", "skipped": "το theme υπάρχει ήδη"}

    out = OUT_ROOT / source_id
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    res: dict[str, Any] = {
        "source_id": source_id, "theme_key": rec["theme_key"], "started_at": _now(),
    }
    _set_state(source_id, "IN_PROGRESS_DEEPSEEK")

    # ---- 1. ΤΟ ΠΡΩΤΟΤΥΠΟ ΕΙΝΑΙ Η ΟΠΤΙΚΗ ΠΗΓΗ ΑΛΗΘΕΙΑΣ
    orig = _render(rec["local_path"], rec["entry"], "original", out)
    res["original_render_status"] = "FAIL" if "fail" in orig else "OK"
    if "fail" in orig:
        _set_state(source_id, "BLOCKED", blocked_reason=f"ENVIRONMENT_BLOCKED: {orig['fail']}")
        res.update(status="BLOCKED", reason=orig["fail"])
        (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        return res

    # ---- 2. μηχανικό πέρασμα DeepSeek
    html, css = _read_source(rec)
    chat = _Chat(source_id)
    chat._safety_checks()
    res["model"] = chat._pass2_model
    contract = extract()
    user = (_contract(rec, contract) + "\n\n=== ORIGINAL index.html ===\n" + html
            + "\n\n=== ORIGINAL CSS ===\n" + css)
    # ΔΥΟ κλήσεις, όχι μία. Μετρήθηκε: ένα ολόκληρο theme (JSX+CSS) σε ένα JSON
    # χτυπά το όριο εξόδου και κόβεται στη μέση — τρεις σερί αποτυχίες
    # «Unterminated string». Χωριστά χωρά, και το CSS γράφεται γνωρίζοντας τα
    # πραγματικά class names του JSX αντί να τα μαντεύει.
    payload: dict[str, Any] = {"files": [], "deviations": []}
    files: list[dict[str, str]] = []
    problem: str | None = None

    def _one(step: str, instruction: str, keep: str) -> dict[str, Any] | None:
        nonlocal problem
        for attempt in range(1 + MAX_REPAIR_ATTEMPTS):
            prompt = f"{user}\n\n=== ΒΗΜΑ: {step} ===\n{instruction}"
            if problem:
                prompt += (f"\n\n=== Η ΠΡΟΗΓΟΥΜΕΝΗ ΑΠΑΝΤΗΣΗ ΑΠΟΡΡΙΦΘΗΚΕ ===\n{problem}\n"
                           "Διόρθωσέ το και ξαναδώσε ΟΛΟΚΛΗΡΟ το αρχείο.")
            try:
                raw = chat.ask(SYSTEM, prompt, max_tokens=32000)
            except ResearchWorkerError as exc:
                problem = str(exc)[:300]
                return None
            (out / f"deepseek-{step}-{attempt + 1}.json").write_text(raw, encoding="utf-8")
            try:
                data = json.loads(raw)
                # Κρατάμε ΜΟΝΟ το αρχείο που ζητά αυτό το βήμα.
                data["files"] = [f for f in data.get("files", [])
                                 if f.get("path", "").endswith(keep)]
                if not data["files"]:
                    raise PortWorkerError(f"το βήμα {step} δεν επέστρεψε αρχείο {keep}")
                _validate(data["files"], rec)
                problem = None
                return data
            except (json.JSONDecodeError, PortWorkerError) as exc:
                problem = str(exc)[:300]
                res.setdefault("repair_attempts", []).append(f"{step}: {problem}")
        return None

    def _generate(feedback: str = "") -> None:
        """Ένας πλήρης κύκλος JSX+CSS. Το `feedback` είναι ό,τι απέρριψαν οι
        guards ή το build — πάει αυτούσιο πίσω στο μοντέλο."""
        nonlocal payload, files
        extra = (f"\n\n=== Η ΠΡΟΗΓΟΥΜΕΝΗ ΠΡΟΣΠΑΘΕΙΑ ΑΠΟΡΡΙΦΘΗΚΕ ===\n{feedback}\n"
                 "Διόρθωσε ΑΚΡΙΒΩΣ αυτά. Μην αλλάξεις τίποτε άλλο.") if feedback else ""
        jsx = _one("JSX", f"Return ONLY sites/lib/templates/{rec['component']}.jsx in files[]. "
                          "Use semantic class names via the `s` import; the stylesheet comes next."
                          + extra, keep=".jsx")
        if not jsx:
            return
        jsx_src = jsx["files"][0]["content"]
        css = _one("CSS", f"Return ONLY sites/lib/templates/{rec['component']}.module.css in files[]. "
                          "It must style EXACTLY the class names used below and nothing else."
                          + extra
                          + f"\n=== THE JSX YOU JUST WROTE ===\n{jsx_src}", keep=".css")
        if not css:
            return
        payload["files"] = jsx["files"] + css["files"]
        payload["deviations"] = (jsx.get("deviations") or []) + (css.get("deviations") or [])
        files = _validate(payload["files"], rec)

    # Guards ΠΡΙΝ γραφτεί οτιδήποτε στον δίσκο: ένα port με λάθος prop ή με
    # μηδέν δεμένες εικόνες δεν αξίζει καν build. Ό,τι απορρίπτουν πάει
    # αυτούσιο πίσω στο μοντέλο, μέχρι MAX_REPAIR_ATTEMPTS φορές.
    _generate()
    for _ in range(MAX_REPAIR_ATTEMPTS):
        if not files:
            break
        guard_out = run_all(files, contract, html, tuple(rec.get("allowed_labels", [])))
        if not any(guard_out.values()):
            break
        res.setdefault("repair_attempts", []).append("guards: " + summarize(guard_out)[:400])
        _generate(summarize(guard_out))
    if files:
        guard_out = run_all(files, contract, html, tuple(rec.get("allowed_labels", [])))
        res["guards"] = guard_out
        if any(guard_out.values()):
            _set_state(source_id, "FAILED", failure="guards")
            res.update(status="FAILED", reason="guards: " + summarize(guard_out)[:400])
            (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
            return res

    tele = chat._telemetry_dict()
    res["token_usage"] = {"input": tele["input_tokens"], "output": tele["output_tokens"]}
    res["cost_usd"] = tele["estimated_cost_usd"]
    if res["cost_usd"] > MAX_COST_USD:
        _set_state(source_id, "FAILED", failure="υπέρβαση ορίου κόστους")
        res.update(status="FAILED", reason=f"κόστος {res['cost_usd']} > {MAX_COST_USD}")
        return res
    if problem is not None:
        _set_state(source_id, "FAILED", failure=problem)
        res.update(status="FAILED", reason=problem)
        (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        return res

    # ---- 3. build/tests, με ανατροφοδότηση σφαλμάτων στο μοντέλο
    def _suite() -> dict[str, dict[str, Any]]:
        out_tests: dict[str, dict[str, Any]] = {}
        for name, cmd in (("templateRegistry", ["node", "tests/templateRegistry.mjs"]),
                          ("spine_guard", ["node", "tests/spine_guard.mjs"]),
                          ("trust_guard", ["node", "tests/trust_guard.mjs"])):
            ok, log = _run(cmd, SITES, timeout=240)
            out_tests[name] = {"passed": ok, "log": log}
        # Δικό μας NEXT_DIST_DIR: δύο agents δεν μοιράζονται .next (CLAUDE.md).
        bok, blog = _run(["npx", "next", "build"], SITES, timeout=900,
                         env=dict(os.environ, NEXT_DIST_DIR=".next-port"))
        out_tests["next_build"] = {"passed": bok, "log": blog[-1800:]}
        return out_tests

    res["files_changed"] = _apply(files)
    res["deviations"] = payload.get("deviations", [])
    res["registered"] = _register(rec)
    tests = _suite()

    # Ένα σφάλμα build είναι ακριβώς το είδος που το μοντέλο μπορεί να διορθώσει
    # μόνο του — αρκεί να το δει. Στο πρώτο proof δεν του το έδειχνα ποτέ και
    # έπρεπε να μπω εγώ για ένα «selector is not pure».
    for _ in range(MAX_REPAIR_ATTEMPTS):
        failed = {k: v for k, v in tests.items() if not v["passed"]}
        if not failed:
            break
        report = '\n\n'.join(_actionable(k, v["log"]) for k, v in failed.items())
        res.setdefault("repair_attempts", []).append("build: " + ", ".join(failed))
        _generate(report)
        if not files:
            break
        guard_out = run_all(files, contract, html, tuple(rec.get("allowed_labels", [])))
        res["guards"] = guard_out
        if any(guard_out.values()):
            _set_state(source_id, "FAILED", failure="guards μετά από build repair")
            res.update(status="FAILED", reason="guards: " + summarize(guard_out)[:400])
            (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
            return res
        res["files_changed"] = _apply(files)
        tests = _suite()

    res["tests_run"] = len(tests)
    res["tests_passed"] = sum(1 for t in tests.values() if t["passed"])
    res["tests_failed"] = res["tests_run"] - res["tests_passed"]
    res["tests"] = {k: {"passed": v["passed"]} for k, v in tests.items()}
    (out / "test-logs.json").write_text(json.dumps(tests, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- 4. Απόδοση Vitrina — μέρος του worker, όχι χειροκίνητο βήμα.
    # Στο πρώτο proof το έκανα με το χέρι· έτσι ο worker δήλωνε
    # READY_FOR_REVIEW χωρίς να έχει δει ποτέ τη δική του σελίδα.
    vit: dict[str, Any] = {"fail": "δεν εκτελέστηκε (build απέτυχε)"}
    if tests.get("next_build", {}).get("passed"):
        try:
            with PreviewServer(SITES, PREVIEW_PORT) as srv:
                res["preview_server"] = {"pid": srv.proc.pid if srv.proc else None,
                                         "port": PREVIEW_PORT, "reclaimed": srv.reclaimed}
                if srv.wait_ready(f"preview/{rec['theme_key']}"):
                    vit = _render(f"http://127.0.0.1:{PREVIEW_PORT}",
                                  f"preview/{rec['theme_key']}", "vitrina", out)
                else:
                    vit = {"fail": "ο preview server δεν απάντησε 200 εντός ορίου"}
        except PreviewServerError as exc:
            vit = {"fail": str(exc)}

    res["vitrina_render_status"] = "FAIL" if "fail" in vit else "OK"
    res["vitrina_metrics"] = vit
    for label in ("desktop", "mobile"):
        m = vit.get(label) or {}
        res.setdefault("render", {})[label] = {
            "overflow": m.get("overflow"), "innerOverflow": m.get("innerOverflow"),
            "broken": m.get("broken"), "images": m.get("images"),
            "h1": m.get("h1"), "consoleErrors": m.get("consoleErrors"),
        }

    # Fail closed στα render-time ευρήματα που δεν φαίνονται στατικά.
    render_problems: list[str] = []
    for label in ("desktop", "mobile"):
        m = vit.get(label) or {}
        if "fail" in m or not m:
            render_problems.append(f"{label}: δεν αποδόθηκε")
            continue
        if m.get("overflow", 0) > 0:
            render_problems.append(f"{label}: οριζόντια υπερχείλιση {m['overflow']}px")
        if m.get("innerOverflow"):
            render_problems.append(f"{label}: εσωτερική υπερχείλιση — {', '.join(m['innerOverflow'][:3])}")
        if m.get("broken", 0) > 0:
            render_problems.append(f"{label}: {m['broken']} σπασμένες εικόνες")
        if m.get("consoleErrors", 0) > 0:
            render_problems.append(f"{label}: {m['consoleErrors']} console errors")
        if m.get("h1") != 1:
            render_problems.append(f"{label}: {m.get('h1')} × h1 (πρέπει 1)")
        orig_imgs = (orig.get("desktop") or {}).get("images", 0)
        if orig_imgs >= 3 and m.get("images", 0) == 0:
            render_problems.append(f"{label}: το πρωτότυπο έχει {orig_imgs} εικόνες, το port 0")
    res["render_problems"] = render_problems

    res["elapsed_seconds"] = round(time.time() - started, 1)
    res["status"] = ("READY_FOR_REVIEW"
                     if res["tests_failed"] == 0 and not render_problems
                     else "FAILED")
    res["original_metrics"] = orig
    (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    _set_state(source_id, res["status"], result=str((out / "result.json").relative_to(ROOT)))
    return res


def next_pending() -> str | None:
    q = _load_queue()
    for sid, rec in q["sources"].items():
        if rec.get("decision") == "PORT_OK" and rec.get("status") == "PENDING":
            return sid
    return None
