#!/usr/bin/env python3
"""Site ξυλουργού από εγκεκριμένη καλλιτεχνική διεύθυνση — με Kimi.

    python scripts/kimi_carpenter.py

Ίδιο πρωτόκολλο με το `kimi_homepage.py`: δύο βήματα (δομή, μετά στιλ), υψηλή
προσπάθεια συλλογισμού, streaming με σκληρό όριο τοίχου, κλειδί μόνο από `.env`.

Απομονωμένο πρωτότυπο για έγκριση — ΔΕΝ αντικαθιστά theme παραγωγής και ΔΕΝ
αγγίζει το ζωντανό site του πελάτη.

Το μοντέλο ΔΕΝ βλέπει: τον κώδικα του Vitrina, υπάρχοντα themes, tokens, ούτε
το site αναφοράς. Βλέπει τη ΔΙΕΥΘΥΝΣΗ (μετρημένη από εμάς), τα ΑΛΗΘΙΝΑ γεγονότα
του πελάτη και τα ΤΕΧΝΙΚΑ ΟΡΙΑ. Έτσι παράγει δική του υλοποίηση αντί να
αντιγράψει ξένη σελίδα.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "koutrakis-redesign-v3"
BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3"
REASONING_EFFORT = "high"
FENCE = re.compile(r"^```[a-z]*\n?|```$", re.M)
WALL = 1500  # δευτερόλεπτα συνολικά· το βήμα 2 παίρνει ό,τι περισσέψει

SYSTEM = """Είσαι senior front-end designer. Υλοποιείς μια ΕΓΚΕΚΡΙΜΕΝΗ
καλλιτεχνική διεύθυνση για site μικρής ελληνικής επιχείρησης — δεν την ξαναγράφεις.

Ο ρόλος σου: να την κάνεις να δουλέψει σε αληθινό browser, παίρνοντας αποφάσεις
υλοποίησης (ακριβή μεγέθη, αποστάσεις, breakpoints, ρυθμό) χωρίς να επιστρέψεις
την ιδέα σε γενικό μοτίβο.

ΑΠΑΓΟΡΕΥΟΝΤΑΙ ΡΗΤΑ — είναι το προεπιλεγμένο μοτίβο και δεν το θέλουμε:
κεντραρισμένος τίτλος με κουμπί από κάτω · πλέγματα από feature cards · τρεις
ίδιες κάρτες σε σειρά · εικονίδιο + τίτλος + παράγραφος επαναλαμβανόμενα ·
σκούρο πέπλο πάνω από κάθε φωτογραφία · μοβ/μπλε διαβαθμίσεις · glassmorphism ·
υπερβολικά στρογγυλεμένα «χάπια» · κάθε ενότητα μέσα σε στρογγυλεμένο κουτί ·
διακοσμητικά εικονίδια που δεν λένε τίποτα · ίδιος ρυθμός σε όλες τις ενότητες ·
οριζόντιο scroll για το κύριο περιεχόμενο.

ΑΠΑΡΑΒΑΤΟ ΟΡΙΟ ΑΛΗΘΕΙΑΣ: χρησιμοποίησε ΜΟΝΟ τα γεγονότα που σου δίνονται. Μην
επινοήσεις χρόνια εμπειρίας, αριθμό έργων, πιστοποιήσεις, βραβεία, κριτικές,
αξιολογήσεις, τιμές, εγγυήσεις ή συνεργασίες. Αν δεν σου δόθηκε, ΔΕΝ υπάρχει."""

DIRECTION = """=== ΕΓΚΕΚΡΙΜΕΝΗ ΔΙΕΥΘΥΝΣΗ — ΨΗΦΙΔΩΤΟ ΠΑΝΕΛ, ΜΕΤΡΗΜΕΝΟ ===

ΠΡΟΣΟΧΗ: ΔΕΝ είναι κεντραρισμένο container με αέρα. Είναι ΠΥΚΝΟ ΨΗΦΙΔΩΤΟ από
πάνελ κολλητά μεταξύ τους, από άκρη σε άκρη της οθόνης, ΧΩΡΙΣ περιθώρια
σελίδας και ΧΩΡΙΣ κενά ανάμεσα στα πάνελ. Το λευκό εμφανίζεται ως ΠΑΝΕΛ, όχι
ως φόντο που περιβάλλει τα πάντα.

ΑΚΡΙΒΗΣ ΑΚΟΛΟΥΘΙΑ (πλάτη ως ποσοστό του viewport, ύψη ενδεικτικά για 1440px):

 1. HERO — 100% πλάτος, ύψος όλο το viewport. Φωτογραφία. ΜΗΔΕΝ κείμενο από
    πάνω. Μόνο όνομα πάνω αριστερά, μενού δεξιά, κυκλικό βελάκι κάτω κεντρικά.
 2. ΛΕΥΚΗ ΖΩΝΗ — 100% πλάτος, ~280px. Μέσα: h1 μικρό (25px/500/#333) και από
    κάτω η μεγάλη γκρι εισαγωγή (30px/300/line-height 45px/#666).
 3. ΣΧΙΣΗ 60/40 — αριστερά ΦΩΤΟΓΡΑΦΙΑ πλάτους 60%, δεξιά ΚΕΙΜΕΝΟ 40% σε λευκό.
    Το κείμενο έχει ΚΕΦΑΛΑΙΑ ετικέτα (22px/700/#000) και παράγραφο 300 weight.
    Κάτω δεξιά στο κείμενο, ΚΥΚΛΙΚΟ ΒΕΛΑΚΙ (→) ως ενέργεια.
 4. ΤΕΣΣΕΡΙΣ ΣΤΗΛΕΣ — τέσσερα πάνελ από 25% το καθένα, ύψος ~270px, κολλητά.
    Χρώματα με αυτή τη σειρά: #DEC098, #E2DAD3, #E8E8E8, #F8F4F1.
    Σε κάθε ένα: μικρή ΚΕΦΑΛΑΙΑ επικεφαλίδα και δύο σειρές κειμένου.
 5. ΛΩΡΙΔΑ ΤΡΙΩΝ ΕΙΚΟΝΩΝ — τρεις φωτογραφίες πλάτους 30% η καθεμία, ύψος
    ~357px, με ΚΕΦΑΛΑΙΑ ετικέτα ΠΑΝΩ από κάθε εικόνα. Φόντο ζώνης λευκό.
 6. ΣΧΙΣΗ 33/67 — αριστερά ΚΕΙΜΕΝΟ 33%, δεξιά ΦΩΤΟΓΡΑΦΙΑ 67%. (Αντίστροφα
    από το βήμα 3 — η εναλλαγή πλευράς είναι σκόπιμη.)
 7. ΜΠΕΖ ΖΩΝΗ #E2DAD3 — 100% πλάτος, ~860px. Μέσα της: λωρίδα με ΔΥΟ εικόνες
    24% και από κάτω λωρίδα με ΤΡΕΙΣ εικόνες 24%, όλες με ΚΕΦΑΛΑΙΑ ετικέτα.
 8. ΤΡΕΙΣ ΣΧΙΣΕΙΣ 50/50 — εναλλάξ: εικόνα αριστερά/κείμενο δεξιά · κείμενο
    αριστερά/εικόνα δεξιά · εικόνα αριστερά/κείμενο δεξιά.
 9. ΣΚΟΥΡΑ ΖΩΝΗ #595959 — 100% πλάτος, ~470px, λευκό κείμενο. Κάλεσμα σε
    επικοινωνία. ΜΗΝ γράψεις χρόνια εμπειρίας ή αριθμούς — δεν τα έχουμε.
10. ΕΠΙΚΟΙΝΩΝΙΑ — τηλέφωνο, περιοχές, ωράριο. ΟΧΙ φόρμα: δεν υπάρχει backend.

ΤΥΠΟΓΡΑΦΙΑ — ΜΟΝΟ Manrope, βάρη 300/500/700
· h1 25px/500/#333 · εισαγωγή 30px/300/lh 45px/#666
· ΚΕΦΑΛΑΙΕΣ ετικέτες 22px/700/#000, γραμμένες κεφαλαία μέσα στο κείμενο
· τρέχον κείμενο 16px/300/#666

ΠΑΛΕΤΑ: #FFFFFF #000000 #666666 #333333 #DEC098 #E2DAD3 #E8E8E8 #F8F4F1
#595959 και #E09900 ΜΟΝΟ για τα κυκλικά βελάκια και τα links.

ΟΙ ΦΩΤΟΓΡΑΦΙΕΣ ΓΕΜΙΖΟΥΝ ΤΟ ΠΑΝΕΛ ΤΟΥΣ: object-fit cover, μηδέν περιθώριο,
μηδέν border-radius. Κάθε πάνελ εικόνας ακουμπά το διπλανό του."""

FACTS = """=== ΑΛΗΘΙΝΑ ΓΕΓΟΝΟΤΑ (τίποτα άλλο δεν υπάρχει) ===

Επωνυμία: Κουτράκης Κουζίνες
Αντικείμενο: ξυλουργός — κουζίνες, ντουλάπες, ειδικές ξυλουργικές κατασκευές
Έδρα: Γέρακας · εξυπηρετεί Ανατολική Αττική και Αθήνα
Τηλέφωνο: 6956297670   (διεθνής μορφή +306956297670)
Ωράριο: Δευτέρα–Σάββατο 08:00–19:00

Υπηρεσίες — ακριβώς αυτές οι τέσσερις:
1. Εντοιχισμός κουζίνας
2. Ντουλάπες & αποθήκευση
3. Ξύλινα κρεβάτια & έπιπλα
4. Μερεμέτια & λουστράρισμα

Διαδικασία — τέσσερα βήματα: Μέτρηση · Σχέδιο · Κατασκευή · Τοποθέτηση

Φωτογραφίες (χρησιμοποίησε αυτά ακριβώς τα URL, θα αντικατασταθούν αργότερα):
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/marble-kitchen.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/walnut-sideboard.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/wardrobe-built-in.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/carved-sideboard.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/rounded-cabinet.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/kids-bunk-bed.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/study-desk.jpg
https://getvitrina.gr/clients/koutrakis-xylourgos/assets/modern-kitchen.jpg

ΔΕΝ ΥΠΑΡΧΟΥΝ και δεν επινοούνται: τιμές, τιμοκατάλογος, κριτικές, αστέρια,
χρόνια εμπειρίας, αριθμός έργων, πιστοποιήσεις, εγγυήσεις, ομάδα, email,
φόρμα επικοινωνίας, online κράτηση. Η μοναδική ενέργεια είναι ΤΗΛΕΦΩΝΟ."""

LIMITS = """=== ΤΕΧΝΙΚΑ ΟΡΙΑ ===

· Αυτοτελές HTML + CSS. Καμία βιβλιοθήκη, κανένα framework, μηδέν tracking.
· Σύνθεσε σκόπιμα για 1440px και για 390px. Το tablet να μη σπάει.
· ΜΗΔΕΝ οριζόντια υπερχείλιση σε κάθε πλάτος.
· Κάθε <img> με ουσιαστικό ελληνικό alt. Lazy loading εκτός από το hero.
· Κάθε τηλέφωνο είναι <a href="tel:+306956297670">. Στο mobile, σταθερή
  μπάρα κλήσης στο κάτω μέρος που δεν κρύβει περιεχόμενο.
· Στόχοι αφής τουλάχιστον 44px.
· `prefers-reduced-motion: reduce` σέβεται· ορατό focus σε κάθε ενέργεια.
· Ένα μόνο <h1>. Σωστή ιεραρχία επικεφαλίδων.
· Γραμματοσειρά: δήλωσε Manrope με fallback· το head_extra μπορεί να φέρει
  <link> Google Fonts ΜΟΝΟ για το πρωτότυπο — στην παραγωγή γίνεται self-hosted."""

STEP1 = DIRECTION + "\n\n" + FACTS + "\n\n" + LIMITS + """

=== ΒΗΜΑ 1 ΑΠΟ 2: Η ΔΟΜΗ ===

Δώσε το σημασιολογικό HTML — ΧΩΡΙΣ CSS, χωρίς <style>. Τα class names δικά σου.
Η διαίρεση είναι μηχανική: σελίδα και φύλλο στυλ μαζί δεν χωρούν σε μία απάντηση.

Απάντησε ΜΟΝΟ με JSON:
{"body": "…", "head_extra": "<link…>", "title": "…",
 "how_direction_realised": "πώς υλοποιείς τις τέσσερις αρχές"}"""

STEP2 = """=== ΒΗΜΑ 2 ΑΠΟ 2: ΤΟ ΣΤΙΛ ===

Ολόκληρο το CSS για τη δομή σου: 1440 και 390 ως σκόπιμες συνθέσεις, η αντίστροφη
ιεραρχία τίτλου/εισαγωγής, η εναλλαγή κλίμακας στα έργα, ο αέρας,
`prefers-reduced-motion`, ορατό focus, σταθερή μπάρα κλήσης στο mobile.

Απάντησε ΜΟΝΟ με JSON:
{"css": "…", "rhythm_notes": "πώς αλλάζει ο ρυθμός ανά ενότητα",
 "mobile_notes": "…", "risks": ["…"]}"""


def _key() -> str:
    """Το κλειδί ζει ΜΟΝΟ στο .env — ποτέ σε argument, log ή commit."""
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^KIMI_API_KEY=(.*)$", line.strip())
        if m and m.group(1).strip():
            return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("Λείπει το KIMI_API_KEY από το .env")


def as_json(text: str) -> dict:
    text = FENCE.sub("", text.strip()).strip()
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        raise SystemExit(f"δεν βρέθηκε JSON στην απάντηση: {text[:200]}")
    return json.loads(text[i:j + 1])


def ask(key: str, user: str, deadline: float,
        max_tokens: int = 64000, attempt: int = 0) -> tuple[str, dict, dict]:
    """Streaming, ΜΙΑ απόπειρα, σκληρό όριο τοίχου.

    Χωρίς stream το `timeout` μετρά αναμονή για ΠΡΩΤΟ byte και η κλήση πεθαίνει
    ενώ το μοντέλο ακόμη συλλογίζεται.
    """
    payload = {
        "model": MODEL, "temperature": 1, "max_tokens": max_tokens,
        "stream": True, "stream_options": {"include_usage": True},
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user}],
    }
    if REASONING_EFFORT:
        payload["reasoning_effort"] = REASONING_EFFORT
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=json.dumps(payload).encode("utf-8"),
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
                            print(f"    πρώτο byte στα {timing['ttft']}s", flush=True)
                        chunks.append(piece)
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        if exc.code == 429 and attempt == 0:
            print("  429 υπερφόρτωση — αναμονή 45s και ΜΙΑ επανάληψη", flush=True)
            time.sleep(45)
            return ask(key, user, deadline, max_tokens, attempt=1)
        raise SystemExit(f"HTTP {exc.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        finish = f"transport: {str(exc)[:80]}"
    timing.update(total=round(time.time() - t0, 1), finish_reason=finish,
                  chars=sum(map(len, chunks)))
    return "".join(chunks), usage, timing


def main() -> int:
    key = _key()
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.time()
    deadline = start + WALL

    print("ΒΗΜΑ 1/2 — δομή", flush=True)
    raw1, usage1, t1 = ask(key, STEP1, deadline)
    print(f"  {t1['total']}s · {t1['chars']} χαρ. · finish={t1['finish_reason']}", flush=True)
    (OUT / "step1.raw.txt").write_text(raw1, encoding="utf-8")
    one = as_json(raw1)
    print(f"  υλοποίηση: {str(one.get('how_direction_realised'))[:160]}", flush=True)

    print("\nΒΗΜΑ 2/2 — στιλ", flush=True)
    user2 = (f"Η ΔΟΜΗ ΠΟΥ ΕΔΩΣΕΣ:\n{one['body']}\n\n{DIRECTION}\n\n{LIMITS}\n\n{STEP2}")
    raw2, usage2, t2 = ask(key, user2, deadline)
    print(f"  {t2['total']}s · {t2['chars']} χαρ. · finish={t2['finish_reason']}", flush=True)
    (OUT / "step2.raw.txt").write_text(raw2, encoding="utf-8")
    two = as_json(raw2)

    html = (f"<!doctype html>\n<html lang=\"el\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{one.get('title', 'Κουτράκης Κουζίνες')}</title>\n"
            f"{one.get('head_extra', '')}\n<style>\n{two['css']}\n</style>\n</head>\n"
            f"{one['body']}\n</html>\n")
    out = OUT / "prototype.html"
    out.write_text(html, encoding="utf-8")
    meta = {"model": MODEL, "reasoning_effort": REASONING_EFFORT,
            "step1": {"timing": t1, "usage": usage1},
            "step2": {"timing": t2, "usage": usage2},
            "how_direction_realised": one.get("how_direction_realised"),
            "rhythm_notes": two.get("rhythm_notes"),
            "mobile_notes": two.get("mobile_notes"), "risks": two.get("risks")}
    (OUT / "run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
    print(f"\n→ {out}  ({len(html)} bytes, συνολικά {round(time.time()-start)}s)")
    print("  Άνοιξέ το σε browser. ΔΕΝ είναι production theme μέχρι να εγκριθεί.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
