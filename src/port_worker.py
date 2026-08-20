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
from src.vitrina_contract import as_prompt, availability, availability_prompt, extract  # noqa: E402
from src.port_guards import run_all, summarize  # noqa: E402
from src.preview_server import PreviewServer, PreviewServerError  # noqa: E402
from src.repair_txn import Ledger  # noqa: E402
from src import contrast_repair as cr  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research" / "port-worker" / "queue.json"
OUT_ROOT = ROOT / "research" / "port-worker"
SITES = ROOT / "sites"

# ---------------------------------------------------------------- όρια
MAX_FILES = 4                  # JSX + CSS + το πολύ δύο ακόμη
MAX_FILE_BYTES = 60_000
MAX_TOTAL_BYTES = 140_000
MAX_REPAIR_ATTEMPTS = 4
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
def sticky_lines(existing: list[str], text: str) -> list[str]:
    """Συσσώρευση περιορισμών χωρίς διπλότυπα, με σταθερή σειρά.

    Ξεχωριστή συνάρτηση επειδή είναι ο πυρήνας μιας μετρημένης παλινδρόμησης:
    ο guard έκοψε το `d.services[].price`, το μοντέλο το αφαίρεσε, και ο επόμενος
    γύρος — που αφορούσε μόνο χρώματα — το ξαναέφερε. Ό,τι απορρίφθηκε μία φορά
    πρέπει να ταξιδεύει με κάθε επόμενο prompt.
    """
    out = list(existing)
    for line in filter(None, (ln.strip() for ln in text.splitlines())):
        if line not in out:
            out.append(line)
    return out


def clip_finding(item: dict[str, Any], viewport: str, width: int,
                 component: str) -> tuple[str, str]:
    """Ταξινόμηση ιδιοκτησίας + ντετερμινιστική συνταγή για ΕΝΑ αποκομμένο πλαίσιο.

    Επιστρέφει (ΤΑΞΙΝΟΜΗΣΗ, κείμενο). Το «ποιος φταίει» δεν είναι το ίδιο με το
    «ποιος μπορεί να το λύσει»: το `FindUs_mapBox` ανήκει σε κοινό component που
    το `_validate` σωστά απαγορεύει να πειραχτεί — 60+ themes το μοιράζονται. Το
    μοντέλο πρέπει να σταλεί στον ΠΛΗΣΙΕΣΤΕΡΟ γονέα που του ανήκει, αλλιώς η
    συνταγή είναι ανεκτέλεστη και καίει ολόκληρο το budget επιδιόρθωσης.
    """
    nl = chr(10)
    sel, owner = item.get("sel", "?"), item.get("owner", "")
    target = item.get("target", "")
    cut = " · ".join(f"«{c['text']}» κρυμμένο κατά {c['by']}px"
                     for c in item.get("cut", []))
    head = nl.join([
        f"{viewport.upper()} {width} FAIL: πραγματικό αποκομμένο περιεχόμενο",
        f"  selector: .{sel}",
        f"  clientHeight: {item.get('clientH')}px · περιεχόμενο: {item.get('scrollH')}px"
        f" · κρυμμένα: {item.get('hidden')}px ({item.get('axis')})",
        f"  overflow: {item.get('overflow')}",
        f"  χάνεται: {cut}",
    ])
    forbid = nl.join([
        "  ΑΠΑΓΟΡΕΥΕΤΑΙ λύση με απόκρυψη: όχι overflow:hidden, όχι μικρότερη",
        "  γραμματοσειρά για να χωρέσει, όχι αφαίρεση του χάρτη ή περιεχομένου.",
        "  Το κείμενο πρέπει να μείνει ορατό και χρησιμοποιήσιμο.",
    ])

    if owner and owner != component:
        if not target:
            return ("BLOCKED_SHARED_COMPONENT", nl.join([
                head,
                f"  Το .{sel} ανήκει στο κοινό component «{owner}» και ΔΕΝ υπάρχει",
                "  γονέας του theme που να μπορεί να το λύσει.",
            ]))
        return ("SHARED_COMPONENT", nl.join([
            head,
            f"  ΙΔΙΟΚΤΗΣΙΑ: το .{sel} ανήκει στο κοινό «{owner}» — ΜΗΝ το πειράξεις.",
            f"  ΕΠΙΤΡΕΠΤΟΣ ΣΤΟΧΟΣ: .{target} (δικό σου). Δώσε στο κοινό component",
            "  αρκετό πλάτος/ύψος — π.χ. ολόκληρη τη γραμμή αντί για στενή στήλη —",
            "  ώστε να χωρά το περιεχόμενό του.",
            forbid,
        ]))
    return ("THEME_OWNED", nl.join([
        head, f"  ΕΠΙΤΡΕΠΤΟΣ ΣΤΟΧΟΣ: .{sel} (δικό σου).", forbid,
    ]))


def _appearance(theme_key: str, biz: str, port: int) -> dict[str, Any]:
    """Αόρατο κείμενο, γραμματοσειρές που δεν κατεβάσαμε, σπασμένες εικόνες.

    Μετρήθηκε: ένα CTA με αντίθεση 1.00 (λευκό σε λευκό) πέρασε ΟΛΕΣ τις πύλες
    του worker — build, spine_guard, trust_guard, μηδενική υπερχείλιση — γιατί
    καμία τους δεν κοιτάζει pixel. Το design_guard.mjs υπήρχε ήδη γι' αυτό
    ακριβώς· απλώς ο worker δεν το έτρεχε ποτέ.
    """
    ok, log = _run(["node", "tests/design_guard.mjs", "--base", f"http://127.0.0.1:{port}",
                    "--only", theme_key, "--biz", biz], SITES, timeout=300)
    problems = [ln.strip() for ln in log.splitlines()
                if ln.strip().startswith(("└", "•")) or "αόρατο κείμενο" in ln]
    return {"passed": ok, "problems": problems[:8], "log": log[-1200:]}


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


def _contract(rec: dict[str, Any], contract: dict[str, Any], biz: str = "") -> str:
    """Το data μέρος ΠΑΡΑΓΕΤΑΙ από τον κώδικα (vitrina_contract), δεν γράφεται
    με το χέρι: αυτό ήταν η μοναδική αιτία ΟΛΩΝ των runtime σφαλμάτων στο πρώτο
    proof. Ένα χειρόγραφο συμβόλαιο παλιώνει σιωπηλά· ένα παραγόμενο όχι."""
    return f"""VITRINA TARGET CONTRACT

Framework: Next.js 14 App Router, React SERVER component (no hooks, no
useState/useEffect, no onClick, no 'use client'). CSS Modules only.

File 1: sites/lib/templates/{rec['component']}.jsx
File 2: sites/lib/templates/{rec['component']}.module.css

{as_prompt(contract, rec['component'])}

{availability_prompt(availability(biz), {k: v.get('item_keys', []) for k, v in contract['fields'].items() if v['type'] == 'array'}) if biz else ''}

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

ΤΑΥΤΟΤΗΤΑ ΣΧΕΔΙΟΥ — ΠΡΕΠΕΙ να επιβιώσει (χωρίς αυτά το port χάνει το νόημά του):
{chr(10).join('  • ' + x for x in rec.get('required_design', []))}

ΠΡΟΣΑΡΜΟΣΙΜΑ — κράτα την ιδέα, μετάφρασέ την σε αληθινή δομή του Vitrina:
{chr(10).join('  • ' + x for x in rec.get('adaptable', []))}

ΔΕΝ ΥΠΟΣΤΗΡΙΖΟΝΤΑΙ ΑΠΟ ΤΟ ΠΡΟΪΟΝ — ΠΑΡΕΛΕΙΨΕ τα. Η απουσία τους είναι ΣΩΣΤΗ.
ΑΠΑΓΟΡΕΥΕΤΑΙ να τα καλύψεις με επινοημένα δεδομένα:
{chr(10).join('  • ' + x for x in rec.get('unsupported_by_product', []))}

Η πηγή είναι ΕΜΠΝΕΥΣΗ, όχι προδιαγραφή αντιγραφής. Στόχος: ένα διακριτό,
επαγγελματικό theme του Vitrina που κρατά το DNA της πηγής — όχι πιστό
αντίγραφο κάθε ενότητας.

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


_ROLE_RE = re.compile(r"([a-z][a-z0-9-]*)/([a-z][a-z0-9-]*)\s+([\d.]+)\s*<\s*([\d.]+)")
_LOWEST_RE = re.compile(r"αντίθεση[^:]*:\s*([\d.]+):1\s*—\s*\S+[^)]*\)\s*([a-z][a-z0-9-]*)/([a-z][a-z0-9-]*)")


def _spine_prescription(log: str, css_text: str) -> str:
    """Συνταγή, όχι διάγνωση.

    Το `--vt-accent-ink 3.69:1` λέει ΟΤΙ κάτι φταίει, όχι ΤΙ να γίνει. Το
    μοντέλο μάντευε το βήμα και συνέκλινε αργά (1.00 -> 3.69 σε τρεις γύρους).
    Εδώ παράγεται ντετερμινιστικά από το ίδιο το αποτέλεσμα του guard: ρόλος,
    μετρημένη αντίθεση, απαιτούμενο κατώφλι, οι πραγματικές τιμές των δύο
    tokens, και η μοναδική επιτρεπτή κατεύθυνση διόρθωσης.
    """
    pairs: list[tuple[str, str, str, str]] = []
    for line in log.splitlines():
        if "✗" in line:
            pairs += [(a, b, got, need) for a, b, got, need in _ROLE_RE.findall(line)]
    if not pairs:
        m = _LOWEST_RE.search(log)
        if m:
            pairs = [(m.group(2), m.group(3), m.group(1), "4.5")]
    if not pairs:
        return ""

    values = dict(re.findall(r"--vt-([a-z][a-z0-9-]*)\s*:\s*([^;]+);", css_text))
    out = ["--- ΠΑΡΑΒΑΣΗ ΑΝΤΙΘΕΣΗΣ (spine) ---"]
    for fg, bg, got, need in dict.fromkeys(pairs):
        out += [
            f"FAIL: --vt-{fg} πάνω σε --vt-{bg}",
            f"  μετρημένη αντίθεση = {got}:1",
            f"  απαιτούμενο ελάχιστο = {need}:1",
            f"  foreground --vt-{fg}: {values.get(fg, '(άγνωστο)').strip()}",
            f"  background --vt-{bg}: {values.get(bg, '(άγνωστο)').strip()}",
            f"  ΔΙΟΡΘΩΣΗ: άλλαξε ΜΟΝΟ την τιμή του --vt-{fg} στο .root, αρκετά",
            f"  ώστε η αντίθεση με το --vt-{bg} να φτάσει >= {need}:1.",
            "  Αν το background είναι ανοιχτό, σκούρυνε το foreground· αν σκούρο, φώτισέ το.",
            "  ΜΗΝ αλλάξεις κανένα άλλο token, καμία απόχρωση, καμία διάταξη.",
            "",
        ]
    return "\n".join(out)


def _render_prescription(vit: dict[str, Any], orig_images: int,
                         component: str = "") -> str:
    """Μηχανικά ευρήματα απόδοσης, ένα ανά γραμμή, με μετρημένο μέγεθος.

    ΟΧΙ αισθητική κρίση: μόνο μετρήσιμα σφάλματα που το μοντέλο μπορεί να
    διορθώσει τοπικά. Η ομορφιά και η πιστότητα μένουν στον validator.
    """
    out: list[str] = []
    for label, w in (("desktop", 1440), ("mobile", 390)):
        m = vit.get(label) or {}
        if "fail" in m or not m:
            out.append(f"{label.upper()} {w}: η σελίδα δεν αποδόθηκε — {m.get('fail', 'άγνωστο')}")
            continue
        if m.get("overflow", 0) > 0:
            out.append(f"{label.upper()} {w} FAIL: η σελίδα κυλά οριζόντια κατά "
                       f"{m['overflow']}px. Περιόρισε το πλάτος του υπεύθυνου στοιχείου.")
        for item in (m.get("clipped") or []):
            out.append(clip_finding(item, label, w, component)[1])
        for item in (m.get("innerOverflow") or []):
            out.append(f"{label.upper()} {w} FAIL: {item} — το στοιχείο ξεπερνά το "
                       "container του. Διόρθωσε ΜΟΝΟ την τοπική διάταξη αυτού του "
                       "selector (padding/width/min-width/gap). Μην αλλάξεις τη "
                       "συνολική σύνθεση της σελίδας.")
        if m.get("broken", 0) > 0:
            out.append(f"{label.upper()} {w} FAIL: {m['broken']} εικόνες δεν φορτώνουν.")
        if m.get("consoleErrors", 0) > 0:
            for s in (m.get("errorSamples") or [])[:3]:
                out.append(f"{label.upper()} {w} console error: {s[:150]}")
        if m.get("h1") != 1:
            out.append(f"{label.upper()} {w} FAIL: {m.get('h1')} × <h1>. Πρέπει ακριβώς ένα.")
        if orig_images >= 3 and m.get("images", 0) == 0:
            out.append(f"{label.upper()} {w} FAIL: το πρωτότυπο έχει {orig_images} εικόνες "
                       "και το port αποδίδει 0. Δέσε τις θέσεις εικόνας σε d.gallery.")
    return "\n".join(dict.fromkeys(out))


# ΚΑΝΟΝΑΣ: ένα theme κρίνεται ΠΑΝΤΑ με δεδομένα του επαγγέλματός του.
# Μέχρι τώρα ο worker απέδιδε το /preview/<key> με το προεπιλεγμένο demo
# (ξυλουργός) — δηλαδή έκρινε ιατρικό theme πάνω σε φωτογραφίες κουζίνας.
# Οι μετρήσεις εικόνων, ύψους και υπερχείλισης ήταν όλες σε λάθος περιεχόμενο.
VERTICAL_DEMO = {
    "medical": "physician", "dentist": "dentist", "pharmacy": "pharmacy",
    "food": "taverna", "cafe": "cafe", "retail": "retail", "beauty": "salon",
    "fitness": "gym", "property": "realestate", "hospitality": "rooms",
    "trades": "plumber", "automotive": "garage", "construction": "carpenter",
    "professional": "lawyer", "farm": "farm", "wellness": "massage",
    # Εκδοτικά/αφηγηματικά themes: ο παραγωγός είναι το demo με το πλουσιότερο
    # story στο demoData — ακριβώς ό,τι χρειάζεται ένα long-form theme για να
    # κριθεί δίκαια. Χωρίς αυτό το compass έμενε BLOCKED (fail-closed, σωστά).
    "content": "farm", "music": "salon",
}


class DemoMappingMissing(PortWorkerError):
    """Το vertical δεν έχει ρητή αντιστοίχιση σε demo business."""


def demo_for(rec: dict[str, Any]) -> str:
    """Ποιο demo business ταιριάζει στο vertical του theme.

    FAIL CLOSED: χωρίς ρητή αντιστοίχιση δεν αποδίδουμε τίποτα. Ένα σιωπηλό
    fallback στο προεπιλεγμένο demo είναι ακριβώς το σφάλμα που έκρινε ιατρικό
    theme πάνω σε φωτογραφίες κουζίνας — και το χειρότερο είδος σφάλματος,
    γιατί το QA βγαίνει πράσινο πάνω σε λάθος σενάριο.
    """
    for v in rec.get("verticals", []):
        if v in VERTICAL_DEMO:
            return VERTICAL_DEMO[v]
    raise DemoMappingMissing(
        f"DEMO_MAPPING_MISSING: τα verticals {rec.get('verticals')} δεν έχουν "
        f"αντιστοίχιση στο VERTICAL_DEMO. Πρόσθεσέ την εκεί — δεν χρησιμοποιείται "
        "ποτέ γενικό ή προηγούμενο demo ως εφεδρεία.")


def _qa_snapshot(vit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Μηχανική κατάσταση ανά viewport, για σύγκριση πριν/μετά."""
    snap: dict[str, dict[str, Any]] = {}
    for label in ("desktop", "mobile"):
        m = vit.get(label) or {}
        snap[label] = {"overflow": m.get("overflow", 0) or 0,
                       "inner": len(m.get("innerOverflow") or []),
                       "clipped": len(m.get("clipped") or []),
                       "broken": m.get("broken", 0) or 0,
                       "console": m.get("consoleErrors", 0) or 0,
                       "h1": m.get("h1")}
    return snap


def _regressions(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> list[str]:
    """Τι ΧΕΙΡΟΤΕΡΕΨΕ. Επιδιόρθωση που φτιάχνει το desktop και σπάει το mobile
    δεν είναι επιδιόρθωση — μετρήθηκε ακριβώς αυτό: mobile 0px -> +65px ενώ το
    μοντέλο κυνηγούσε ανύπαρκτο σφάλμα στο desktop."""
    out: list[str] = []
    for vp in ("desktop", "mobile"):
        b, a = before.get(vp, {}), after.get(vp, {})
        for key, label in (("overflow", "οριζόντια υπερχείλιση"),
                           ("inner", "εσωτερικές υπερχειλίσεις"),
                           ("broken", "σπασμένες εικόνες"),
                           ("console", "console errors")):
            if (a.get(key) or 0) > (b.get(key) or 0):
                out.append(f"{vp.upper()}: {label} {b.get(key)} -> {a.get(key)}")
        if b.get("h1") == 1 and a.get("h1") != 1:
            out.append(f"{vp.upper()}: h1 από 1 -> {a.get('h1')}")
    return out


def _regression_note(regressed: list[str]) -> str:
    if not regressed:
        return ""
    nl = chr(10)
    return (nl + "--- Η ΠΡΟΗΓΟΥΜΕΝΗ ΕΠΙΔΙΟΡΘΩΣΗ ΕΦΕΡΕ ΟΠΙΣΘΟΔΡΟΜΗΣΗ ---" + nl
            + nl.join(regressed) + nl
            + "Διόρθωσε το αρχικό πρόβλημα ΧΩΡΙΣ να αλλάξεις τη διάταξη που ήδη "
              "δούλευε στο άλλο viewport.")


def _contrast_only_fix(chat: Any, css_path: Path, spine_log: str,
                       res: dict[str, Any]) -> bool:
    """Στενή διόρθωση: ΜΙΑ τιμή token, καμία άλλη αλλαγή.

    Δεν ζητάμε ολόκληρο το φύλλο στυλ για έξι χαρακτήρες — αυτό μετακινούσε
    padding και πλάτη και έφερνε νέες υπερχειλίσεις σε κάθε γύρο.
    """
    css = css_path.read_text(encoding="utf-8")
    fail = cr.parse_failure(spine_log, css)
    if not fail:
        return False
    # Budget: η απάντηση είναι ~40 tokens, αλλά το v4-pro παράγει reasoning
    # tokens ΠΡΙΝ από αυτήν. Στα 400 το σώμα έβγαινε άδειο σε 4/4 κλήσεις.
    # 1500 αφήνει άνετο περιθώριο για τον συλλογισμό μιας προσαρμογής χρώματος
    # χωρίς να είναι αυθαίρετα μεγάλο.
    # ΝΤΕΤΕΡΜΙΝΙΣΤΙΚΑ, χωρίς μοντέλο. Μετρήθηκε σε τέσσερα τρεξίματα ότι το
    # μοντέλο γέμιζε κάθε budget με reasoning και επέστρεφε κενό content. Η
    # εργασία είναι αριθμητική: η απόχρωση διατηρείται εξ ορισμού, αλλάζει
    # μόνο η φωτεινότητα, με δυαδική αναζήτηση για την ΜΙΚΡΟΤΕΡΗ αλλαγή.
    record: dict[str, Any] = {"token": fail["fg_token"], "from": fail["fg_value"],
                              "was": fail["measured"], "required": fail["required"],
                              "method": "deterministic-hsl", "model_tokens": 0}
    value, err = cr.solve(fail["fg_value"], fail["bg_value"], fail["required"])
    if value is None:
        record.update(outcome=cr.NO_WRITE, error=err)
        res.setdefault("contrast_repair", []).append(record)
        return False
    ok, ratio = cr.verify(value, fail["bg_value"], fail["required"])
    record.update(to=value, now=ratio,
                  hue_before=round(cr.to_hsl(fail["fg_value"])[0]),
                  hue_after=round(cr.to_hsl(value)[0]),
                  outcome="APPLIED" if ok else cr.NO_WRITE,
                  error="" if ok else f"η τιμή δίνει {ratio}:1 < {fail['required']}:1")
    res.setdefault("contrast_repair", []).append(record)
    if not ok:
        return False
    css_path.write_text(cr.apply_token(css, fail["fg_token"], value), encoding="utf-8")
    return True


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
    tpl = SITES / "lib" / "templates" / f"{rec['component']}.jsx"
    if tpl.exists():
        # Ένα run που κόπηκε στα guards αφήνει αρχεία στον δίσκο. Αυτά ΔΕΝ είναι
        # theme — είναι απορρίμματα απορριφθείσας υποψηφιότητας. Αν τα δεχτούμε
        # ως «υπάρχον theme», κάθε επόμενη προσπάθεια γίνεται σιωπηλό SKIPPED και
        # το ελάττωμα μένει στον δίσκο για πάντα. Καθαρίζουμε και ξαναχτίζουμε.
        if rec.get("status") in ("PENDING", "FAILED"):
            for leftover in tpl.parent.glob(f"{rec['component']}.*"):
                leftover.unlink()
        else:
            return {"source_id": source_id, "status": "SKIPPED",
                    "skipped": "το theme υπάρχει ήδη"}

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
    try:
        _biz = demo_for(rec)
    except DemoMappingMissing:
        _biz = ""
    user = (_contract(rec, contract, _biz) + "\n\n=== ORIGINAL index.html ===\n" + html
            + "\n\n=== ORIGINAL CSS ===\n" + css)
    # ΔΥΟ κλήσεις, όχι μία. Μετρήθηκε: ένα ολόκληρο theme (JSX+CSS) σε ένα JSON
    # χτυπά το όριο εξόδου και κόβεται στη μέση — τρεις σερί αποτυχίες
    # «Unterminated string». Χωριστά χωρά, και το CSS γράφεται γνωρίζοντας τα
    # πραγματικά class names του JSX αντί να τα μαντεύει.
    payload: dict[str, Any] = {"files": [], "deviations": []}
    files: list[dict[str, str]] = []
    problem: str | None = None

    _step_log: list[dict[str, Any]] = res.setdefault("generation_steps", [])

    # Κάθε γύρος ξαναγράφει ΟΛΟΚΛΗΡΟ το αρχείο, οπότε μια διόρθωση που κερδήθηκε
    # σε προηγούμενο γύρο χάνεται αν δεν επαναληφθεί. Μετρήθηκε: ο guard έκοψε το
    # `d.services[].price`, το μοντέλο το αφαίρεσε — και ο ΕΠΟΜΕΝΟΣ γύρος (μόνο
    # για χρώματα) το ξαναέφερε, γιατί κανείς δεν του το ξαναείπε. Οι περιορισμοί
    # συσσωρεύονται και ταξιδεύουν με ΚΑΘΕ prompt.
    _payload_seq = [0]
    _sticky: list[str] = []

    def _remember(text: str) -> None:
        _sticky[:] = sticky_lines(_sticky, text)

    def _one(step: str, instruction: str, keep: str) -> dict[str, Any] | None:
        nonlocal problem
        for attempt in range(1 + MAX_REPAIR_ATTEMPTS):
            prompt = f"{user}\n\n=== ΒΗΜΑ: {step} ===\n{instruction}"
            if _sticky:
                prompt += ("\n\n=== ΜΟΝΙΜΟΙ ΠΕΡΙΟΡΙΣΜΟΙ (ισχύουν σε ΚΑΘΕ γύρο) ===\n"
                           + "\n".join(f"- {c}" for c in _sticky)
                           + "\nΑυτοί οι περιορισμοί έχουν ήδη απορρίψει προηγούμενη απάντηση. Μην τους παραβιάσεις ξανά, ούτε κατά λάθος.")
            if problem:
                prompt += (f"\n\n=== Η ΠΡΟΗΓΟΥΜΕΝΗ ΑΠΑΝΤΗΣΗ ΑΠΟΡΡΙΦΘΗΚΕ ===\n{problem}\n"
                           "Διόρθωσέ το και ξαναδώσε ΟΛΟΚΛΗΡΟ το αρχείο.")
            try:
                raw = chat.ask(SYSTEM, prompt, max_tokens=32000)
            except ResearchWorkerError as exc:
                problem = str(exc)[:300]
                _step_log.append({"step": step, "attempt": attempt + 1,
                                  "outcome": "GENERATION_FAILED",
                                  "reason": problem, "patch_produced": False,
                                  "applied": False})
                return None
            _payload_seq[0] += 1
            (out / f"deepseek-{_payload_seq[0]:02d}-{step}.json").write_text(raw, encoding="utf-8")
            try:
                data = json.loads(raw)
                # Κρατάμε ΜΟΝΟ το αρχείο που ζητά αυτό το βήμα.
                data["files"] = [f for f in data.get("files", [])
                                 if f.get("path", "").endswith(keep)]
                if not data["files"]:
                    raise PortWorkerError(f"το βήμα {step} δεν επέστρεψε αρχείο {keep}")
                _validate(data["files"], rec)
                problem = None
                _step_log.append({"step": step, "attempt": attempt + 1,
                                  "outcome": "SUCCESS", "reason": "",
                                  "patch_produced": True, "applied": False})
                return data
            except (json.JSONDecodeError, PortWorkerError) as exc:
                problem = str(exc)[:300]
                _step_log.append({"step": step, "attempt": attempt + 1,
                                  "outcome": "VALIDATION_FAILED",
                                  "reason": problem, "patch_produced": True,
                                  "applied": False})
                res.setdefault("repair_attempts", []).append(f"{step}: {problem}")
        _step_log.append({"step": step, "attempt": 1 + MAX_REPAIR_ATTEMPTS,
                          "outcome": "BUDGET_EXHAUSTED", "reason": problem or "",
                          "patch_produced": False, "applied": False})
        return None

    def _generate(feedback: str = "") -> bool:
        """Ένας πλήρης κύκλος JSX+CSS. Το `feedback` είναι ό,τι απέρριψαν οι
        guards ή το build — πάει αυτούσιο πίσω στο μοντέλο."""
        nonlocal payload, files
        # ΒΑΣΗ ΕΠΙΔΙΟΡΘΩΣΗΣ: το τρέχον αρχείο, όχι το πρωτότυπο.
        # Μετρήθηκε τρεις φορές: ο guard έκοβε το `d.services[].price`, ο επόμενος
        # γύρος το αφαιρούσε, κι ο μεθεπόμενος το ξανάφερνε. Ο λόγος δεν ήταν
        # απειθαρχία — το μοντέλο δεν είχε ΠΟΤΕ αντίγραφο του αρχείου. Κάθε γύρος
        # το ξαναέγραφε από το πρωτότυπο HTML, που ΕΧΕΙ τιμές. Η εντολή «μην
        # αλλάξεις τίποτε άλλο» ήταν κυριολεκτικά ανεκτέλεστη.
        base = {f["path"].rsplit(".", 1)[-1]: f["content"] for f in (files or [])}

        def _base(ext: str) -> str:
            src = base.get(ext, "")
            if not src:
                return ""
            nl = chr(10)
            return (nl + nl + "=== ΤΟ ΤΡΕΧΟΝ ΑΡΧΕΙΟ — ΞΕΚΙΝΑ ΑΠΟ ΑΥΤΟ ===" + nl + src + nl
                    + "=== ΤΕΛΟΣ ΤΡΕΧΟΝΤΟΣ ΑΡΧΕΙΟΥ ===" + nl
                    + "Επίστρεψέ το ΞΑΝΑ ΟΛΟΚΛΗΡΟ με ΜΟΝΟ τις ζητούμενες αλλαγές. "
                      "Κάθε άλλη διαφορά από το παραπάνω είναι σφάλμα.")

        extra = (f"\n\n=== Η ΠΡΟΗΓΟΥΜΕΝΗ ΠΡΟΣΠΑΘΕΙΑ ΑΠΟΡΡΙΦΘΗΚΕ ===\n{feedback}\n"
                 "Διόρθωσε ΑΚΡΙΒΩΣ αυτά. Μην αλλάξεις τίποτε άλλο.") if feedback else ""
        jsx = _one("JSX", f"Return ONLY sites/lib/templates/{rec['component']}.jsx in files[]. "
                          "Use semantic class names via the `s` import; the stylesheet comes next."
                          + extra + (_base("jsx") if feedback else ""), keep=".jsx")
        if not jsx:
            res["generation_blocked"] = "JSX: το βήμα δεν παρήγαγε έγκυρο αρχείο"
            return False
        jsx_src = jsx["files"][0]["content"]
        css = _one("CSS", f"Return ONLY sites/lib/templates/{rec['component']}.module.css in files[]. "
                          "It must style EXACTLY the class names used below and nothing else.\n"
                          "HARD RULES — μία παράβαση απορρίπτει ΟΛΟ το αρχείο:\n"
                          "  1. ΠΟΤΕ !important. Ούτε μία φορά, για κανέναν λόγο.\n"
                          "  2. CSS Modules: κάθε selector πρέπει να περιέχει τοπική κλάση. "
                          "     a:focus-visible σκέτο ΔΕΝ μεταγλωττίζεται — .root a:focus-visible.\n"
                          "  3. Κάθε χρώμα από τους 11 --vt-* ρόλους στο .root. Κανένα hex αλλού.\n"
                          "  4. Την αντίθεση τη διορθώνεις αλλάζοντας την ΤΙΜΗ του ρόλου στο "
                          "     .root — ποτέ παρακάμπτοντας ή διπλασιάζοντας κανόνα αλλού.\n"
                          + extra + (_base("css") if feedback else "")
                          + f"\n=== THE JSX YOU JUST WROTE ===\n{jsx_src}", keep=".css")
        if not css:
            # ΚΡΙΣΙΜΟ: χωρίς αυτό ο βρόχος συνέχιζε πάνω σε ΠΑΛΙΟ css και έκαιγε
            # το budget χωρίς να γράψει τίποτα. Τρία τρεξίματα έδειξαν ακριβώς
            # το ίδιο #247cff / 3.69:1 επειδή καμία συνταγή δεν έφτανε ποτέ
            # στον δίσκο, ενώ ο worker προχωρούσε σαν να έγινε repair.
            res["generation_blocked"] = ("CSS: το βήμα εξάντλησε τις απόπειρές του — "
                                         "τα προηγούμενα αρχεία ΔΕΝ είναι επιδιόρθωση")
            return False
        payload["files"] = jsx["files"] + css["files"]
        payload["deviations"] = (jsx.get("deviations") or []) + (css.get("deviations") or [])
        files = _validate(payload["files"], rec)
        return True

    # Guards ΠΡΙΝ γραφτεί οτιδήποτε στον δίσκο: ένα port με λάθος prop ή με
    # μηδέν δεμένες εικόνες δεν αξίζει καν build. Ό,τι απορρίπτουν πάει
    # αυτούσιο πίσω στο μοντέλο, μέχρι MAX_REPAIR_ATTEMPTS φορές.
    _generate()
    for _ in range(MAX_REPAIR_ATTEMPTS):
        if not files:
            break
        guard_out = run_all(files, contract, html, tuple(rec.get("allowed_labels", [])),
                              availability(_biz) if _biz else None)
        if not any(guard_out.values()):
            break
        res.setdefault("repair_attempts", []).append("guards: " + summarize(guard_out)[:400])
        _remember(summarize(guard_out))
        _generate(summarize(guard_out))
    if files:
        guard_out = run_all(files, contract, html, tuple(rec.get("allowed_labels", [])),
                              availability(_biz) if _biz else None)
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

    try:
        biz = demo_for(rec)
    except DemoMappingMissing as exc:
        _set_state(source_id, "BLOCKED", blocked_reason=str(exc))
        res.update(status="BLOCKED", reason=str(exc), demo_business=None)
        (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        return res
    res["demo_business"] = biz
    preview_path = f"preview/{rec['theme_key']}?biz={biz}"

    def _render_vitrina() -> dict[str, Any]:
        """Απόδοση Vitrina. Μέρος του ΒΡΟΧΟΥ, όχι επόμενο βήμα — αλλιώς ένα
        +10px ξεχείλισμα δεν έφτανε ποτέ στο μοντέλο."""
        if not tests.get("next_build", {}).get("passed"):
            return {"fail": "δεν εκτελέστηκε (build απέτυχε)"}
        try:
            with PreviewServer(SITES, PREVIEW_PORT) as srv:
                res["preview_server"] = {"pid": srv.proc.pid if srv.proc else None,
                                         "port": PREVIEW_PORT, "reclaimed": srv.reclaimed}
                if not srv.wait_ready(preview_path):
                    return {"fail": "ο preview server δεν απάντησε 200 εντός ορίου"}
                metrics = _render(f"http://127.0.0.1:{PREVIEW_PORT}",
                                  preview_path, "vitrina", out)
                # Ίδιος server, ίδια στιγμή: ο έλεγχος εμφάνισης χρειάζεται
                # ζωντανή σελίδα και δεν αξίζει δεύτερο σήκωμα.
                metrics["appearance"] = _appearance(rec["theme_key"], biz, PREVIEW_PORT)
                return metrics
        except PreviewServerError as exc:
            return {"fail": str(exc)}

    orig_imgs = (orig.get("desktop") or {}).get("images", 0)
    css_path = SITES / "lib" / "templates" / f"{rec['component']}.module.css"

    res["files_changed"] = _apply(files)
    res["deviations"] = payload.get("deviations", [])
    res["registered"] = _register(rec)
    tests = _suite()
    vit = _render_vitrina()

    # ΕΝΑΣ βρόχος για build ΚΑΙ απόδοση, μέσα στο ΥΠΑΡΧΟΝ budget. Ό,τι
    # επιστρέφει είναι συνταγή («κάνε αυτό»), όχι διάγνωση («κάτι φταίει»).
    theme_paths = [SITES / "lib" / "templates" / f"{rec['component']}.jsx",
                   SITES / "lib" / "templates" / f"{rec['component']}.module.css"]
    ledger = Ledger(theme_paths)
    ledger.seed(vit, {k: v["passed"] for k, v in tests.items()})
    regression_note = ""
    for attempt_no in range(1, MAX_REPAIR_ATTEMPTS + 1):
        failed = {k: v for k, v in tests.items() if not v["passed"]}
        css_text = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        parts: list[str] = []
        for k, v in failed.items():
            rx = _spine_prescription(v["log"], css_text) if k == "spine_guard" else ""
            parts.append(rx or _actionable(k, v["log"]))
        render_rx = _render_prescription(vit, orig_imgs, rec["component"])
        app = vit.get("appearance") or {}
        if app and not app.get("passed", True):
            parts.append("--- ΕΜΦΑΝΙΣΗ ΣΕ ΠΡΑΓΜΑΤΙΚΟ BROWSER ---\n" + "\n".join(app.get("problems") or []) + "\nΑΟΡΑΤΟ ΚΕΙΜΕΝΟ: δώσε χρώμα που διαβάζεται πάνω στο ΠΡΑΓΜΑΤΙΚΟ φόντο του στοιχείου· πρόσεξε την ΕΙΔΙΚΟΤΗΤΑ — `.root a` (0,2,0) υπερισχύει του `.heroButton` (0,1,0), γι' αυτό τα resets γράφονται `.root :where(a)`.\nΓΡΑΜΜΑΤΟΣΕΙΡΑ: μόνο όσες δηλώνει το συμβόλαιο ως self-hosted.")
        if render_rx:
            parts.append("--- ΜΗΧΑΝΙΚΑ ΕΥΡΗΜΑΤΑ ΑΠΟΔΟΣΗΣ ---\n" + render_rx)
        if not parts:
            break

        res.setdefault("repair_attempts", []).append(
            ("build: " + ", ".join(failed) if failed else "") +
            (" · render" if render_rx else ""))
        _generate("\n\n".join(parts))
        if not files:
            break
        guard_out = run_all(files, contract, html, tuple(rec.get("allowed_labels", [])),
                              availability(_biz) if _biz else None)
        res["guards"] = guard_out
        if any(guard_out.values()):
            _set_state(source_id, "FAILED", failure="guards μετά από repair")
            res.update(status="FAILED", reason="guards: " + summarize(guard_out)[:400])
            (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
            return res
        # ΔΡΟΜΟΛΟΓΗΣΗ: η διόρθωση αντίθεσης δεν εξαρτάται από ευρήματα διάταξης.
        # Η προηγούμενη συνθήκη απαιτούσε τελείως καθαρή απόδοση, που δεν συνέβη
        # ποτέ — οπότε η στενή διαδρομή δεν ενεργοποιήθηκε καμία φορά. Τα
        # ευρήματα απόδοσης έχουν τη δική τους διαδρομή· δεν μπλοκάρουν αυτή.
        narrow = False
        if not tests.get("spine_guard", {}).get("passed", True):
            narrow = _contrast_only_fix(chat, theme_paths[1],
                                        tests["spine_guard"]["log"], res)
        if not narrow:
            res["files_changed"] = _apply(files)
        tests = _suite()
        vit = _render_vitrina()
        app_ok = (vit.get("appearance") or {}).get("passed", False)
        gates_ok = all(v["passed"] for v in tests.values()) and app_ok
        verdict = ledger.judge(attempt_no, vit,
                               {k: v["passed"] for k, v in tests.items()}, gates_ok)
        res["repair_ledger"] = ledger.report()
        if verdict.decision == "REJECTED":
            # ΣΥΝΑΛΛΑΚΤΙΚΟ ΟΡΙΟ: ο απορριφθείς υποψήφιος ΔΕΝ γίνεται είσοδος για
            # την επόμενη απόπειρα. Τα αρχεία επανήλθαν· ξαναμετράμε από το
            # αποδεκτό ώστε ο επόμενος γύρος να κρίνεται σε πραγματική βάση.
            tests = _suite()
            vit = _render_vitrina()
        regression_note = _regression_note(verdict.regressions)

    res["tests_run"] = len(tests)
    res["tests_passed"] = sum(1 for t in tests.values() if t["passed"])
    res["tests_failed"] = res["tests_run"] - res["tests_passed"]
    res["tests"] = {k: {"passed": v["passed"]} for k, v in tests.items()}
    (out / "test-logs.json").write_text(json.dumps(tests, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- 4. Απόδοση Vitrina — μέρος του worker, όχι χειροκίνητο βήμα.
    # Στο πρώτο proof το έκανα με το χέρι· έτσι ο worker δήλωνε
    # READY_FOR_REVIEW χωρίς να έχει δει ποτέ τη δική του σελίδα.
    if any(a.decision == "REJECTED" for a in ledger.attempts) and             ledger.attempts[-1].decision == "REJECTED":
        res["rollback_final"] = ledger.rollback_to_accepted()
        tests = _suite()
        vit = _render_vitrina()
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
    _app = vit.get("appearance") or {}
    res["appearance"] = {k: _app.get(k) for k in ("passed", "problems")}
    if not _app.get("passed", False):
        render_problems.append("εμφάνιση: " + ("; ".join(_app.get("problems") or [])
                                               or "ο έλεγχος δεν ολοκληρώθηκε"))
    for label in ("desktop", "mobile"):
        m = vit.get(label) or {}
        if "fail" in m or not m:
            render_problems.append(f"{label}: δεν αποδόθηκε")
            continue
        if m.get("overflow", 0) > 0:
            render_problems.append(f"{label}: οριζόντια υπερχείλιση {m['overflow']}px")
        if m.get("innerOverflow"):
            render_problems.append(f"{label}: εσωτερική υπερχείλιση — {', '.join(m['innerOverflow'][:3])}")
        for item in (m.get("clipped") or [])[:3]:
            kind, _ = clip_finding(item, label, 1440 if label == "desktop" else 390,
                                   rec["component"])
            lost = " · ".join(c["text"] for c in item.get("cut", []))
            render_problems.append(
                f"{label}: αποκομμένο περιεχόμενο [{kind}] .{item.get('sel')} — "
                f"{item.get('hidden')}px κρυμμένα ({lost})")
            if kind == "BLOCKED_SHARED_COMPONENT":
                res.setdefault("shared_component_blockers", []).append(
                    {"viewport": label, "selector": item.get("sel"),
                     "owner": item.get("owner")})
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
