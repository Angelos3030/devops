#!/usr/bin/env python3
"""Υλοποίηση της νέας δημόσιας αρχικής, από εγκεκριμένη καλλιτεχνική διεύθυνση.

    python scripts/kimi_homepage.py

Απομονωμένο πρωτότυπο για έγκριση — ΔΕΝ αντικαθιστά τη σελίδα παραγωγής.

Το μοντέλο δεν βλέπει: τη σημερινή αρχική, themes πελατών, components ή tokens
του Vitrina. Βλέπει τη διεύθυνση, τα αληθινά γεγονότα και τα τεχνικά όρια.

Αυτοτελές επίτηδες: η παλιά μηχανή benchmark διαγράφηκε και δεν αναστήθηκε.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "research" / "homepage-redesign"
PREVIEW = "https://sites-production-da56.up.railway.app/preview"
BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3"
# Υψηλή προσπάθεια συλλογισμού. Αν το API δεν τη δέχεται, ο έλεγχος σύνδεσης
# παρακάτω τη δείχνει με το ακριβές μήνυμα και σταματάμε — καμία τυφλή
# επανάληψη με άλλες παραμέτρους.
REASONING_EFFORT = "high"
FENCE = re.compile(r"^```[a-z]*\n?|```$", re.M)

SYSTEM = """Είσαι senior front-end designer. Υλοποιείς μια ΕΓΚΕΚΡΙΜΕΝΗ
καλλιτεχνική διεύθυνση για δημόσια αρχική σελίδα προϊόντος — δεν την ξαναγράφεις.

Ο ρόλος σου: να την κάνεις να δουλέψει σε αληθινό browser, παίρνοντας αποφάσεις
υλοποίησης (ακριβή μεγέθη, αποστάσεις, breakpoints, τεχνική κίνησης) χωρίς να
επιστρέψεις την ιδέα σε γενικό μοτίβο.

ΑΠΑΓΟΡΕΥΟΝΤΑΙ ΡΗΤΑ — είναι το προεπιλεγμένο μοτίβο και δεν το θέλουμε:
κεντραρισμένος τίτλος με κουμπί από κάτω · ατέλειωτα πλέγματα από feature cards ·
τρεις ίδιες κάρτες σε σειρά · εικονίδιο + τίτλος + παράγραφος επαναλαμβανόμενα ·
γιγάντιες χρωματικές κηλίδες · μοβ/μπλε διαβαθμίσεις «AI startup» ·
glassmorphism παντού · υπερβολικά στρογγυλεμένα «χάπια» · κάθε ενότητα μέσα σε
στρογγυλεμένο κουτί · αυθαίρετα mockup dashboard · διακοσμητικά αστεράκια AI ·
ίδιος ρυθμός σε όλες τις ενότητες.

ΑΠΑΡΑΒΑΤΟ ΟΡΙΟ ΑΛΗΘΕΙΑΣ: χρησιμοποίησε ΜΟΝΟ τα γεγονότα που σου δίνονται. Μην
επινοήσεις αριθμό πελατών, ποσοστά, κριτικές, αξιολογήσεις, βραβεία,
αποτελέσματα, ενσωματώσεις ή λειτουργίες. Μην υπονοήσεις ότι δημιουργείται site
αυτόματα σε πραγματικό χρόνο — δεν υπάρχει τέτοια λειτουργία σήμερα."""

STEP1 = """=== ΒΗΜΑ 1 ΑΠΟ 2: Η ΔΟΜΗ ===

Δώσε το σημασιολογικό HTML — ΧΩΡΙΣ CSS, χωρίς <style>. Τα class names δικά σου.
Συμπεριέλαβε το inline <script> της εναλλαγής παραδείγματος αν το χρειάζεσαι.
Η διαίρεση είναι μηχανική: σελίδα και φύλλο στυλ μαζί δεν χωρούν σε μία απάντηση.

Απάντησε ΜΟΝΟ με JSON:
{"body": "…", "head_extra": "<link…> γραμματοσειρές", "title": "…",
 "how_direction_realised": "πώς υλοποιείς το κατώφλι, την υπογραφή και τον δρόμο"}"""

STEP2 = """=== ΒΗΜΑ 2 ΑΠΟ 2: ΤΟ ΣΤΙΛ ===

Ολόκληρο το CSS για τη δομή σου: 1440 και 390 ως σκόπιμες συνθέσεις, το κατώφλι,
το φως, ο δρόμος των βιτρινών, τα micro-interactions, `prefers-reduced-motion`,
ορατό focus.

Απάντησε ΜΟΝΟ με JSON:
{"css": "…", "interactions": ["…"], "showcase_behaviour": "…", "mobile_notes": "…"}"""


def _key() -> str:
    """Το κλειδί ζει ΜΟΝΟ στο .env — ποτέ σε argument, log ή commit."""
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^KIMI_API_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("Λείπει το KIMI_API_KEY από το .env")


def as_json(text: str) -> dict:
    """Το stream δίνει σκέτο κείμενο· απομονώνουμε το JSON σώμα."""
    text = FENCE.sub("", text.strip()).strip()
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        raise SystemExit("δεν βρέθηκε JSON στην απάντηση")
    return json.loads(text[i:j + 1])


def ask(key: str, user: str, deadline: float,
        max_tokens: int = 64000, attempt: int = 0) -> tuple[str, dict, dict]:
    """Streaming, ΜΙΑ απόπειρα, σκληρό όριο τοίχου.

    Χωρίς stream το `timeout` μετρά αναμονή για ΠΡΩΤΟ byte και η κλήση πεθαίνει
    ενώ το μοντέλο ακόμη συλλογίζεται — μετρήθηκε σε δύο αποτυχίες των 900s.
    """
    payload = {
        "model": MODEL, "temperature": 1, "max_tokens": max_tokens,
        "stream": True, "stream_options": {"include_usage": True},
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user}],
    }
    if REASONING_EFFORT:
        payload["reasoning_effort"] = REASONING_EFFORT
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "text/event-stream"})
    t0 = time.time()
    chunks: list[str] = []
    usage: dict = {}
    finish = "unknown"
    timing: dict = {"ttft": None}
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            for line in resp:
                if time.time() > deadline:
                    finish = "deadline"
                    break
                s = line.decode("utf-8", "replace").strip()
                if not s.startswith("data:"):
                    continue
                data = s[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    ev = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if ev.get("usage"):
                    usage = ev["usage"]
                for ch in ev.get("choices", []):
                    piece = (ch.get("delta") or {}).get("content") or ""
                    if piece:
                        if timing["ttft"] is None:
                            timing["ttft"] = round(time.time() - t0, 1)
                        chunks.append(piece)
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        # 429 = προσωρινή υπερφόρτωση, η ίδια η υπηρεσία λέει «ξαναδοκίμασε».
        # Διαφέρει ουσιωδώς από απόρριψη παραμέτρου ή μοντέλου, που σημαίνει ότι
        # η ρύθμισή μας είναι λάθος και καμία επανάληψη δεν θα τη σώσει.
        if exc.code == 429 and attempt == 0:
            print(f"  429 υπερφόρτωση — αναμονή 45s και ΜΙΑ επανάληψη", flush=True)
            time.sleep(45)
            return ask(key, user, deadline, max_tokens, attempt=1)
        raise SystemExit(f"HTTP {exc.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        finish = f"transport: {str(exc)[:80]}"
    timing.update(total=round(time.time() - t0, 1), finish_reason=finish,
                  chars=sum(map(len, chunks)))
    return "".join(chunks), usage, timing


def brief() -> str:
    direction = (OUT / "ART_DIRECTION.md").read_text(encoding="utf-8")
    return f"""{direction}

=== ΤΑ ΑΛΗΘΙΝΑ ΓΕΓΟΝΟΤΑ (μόνο αυτά) ===

Προϊόν: Vitrina — getvitrina.gr · hello@getvitrina.gr
Τι είναι: φτιάχνουμε και συντηρούμε την online παρουσία μικρών ελληνικών
επιχειρήσεων. Ο πελάτης περιγράφει τι κάνει· εμείς αναλαμβάνουμε τη δουλειά.

Τιμή: €14.99/μήνα. Πρώτος μήνας δωρεάν. Ακύρωση όποτε θέλεις, χωρίς δέσμευση.
Περιλαμβάνονται: φιλοξενία, local SEO, απεριόριστες αλλαγές.
Προαιρετικά: .gr domain €24/έτος, με πλήρη τεχνική ρύθμιση (DNS, SSL, Cloudflare).

Νομικές σελίδες που υπάρχουν: privacy.html · terms.html · refunds.html ·
data-deletion.html

Κύρια διατύπωση, ΜΗΝ την αντικαταστήσεις με γενικόλογα:
  «Η επιχείρησή σου αξίζει καλύτερη βιτρίνα.»
  «Πες μας τι κάνεις. Εμείς αναλαμβάνουμε την online παρουσία σου.»

=== ΤΑ ΕΞΙ ΠΡΑΓΜΑΤΙΚΑ SITE ===

Χρησιμοποιείς ΣΤΙΓΜΙΟΤΥΠΑ, όχι iframe. Ο preview server επιστρέφει
`x-frame-options: SAMEORIGIN` — επαληθεύτηκε — οπότε κάθε iframe βγαίνει ΚΕΝΟ.
Τα στιγμιότυπα είναι αληθινές λήψεις των ζωντανών site, 1280x900.

  εικόνα                | επάγγελμα                | σύνδεσμος
  shots/salon.jpg       | Κομμωτήριο · Γλυφάδα     | {PREVIEW}/beauty-atelier?biz=salon
  shots/taverna.jpg     | Ταβέρνα · Θεσσαλονίκη    | {PREVIEW}/warmth?biz=taverna
  shots/dentist.jpg     | Οδοντιατρείο · Χαλάνδρι  | {PREVIEW}/clinic-triage?biz=dentist
  shots/plumber.jpg     | Υδραυλικός · Περιστέρι   | {PREVIEW}/callout?biz=plumber
  shots/cafe.jpg        | Καφέ & φούρνος           | {PREVIEW}/bakery-editorial?biz=cafe
  shots/rooms.jpg       | Ενοικιαζόμενα δωμάτια    | {PREVIEW}/aegean?biz=rooms

Κάθε `<img>`: `width="1280" height="900"`, `loading="lazy"`, `decoding="async"`
και περιγραφικό `alt`. Το ΠΡΩΤΟ (μέσα στο hero preview) ΧΩΡΙΣ lazy — φαίνεται
αμέσως. Κάθε παράδειγμα είναι και σύνδεσμος που ανοίγει το ζωντανό site σε νέα
καρτέλα (`target="_blank" rel="noopener"`).

ΤΟ HERO PREVIEW: μεγάλο πλαίσιο τύπου browser με τις ΤΕΣΣΕΡΙΣ επιλογές
(Κομμωτήριο · Ταβέρνα · Οδοντιατρείο · Υδραυλικός). Η επιλογή αλλάζει την εικόνα
μέσα στο πλαίσιο με ομαλή μετάβαση. Και οι τέσσερις εικόνες υπάρχουν στο DOM· η
εναλλαγή γίνεται με κλάση, ώστε να μη «σπάει» χωρίς JavaScript.

Σήμανε ρητά ότι πρόκειται για **παράδειγμα** — δεν είναι το site του επισκέπτη
και δεν δημιουργείται τίποτα εκείνη τη στιγμή.

=== ΤΕΧΝΙΚΕΣ ΑΠΑΙΤΗΣΕΙΣ ===

Ένα αυτοτελές HTML με ενσωματωμένο <style>. Χωρίς frameworks, χωρίς build.
Γραμματοσειρές: Google Fonts με <link> — **Manrope** (400, 500, 800), με
ελληνικό subset.

JavaScript: λίγες γραμμές inline για την εναλλαγή του hero preview και για τις
αποκαλύψεις ενοτήτων (IntersectionObserver). Η σελίδα πρέπει να παραμένει
πλήρως κατανοητή και χωρίς JS.

Responsive: 1440 και 390 ως ΔΥΟ σκόπιμες συνθέσεις. Στα 390 καμία οριζόντια
κύλιση, στόχοι αφής ≥44px, σταθερή ράβδος ενέργειας στον πάτο.

Προσβασιμότητα: σημασιολογικό HTML, ΕΝΑ <h1>, αντίθεση κειμένου ≥4.5:1 για κάθε
κείμενο, κουμπί και σύνδεσμο πάνω στο πραγματικό του φόντο, ορατό focus,
`@media (prefers-reduced-motion: reduce)` που μηδενίζει την κίνηση.

Γλώσσα: ελληνικά. `<html lang="el">`."""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    key, base = _key(), brief()
    deadline = time.time() + 1800
    t0 = time.time()

    raw1, u1, t1 = ask(key, base + "\n\n" + STEP1, deadline)
    print("ΒΗΜΑ 1:", json.dumps(t1, ensure_ascii=False), flush=True)
    (OUT / "step1.txt").write_text(raw1, encoding="utf-8")
    d1 = as_json(raw1)
    body = d1.get("body", "")
    if "<" not in body:
        raise SystemExit("το βήμα 1 δεν επέστρεψε δομή")

    raw2, u2, t2 = ask(key, base + "\n\n" + STEP2 + "\n\n=== Η ΔΟΜΗ ΣΟΥ ===\n" + body,
                       deadline)
    print("ΒΗΜΑ 2:", json.dumps(t2, ensure_ascii=False), flush=True)
    (OUT / "step2.txt").write_text(raw2, encoding="utf-8")
    d2 = as_json(raw2)
    css = d2.get("css", "")
    if not css.strip():
        raise SystemExit("το βήμα 2 δεν επέστρεψε CSS")

    html = ("<!doctype html>\n<html lang=\"el\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{d1.get('title', 'Vitrina')}</title>\n{d1.get('head_extra', '')}\n"
            f"<style>\n{css}\n</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n")
    (OUT / "homepage.html").write_text(html, encoding="utf-8")

    meta = {"model": MODEL, "bytes": len(html.encode("utf-8")),
            "runtime_total": round(time.time() - t0, 1),
            "timing": {"step1": t1, "step2": t2},
            "usage": {k: u1.get(k, 0) + u2.get(k, 0)
                      for k in ("prompt_tokens", "completion_tokens")},
            "how_direction_realised": d1.get("how_direction_realised"),
            "interactions": d2.get("interactions"),
            "showcase_behaviour": d2.get("showcase_behaviour"),
            "mobile_notes": d2.get("mobile_notes")}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                   encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("bytes", "runtime_total", "usage")},
                     ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
