#!/usr/bin/env python3
"""Ενσωμάτωση της εγκεκριμένης αρχικής στην παραγωγή.

    python scripts/integrate_homepage.py

Πηγή : research/homepage-redesign/homepage-full.html  (24/24 στην ταυτοποίηση)
Στόχος: web/index.html + web/shots/

Δεν αλλάζει τίποτα στο σχέδιο. Προσθέτει μόνο ό,τι χρειάζεται η παραγωγή:
self-hosted γραμματοσειρά, λογότυπο, SEO, και σύνδεση του input με το
πραγματικό onboarding (`start.html?text=`).
"""
from __future__ import annotations

import io
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research" / "homepage-redesign" / "homepage-full.html"
WEB = ROOT / "web"
DEST = WEB / "index.html"

TITLE = "Vitrina — Φτιάχνουμε το site. Εσύ ασχολείσαι με την επιχείρησή σου."
DESC = ("Επαγγελματική ιστοσελίδα για ελληνικές επιχειρήσεις: σχέδιο ανά επάγγελμα, "
        "φιλοξενία, local SEO και απεριόριστες αλλαγές. €14,99/μήνα, πρώτος μήνας δωρεάν.")

HEAD = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://getvitrina.gr/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://getvitrina.gr/">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="https://getvitrina.gr/cover-facebook.png">
<meta property="og:locale" content="el_GR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="favicon-180.png">
<meta name="theme-color" content="#FBFAF7">'''

# Το λογότυπο: σήμα βιτρίνας + wordmark. Η γεωμετρία (2.4 περίγραμμα / 2.4
# μοντάζ σε 20 τετράγωνο) είναι αυτή που επιβίωσε στη δοκιμή απόδοσης 1x.
LOGO = '''<span class="logo" aria-label="Vitrina">
      <svg class="logo-mark" viewBox="0 0 22 28" width="17" height="22" aria-hidden="true" focusable="false">
        <rect x="1.2" y="4" width="19.6" height="20" rx="4.5" fill="none" stroke="currentColor" stroke-width="2.4"/>
        <rect x="9.8" y="4" width="2.4" height="20" fill="currentColor"/>
      </svg>vitrina</span>'''

LOGO_CSS = '''
  /* ── λογότυπο ── */
  .logo{ display:inline-flex; align-items:center; gap:8px; }
  .logo-mark{ flex:none; display:block; }
  @media (max-width:899px){ .logo-mark{ width:15px; height:19px; } }
'''

# Το input οδηγεί στο πραγματικό onboarding. Ίδιο συμβόλαιο με τη σελίδα που
# αντικαθιστά: start.html διαβάζει URLSearchParams.get('text').
FORM_JS = '''
  /* ── Το brief πάει στο πραγματικό onboarding ──────────────────────────
     Ίδιο συμβόλαιο με την προηγούμενη αρχική: start.html?text=…
     Καμία υπόσχεση αυτόματης δημιουργίας — απλή μεταφορά του κειμένου. */
  (function () {
    var form = document.getElementById('brief-form')
    if (!form) return
    form.setAttribute('action', 'start.html')
    form.setAttribute('method', 'get')
    form.addEventListener('submit', function (e) {
      e.preventDefault()
      var t = document.getElementById('brief')
      var v = (t.value || '').trim()
      if (!v) { t.focus(); return }
      window.location.href = 'start.html?text=' + encodeURIComponent(v)
    })
  })()
'''


def main() -> None:
    src = io.open(SRC, encoding="utf-8").read()

    # 1. assets
    shots_dst = WEB / "shots"
    shots_dst.mkdir(exist_ok=True)
    used = sorted(set(re.findall(r'src="shots/([\w.-]+\.jpg)"', src)))
    for f in used:
        shutil.copy2(SRC.parent / "shots" / f, shots_dst / f)

    # 2. head: αντικατάσταση του Google Fonts link με self-hosted @font-face
    face = io.open(WEB / "fonts" / "manrope.css", encoding="utf-8").read()
    out = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", src)
    out, n = re.subn(r'<link rel="stylesheet"[^>]*fonts\.googleapis[^>]*>', "", out)
    assert n == 1, f"δεν βρέθηκε το Google Fonts link ({n})"
    assert "googleapis" not in out and "gstatic" not in out, "έμεινε αναφορά σε Google Fonts"

    out = re.sub(r"<style>", "<style>\n" + face + LOGO_CSS, out, count=1)

    # 3. head tags
    out = re.sub(r'<meta charset="[^"]*">', "", out, count=1)
    out = re.sub(r'<meta name="viewport"[^>]*>', "", out, count=1)
    out = re.sub(r"<title>.*?</title>", "", out, count=1, flags=re.S)
    out = re.sub(r'<meta name="description"[^>]*>', "", out, count=1)
    out = re.sub(r"<head>", "<head>\n" + HEAD, out, count=1)
    assert out.count("<title>") == 1, "διπλό <title>"

    # 4. λογότυπο στο header
    out, n = re.subn(r'<span class="logo">vitrina</span>', LOGO, out, count=1)
    assert n == 1, "δεν βρέθηκε το wordmark του header"

    # 5. σύνδεση με onboarding
    out = re.sub(r"</body>", "<script>\n" + FORM_JS + "\n</script>\n</body>", out, count=1)

    # 6. εγγυήσεις: τίποτα δεν άλλαξε στο κλειδωμένο hero
    for frag in ("Φτιάχνουμε το site.", "Εσύ ασχολείσαι με", "Πες μας με δυο λόγια τι κάνεις",
                 "κομμωτήριο στη Γλυφάδα", "Δείξε μου", "Πραγματικά site που φτιάξαμε",
                 "translateY(-11px) scale(1.08)", "data-pan", "rotator",
                 "#E85D3F", "14,99", "Έξι επιχειρήσεις", "Τι αναλαμβάνουμε",
                 "Πώς γίνεται", "hello@getvitrina.gr"):
        assert frag in out, f"ΧΑΘΗΚΕ: {frag}"
    assert not re.search(r"font-weight:\s*[89]00", out), "εμφανίστηκε βάρος 800/900"
    assert "4F39F6" not in out.upper(), "εμφανίστηκε indigo"

    io.open(DEST, "w", encoding="utf-8").write(out)
    print(f"OK -> web/index.html  {len(out.encode('utf-8')) // 1024} KB")
    print(f"     web/shots/       {len(used)} αρχεία")


if __name__ == "__main__":
    main()
