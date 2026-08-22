#!/usr/bin/env python3
"""Οι ενότητες κάτω από το πρώτο viewport, στη γλώσσα του εγκεκριμένου hero.

    python scripts/homepage_sections.py

Είσοδος:  research/homepage-redesign/hero-interactive.html  (εγκεκριμένο, δεν αγγίζεται)
Έξοδος:   research/homepage-redesign/homepage-full.html

Το hero αντιγράφεται αυτούσιο. Η μόνη δομική αλλαγή είναι ότι το
`<main class="hero">` γίνεται `<section class="hero">` μέσα σε ένα `<main>`
που τυλίγει πλέον ολόκληρη τη σελίδα — το CSS στοχεύει `.hero`, όχι `main`,
οπότε η γεωμετρία δεν αλλάζει (επαληθεύεται με diff).
"""
from __future__ import annotations

import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "homepage-redesign"
SRC = OUT / "hero-interactive.html"
DEST = OUT / "homepage-full.html"

P = "https://sites-production-da56.up.railway.app/preview/"

# Και τα έξι επαληθεύτηκαν με HTTP 200 και h1 που ταιριάζει στο screenshot.
SITES = [
    ("cafe-tall.jpg",    "Αλκυόνη",                   "Καφετέρια",               "bakery-editorial?biz=cafe"),
    ("dentist-full.jpg", "Οδοντιατρείο Παπαδοπούλου", "Οδοντιατρείο · Χαλάνδρι", "clinic-triage?biz=dentist"),
    ("taverna-full.jpg", "Ο Λεωνίδας",                "Ταβέρνα · Θεσσαλονίκη",   "warmth?biz=taverna"),
    ("plumber-full.jpg", "Υδραυλικός Νίκος",          "Υδραυλικός · Περιστέρι",  "callout?biz=plumber"),
    ("salon-full.jpg",   "Studio Μαρία",              "Κομμωτήριο · Γλυφάδα",    "beauty-atelier?biz=salon"),
    ("rooms-tall.jpg",   "Θαλασσιά",                  "Δωμάτια · Πάρος",         "aegean?biz=rooms"),
]


def portfolio_items() -> str:
    out = []
    for i, (img, name, label, href) in enumerate(SITES):
        lazy = "" if i < 2 else ' loading="lazy"'
        out.append(f'''        <a class="pf-item" href="{P}{href}" target="_blank" rel="noopener">
          <span class="pf-shot"><img src="shots/pf-{img}" width="460" height="500"
                alt="Ιστοσελίδα που φτιάξαμε — {name}"{lazy}></span>
          <span class="pf-meta">
            <span class="pf-name">{name}</span>
            <span class="pf-kind">{label}</span>
            <span class="pf-go">Δες το site ↗</span>
          </span>
        </a>''')
    return "\n".join(out)


SECTIONS = '''
  <section class="sec sec-pf" id="examples">
    <div class="sec-head">
      <h2>Έξι επιχειρήσεις, έξι διαφορετικά site.</h2>
      <p>Κανένα δεν μοιάζει με το άλλο. Κάθε ένα είναι φτιαγμένο για τη δουλειά που κάνει.</p>
    </div>
    <div class="pf-strip">
PORTFOLIO
    </div>
  </section>

  <section class="sec sec-handles" id="handles">
    <div class="sec-head">
      <h2>Τι αναλαμβάνουμε.</h2>
      <p>Τέσσερα πράγματα, και κανένα δεν πέφτει πάνω σου.</p>
    </div>

    <div class="hd hd-build">
      <div class="hd-said">
        <span class="hd-name">Κατασκευή site</span>
        <p class="hd-head">10 λεπτά από εσένα.<br>Τα υπόλοιπα από εμάς.</p>
        <p class="hd-sub">Διαλέγεις το σχέδιο που σου αρέσει, ανεβάζεις λογότυπο και
        φωτογραφίες, και μας γράφεις τις αλλαγές που θέλεις. Εμείς αναλαμβάνουμε τα υπόλοιπα.</p>
      </div>

      <div class="hd-flowwrap">
        <div class="hd-flow">
          <div class="fl">
            <span class="fl-art fl-pick" aria-hidden="true">
              <img src="shots/fan-cafe-tall.jpg" alt="">
              <img src="shots/fan-taverna-full.jpg" alt="" class="on">
              <img src="shots/fan-salon-full.jpg" alt="">
            </span>
            <span class="fl-t">Διαλέγεις σχέδιο</span>
          </div>

          <i class="fl-ar" aria-hidden="true">→</i>

          <div class="fl">
            <span class="fl-art fl-up" aria-hidden="true"><i class="lg"></i><i></i><i></i></span>
            <span class="fl-t">Ανεβάζεις λογότυπο<br>και φωτογραφίες
              <em class="fl-alt">Δεν έχεις λογότυπο; Σου φτιάχνουμε ένα.</em></span>
          </div>

          <i class="fl-ar" aria-hidden="true">→</i>

          <div class="fl">
            <span class="fl-art fl-msg">Θέλω αυτή τη φωτογραφία εδώ</span>
            <span class="fl-t">Γράφεις τις αλλαγές σου</span>
          </div>

          <div class="fl fl-end">
            <span class="fl-art fl-ok" aria-hidden="true">✓</span>
            <span class="fl-t">Εμείς αναλαμβάνουμε</span>
          </div>
        </div>
        <p class="hd-flow-note">Τις φωτογραφίες τις προσαρμόζουμε και τις τοποθετούμε εμείς. Δεν ανοίγεις ποτέ editor και δεν χρειάζεται να ξέρεις από κατασκευή site.</p>
      </div>
    </div>

    <div class="hd-pair">
      <div class="hd hd-host">
        <div class="hd-said">
          <span class="hd-name">Hosting</span>
          <p>Μένει online. Δεν ανανεώνεις τίποτα, δεν πληρώνεις ξεχωριστά.</p>
        </div>
        <div class="hd-panel hd-status">
          <span class="st-line"><i class="dot" aria-hidden="true"></i>online</span>
          <span class="st-sub">HTTPS ενεργό</span>
          <span class="st-sub">Χωρίς ανανεώσεις, χωρίς χωριστό λογαριασμό</span>
        </div>
      </div>

      <div class="hd hd-seo">
        <div class="hd-said">
          <span class="hd-name">Local SEO</span>
          <p>Επάγγελμα, περιοχή και τηλέφωνο γραμμένα ώστε να σε βρίσκει η τοπική αναζήτηση.</p>
        </div>
        <div class="hd-panel hd-nap">
          <span class="nap-kind">Υδραυλικός · Περιστέρι</span>
          <span class="nap-area">Εξυπηρετούμε: Περιστέρι · Ίλιον · Πετρούπολη</span>
          <span class="nap-tel">210 5700000</span>
          <span class="nap-note">Από πραγματικό site που φτιάξαμε</span>
        </div>
      </div>
    </div>

    <div class="hd hd-edit">
      <div class="hd-said">
        <span class="hd-name">Αλλαγές</span>
        <p>Στέλνεις μήνυμα. Δεν ανοίγεις ποτέ editor.</p>
      </div>
      <div class="hd-chat">
        <span class="ask">Άλλαξε το ωράριο σε 12:00–01:00</span>
        <span class="ans">Έγινε.</span>
      </div>
    </div>
  </section>

  <section class="sec sec-how" id="how">
    <h2 class="hw-title">Πώς γίνεται.</h2>
    <ol class="hw">
      <li><span class="hw-n">01</span><span class="hw-t">Μας λες τι κάνεις</span></li>
      <li><span class="hw-n">02</span><span class="hw-t">Το φτιάχνουμε</span></li>
      <li><span class="hw-n">03</span><span class="hw-t">Το δημοσιεύουμε</span></li>
      <li><span class="hw-n">04</span><span class="hw-t">Το κρατάμε ενημερωμένο</span></li>
    </ol>
  </section>

  <section class="sec sec-price" id="pricing">
    <div class="pr-left">
      <p class="pr-amount">€14,99<span>/μήνα</span></p>
      <p class="pr-terms">Πρώτος μήνας δωρεάν.<br>Ακύρωση όποτε θέλεις.</p>
      <a class="pr-cta" href="#brief">Ξεκίνα δωρεάν</a>
    </div>
    <div class="pr-right">
      <p class="pr-inc-title">Στη συνδρομή</p>
      <ul class="pr-inc">
        <li>Κατασκευή site</li>
        <li>Hosting</li>
        <li>Local SEO</li>
        <li>Αλλαγές &amp; συντήρηση</li>
      </ul>
      <p class="pr-opt">Προαιρετικά: δικό σου .gr domain — <b>€24/έτος</b>, με την τεχνική ρύθμιση δική μας.</p>
    </div>
  </section>

  <section class="sec sec-final" id="start">
    <div class="fc-copy">
      <h2>Πες μας τι κάνεις.<br>Εμείς αναλαμβάνουμε την online παρουσία σου.</h2>
      <a class="fc-cta" href="#brief">Ξεκίνα — πρώτος μήνας δωρεάν</a>
      <p class="fc-note">Πρώτος μήνας δωρεάν · ακύρωση όποτε θέλεις</p>
    </div>
    <div class="fc-proof" aria-hidden="true">
      <img src="shots/prf-cafe-tall.jpg" width="228" height="296" alt="" loading="lazy">
      <img src="shots/prf-dentist-full.jpg" width="228" height="296" alt="" loading="lazy">
      <img src="shots/prf-plumber-full.jpg" width="228" height="296" alt="" loading="lazy">
      <img src="shots/prf-salon-full.jpg" width="228" height="296" alt="" loading="lazy">
    </div>
  </section>

  <footer class="ft">
    <span class="ft-brand">vitrina</span>
    <a class="ft-mail" href="mailto:hello@getvitrina.gr">hello@getvitrina.gr</a>
    <nav class="ft-legal">
      <a href="privacy.html">Απόρρητο</a>
      <a href="terms.html">Όροι</a>
      <a href="refunds.html">Ακυρώσεις</a>
      <a href="data-deletion.html">Διαγραφή δεδομένων</a>
    </nav>
  </footer>
'''.replace("PORTFOLIO", portfolio_items())


CSS = '''
  /* ═══════════ Κάτω από το πρώτο viewport ═══════════ */
  .sec{ padding:66px 48px; }
  .sec-head{ max-width:640px; margin:0 0 40px; }
  .sec h2{
    margin:0;
    font-size:26px;
    font-weight:600;
    line-height:1.25;
    letter-spacing:-.015em;
    color:var(--text);
  }
  .sec-head p{ margin:10px 0 0; font-size:17px; color:var(--secondary); line-height:1.5; }

  /* ── 1. Χαρτοφυλάκιο ── */
  .sec-pf{ padding-bottom:76px; }
  .pf-strip{
    display:flex;
    gap:20px;
    overflow-x:auto;
    scroll-snap-type:x mandatory;
    scroll-padding-left:48px;
    margin:0 -48px;
    padding:4px 48px 20px;
    scrollbar-width:none;
  }
  .pf-strip::-webkit-scrollbar{ display:none; }
  .pf-item{
    flex:0 0 460px;
    scroll-snap-align:start;
    text-decoration:none;
    color:inherit;
    display:block;
  }
  .pf-shot{
    display:block;
    height:500px;
    overflow:hidden;
    border:1px solid var(--line);
    border-radius:10px;
    background:var(--warm);
    box-shadow:0 1px 2px rgba(23,23,20,.05), 0 10px 28px rgba(23,23,20,.07);
    transition:box-shadow .3s cubic-bezier(.22,.7,.3,1);
  }
  .pf-shot img{ display:block; width:100%; height:auto; }
  .pf-item:hover .pf-shot{ box-shadow:0 2px 6px rgba(23,23,20,.06), 0 18px 40px rgba(23,23,20,.12); }
  .pf-meta{ display:block; padding:16px 2px 0; }
  .pf-name{ display:block; font-size:16px; font-weight:600; }
  .pf-kind{ display:block; margin-top:2px; font-size:14px; color:var(--secondary); }
  .pf-go{ display:block; margin-top:8px; font-size:14px; color:var(--accent); }
  .pf-item:focus-visible .pf-shot{ outline:2px solid var(--accent); outline-offset:3px; }

  /* ── 2. Τι αναλαμβάνουμε ── */
  .sec-handles{ background:var(--warm); padding-top:56px; padding-bottom:56px; }
  .sec-handles .sec-head{ margin-bottom:30px; }
  .hd{ display:grid; grid-template-columns:300px minmax(0,1fr); gap:40px; align-items:start; }
  .hd-said .hd-name{
    display:block; font-size:13px; font-weight:600;
    letter-spacing:.1em; text-transform:uppercase; color:var(--accent);
  }
  .hd-said p{ margin:10px 0 0; font-size:16px; line-height:1.55; color:var(--secondary); }

  .hd-build{ padding-bottom:22px; border-bottom:1px solid var(--line); }
  .hd-head{
    margin:12px 0 0 !important;
    font-size:20px; font-weight:600; line-height:1.3;
    letter-spacing:-.01em; color:var(--text) !important;
  }
  .hd-sub{ margin:8px 0 0 !important; font-size:16px; line-height:1.5; }
  /* Μία συνεχής ακολουθία: τρεις είσοδοι του πελάτη, μετά η ανάληψη.
     ΧΩΡΙΣ αρίθμηση — το «Πώς γίνεται» πιο κάτω έχει ήδη αριθμημένα βήματα. */
  .hd-flowwrap{ align-self:center; }
  .hd-flow{ display:flex; align-items:flex-end; gap:16px; flex-wrap:wrap; }
  .fl{ display:flex; flex-direction:column; gap:12px; }
  .fl-art{ display:flex; align-items:flex-end; height:66px; }
  .fl-t{ font-size:14px; font-weight:500; color:var(--secondary); line-height:1.35; }
  .fl-ar{ font-style:normal; color:var(--accent); font-size:15px; padding-bottom:26px; }

  .fl-pick{ position:relative; width:118px; }
  .fl-pick img{
    position:absolute; bottom:0; width:44px; height:58px;
    object-fit:cover; object-position:top;
    border:1px solid var(--line); border-radius:5px; background:#fff;
  }
  .fl-pick img:nth-child(1){ left:0;    bottom:0; }
  .fl-pick img:nth-child(2){ left:37px; bottom:4px; z-index:2;
    border:2px solid var(--accent); box-shadow:0 4px 12px rgba(23,23,20,.10); }
  .fl-pick img:nth-child(3){ left:74px; bottom:0; }

  .fl-up{ position:relative; width:82px; }
  .fl-up i{
    position:absolute; bottom:0; width:40px; height:40px;
    border:1px solid var(--line); border-radius:6px; background:#fff;
  }
  .fl-up i:nth-child(1){ left:0;    bottom:10px; }
  .fl-up i:nth-child(2){ left:14px; bottom:5px; }
  .fl-up i:nth-child(3){ left:28px; bottom:0; z-index:2;
    background:var(--warm); border-color:var(--accent); }
  .fl-up i:nth-child(3)::after{
    content:"+"; position:absolute; inset:0; display:grid; place-items:center;
    color:var(--accent); font-size:17px; font-weight:600; line-height:1;
  }
  /* Το πίσω πλακίδιο δηλώνεται ως λογότυπο — μικρό τετράγωνο σήμα, ώστε το
     βήμα να διαβάζεται «λογότυπο ΚΑΙ φωτογραφίες» χωρίς δεύτερο εικονίδιο. */
  .fl-up i.lg{ background:var(--warm); border-color:var(--line); z-index:3; }
  .fl-up i.lg::after{
    content:""; position:absolute; left:11px; top:11px; width:14px; height:14px;
    border:2px solid var(--secondary); border-radius:3px;
  }
  .fl-alt{
    display:block; margin-top:5px; font-style:normal;
    font-size:12.5px; font-weight:400; color:var(--accent);
  }

  .fl-msg{
    max-width:196px; align-items:center;
    background:#fff; border:1px solid var(--line);
    border-radius:14px 14px 14px 4px; padding:9px 13px;
    font-size:13px; line-height:1.35; color:var(--text);
  }

  /* το τελευταίο βήμα έχει σκόπιμα μεγαλύτερο βάρος — είναι η υπόσχεση */
  .fl-end{ margin-left:10px; padding-left:26px; border-left:1px solid var(--line); }
  .fl-ok{
    flex:none;
    width:38px; height:38px; border-radius:50%;
    background:var(--accent); color:var(--bg);
    display:grid !important; place-items:center;
    font-size:19px; line-height:1;
  }
  .fl-end .fl-t{ font-size:17px; font-weight:600; color:var(--text); }
  .hd-flow-note{ margin:22px 0 0 !important; font-size:13px; color:var(--secondary); }

  .hd-pair{
    display:grid; grid-template-columns:1fr 1fr; gap:56px;
    padding:22px 0; border-bottom:1px solid var(--line);
  }
  .hd-pair .hd{ grid-template-columns:1fr; gap:22px; }
  .hd-panel{
    background:#fff; border:1px solid var(--line); border-radius:12px;
    padding:17px 20px; display:grid; gap:5px;
  }
  .hd-status .st-line{
    display:inline-flex; align-items:center; gap:9px;
    font-size:19px; font-weight:600; color:var(--ok);
  }
  .hd-status .dot{
    width:9px; height:9px; border-radius:50%; background:var(--ok);
    display:inline-block; box-shadow:0 0 0 4px rgba(24,134,107,.14);
  }
  .hd-status .st-sub{ font-size:14px; color:var(--secondary); }
  .hd-nap .nap-kind{ font-size:16px; font-weight:600; }
  .hd-nap .nap-area,.hd-nap .nap-tel{ font-size:14px; color:var(--secondary); }
  .hd-nap .nap-tel{ font-variant-numeric:tabular-nums; }
  .hd-nap .nap-note{
    margin-top:4px; padding-top:9px; border-top:1px solid var(--line);
    font-size:12px; letter-spacing:.03em; color:var(--secondary);
  }

  .hd-edit{ padding-top:24px; align-items:center; }
  .hd-chat{ display:grid; gap:10px; justify-items:start; font-size:16px; max-width:640px; }
  .hd-chat .ask{
    background:#fff; border:1px solid var(--line);
    border-radius:16px 16px 16px 4px; padding:12px 18px; color:var(--text);
  }
  .hd-chat .ans{
    justify-self:end; background:var(--text); color:var(--bg);
    border-radius:16px 16px 4px 16px; padding:12px 18px; font-weight:500;
  }

  /* ── 3. Πώς γίνεται — μία συνεχής γραμμή ── */
  .sec-how{ padding-top:50px; padding-bottom:50px; }
  .hw-title{ margin:0 0 22px; }
  .hw{
    display:grid; grid-template-columns:repeat(4,1fr);
    margin:0; padding:20px 0 0; list-style:none;
    border-top:1px solid var(--line);
  }
  .hw li{ position:relative; padding-right:28px; }
  .hw li::before{
    content:""; position:absolute; top:-24px; left:0;
    width:7px; height:7px; border-radius:50%; background:var(--accent);
  }
  .hw-n{
    display:inline-block; font-size:12px; letter-spacing:.1em;
    color:var(--secondary); font-variant-numeric:tabular-nums;
  }
  .hw-t{ display:block; margin-top:3px; font-size:17px; font-weight:500; line-height:1.3; }

  /* ── 4. Τιμή — το σημείο που σταματά η κύλιση ── */
  .sec-price{
    background:var(--warm);
    display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr);
    gap:72px; align-items:center;
    padding-top:64px; padding-bottom:64px;
  }
  .pr-amount{
    margin:0; font-size:56px; font-weight:600;
    letter-spacing:-.03em; line-height:1; font-variant-numeric:tabular-nums;
  }
  .pr-amount span{ font-size:20px; font-weight:400; color:var(--secondary); margin-left:6px; letter-spacing:0; }
  .pr-terms{ margin:16px 0 0; font-size:17px; line-height:1.5; color:var(--secondary); }
  .pr-cta{
    display:inline-flex; align-items:center; justify-content:center;
    margin-top:28px; height:50px; padding:0 28px;
    background:var(--accent); color:var(--bg);
    border-radius:10px; font-size:16px; font-weight:600; text-decoration:none;
    transition:background-color .3s;
  }
  .pr-cta:hover{ background:var(--accent-hover); }
  .pr-cta:focus-visible,.fc-cta:focus-visible{ outline:2px solid var(--accent); outline-offset:3px; }
  .pr-inc-title{
    margin:0 0 14px; font-size:13px; font-weight:600;
    letter-spacing:.1em; text-transform:uppercase; color:var(--secondary);
  }
  .pr-inc{ margin:0; padding:0; list-style:none; }
  .pr-inc li{
    position:relative; padding:11px 0 11px 24px; font-size:17px;
    border-top:1px solid var(--line);
  }
  .pr-inc li:first-child{ border-top:0; padding-top:0; }
  .pr-inc li:first-child::before{ top:6px; }
  .pr-inc li::before{
    content:""; position:absolute; left:0; top:17px;
    width:8px; height:8px; border-radius:50%; background:var(--ok);
  }
  .pr-opt{ margin:22px 0 0; font-size:15px; line-height:1.5; color:var(--secondary); }
  .pr-opt b{ font-weight:600; color:var(--text); }

  /* ── 5. Τελικό CTA ── */
  .sec-final{
    display:grid; grid-template-columns:minmax(0,470px) minmax(0,1fr);
    align-items:center; gap:56px;
    padding-right:0; padding-top:62px; padding-bottom:62px;
    overflow:clip;
  }
  .fc-copy h2{ font-size:28px; font-weight:600; line-height:1.28; }
  .fc-cta{
    display:inline-flex; align-items:center; justify-content:center;
    margin-top:28px; height:50px; padding:0 28px;
    background:var(--accent); color:var(--bg);
    border-radius:10px; font-size:16px; font-weight:600; text-decoration:none;
    transition:background-color .3s;
  }
  .fc-cta:hover{ background:var(--accent-hover); }
  .fc-note{ margin:14px 0 0; font-size:14px; color:var(--secondary); }
  /* βεντάλια πραγματικών site που κόβεται στη δεξιά άκρη — ίδιο μοτίβο με το hero */
  .fc-proof{ position:relative; height:340px; }
  .fc-proof img{
    position:absolute; top:0; width:228px; height:296px;
    object-fit:cover; object-position:top;
    border:1px solid var(--line); border-radius:9px; background:var(--warm);
    box-shadow:0 1px 2px rgba(23,23,20,.05), 0 12px 30px rgba(23,23,20,.08);
  }
  .fc-proof img:nth-child(1){ left:0;     top:0;  }
  .fc-proof img:nth-child(2){ left:190px; top:16px; }
  .fc-proof img:nth-child(3){ left:380px; top:32px; }
  .fc-proof img:nth-child(4){ left:570px; top:48px; }

  /* ── 6. Footer ── */
  .ft{
    display:flex; flex-wrap:wrap; align-items:center; gap:14px 28px;
    padding:26px 48px 34px;
    border-top:1px solid var(--line);
    font-size:14px; color:var(--secondary);
  }
  .ft-brand{ font-size:17px; font-weight:600; color:var(--text); }
  .ft-mail{ color:var(--text); text-decoration:none; }
  .ft-mail:hover{ color:var(--accent); }
  .ft-legal{ display:flex; flex-wrap:wrap; gap:18px; margin-left:auto; }
  .ft a{ color:var(--secondary); text-decoration:none; }
  .ft a:hover{ color:var(--text); }
  .ft a:focus-visible{ outline:2px solid var(--accent); outline-offset:3px; }

  /* ── Κάτω από 900px ── */
  @media (max-width:899px){
    .sec{ padding:56px 24px; }
    .sec h2{ font-size:22px; }
    .sec-head{ margin-bottom:28px; }
    .sec-head p{ font-size:15px; }

    .pf-strip{
      gap:12px; margin:0 -24px; padding:4px 24px 16px;
      scroll-padding-left:24px;
    }
    .pf-item{ flex:0 0 84vw; }
    .pf-shot{ height:auto; aspect-ratio:380 / 466; }

    .hd{ grid-template-columns:1fr; gap:18px; }
    .hd-build{ padding-bottom:22px; }
    .hd-head{ font-size:18px; }
    .hd-sub{ font-size:15px; }
    .hd-flow{ gap:12px 20px; align-items:flex-end; }
    .fl-ar{ display:none; }
    .fl{ gap:9px; }
    .fl-art{ height:54px; }
    .fl-t{ font-size:13px; }
    .fl-alt{ font-size:12px; }
    .fl-pick{ width:104px; }
    .fl-pick img{ width:38px; height:50px; }
    .fl-pick img:nth-child(2){ left:33px; }
    .fl-pick img:nth-child(3){ left:66px; }
    .fl-msg{ max-width:290px; padding:8px 12px; }
    .fl-end{
      margin:2px 0 0; padding:14px 0 0;
      border-left:0; border-top:1px solid var(--line);
      flex-direction:row; align-items:center; gap:12px; width:100%;
    }
    .fl-end .fl-ok{ height:38px; }   /* ειδικότερο από το .fl-art παραπάνω */
    .hd-flow-note{ margin-top:14px !important; }
    .hd-pair{ grid-template-columns:1fr; gap:28px; padding:24px 0; }
    .hd-edit{ padding-top:24px; }
    .hd-chat{ max-width:none; }

    .sec-how{ padding-top:44px; padding-bottom:44px; }
    .hw{ grid-template-columns:1fr 1fr; gap:22px 0; }
    .hw li{ padding-right:16px; }
    .hw li:nth-child(n+3)::before{ top:-14px; }

    .sec-price{
      grid-template-columns:1fr; gap:34px;
      padding-top:56px; padding-bottom:56px;
    }
    .pr-amount{ font-size:42px; }
    /* στο mobile τα δύο CTA πέφτουν στην ίδια οθόνη — μένει το τελικό */
    .pr-cta{ display:none; }
    .fc-cta{ width:100%; }

    .sec-final{ grid-template-columns:1fr; gap:34px; }
    .fc-copy h2{ font-size:22px; }
    .fc-proof{ height:250px; margin:0 -24px; padding:0 24px; }
    .fc-proof img{ width:168px; height:218px; }
    .fc-proof img:nth-child(1){ left:24px; }
    .fc-proof img:nth-child(2){ left:164px; top:12px; }
    .fc-proof img:nth-child(3){ left:304px; top:24px; }
    .fc-proof img:nth-child(4){ left:444px; top:36px; }

    .ft{ padding:22px 24px 30px; }
    .ft-legal{ margin-left:0; gap:14px; }
  }
'''


def build(src: str) -> str:
    # 1. το hero γίνεται section μέσα σε main που τυλίγει όλη τη σελίδα
    out, k = re.subn(r'<main class="hero">', '<main>\n\n  <section class="hero">', src, count=1)
    assert k == 1
    out, k = re.subn(r'\n</main>\n', '\n  </section>\n' + SECTIONS + '\n</main>\n', out, count=1)
    assert k == 1, "δεν βρέθηκε το κλείσιμο του main"

    # 2. token επιτυχίας + CSS ενοτήτων
    out, k = re.subn(r'(    --warm:#F5EFE7;)', r'\1\n    --ok:#18866B;', out, count=1)
    assert k == 1
    out, k = re.subn(r'\n  /\* ── Mobile < 900px ── \*/', CSS + '\n  /* ── Mobile < 900px ── */', out, count=1)
    assert k == 1, "δεν βρέθηκε το mobile block"
    return out


def main() -> None:
    src = io.open(SRC, encoding="utf-8").read()
    out = build(src)

    # Το περιεχόμενο του hero μένει αυτούσιο
    def hero_inner(s: str) -> str:
        # από την αριστερή στήλη ως το τέλος της λεζάντας — δηλαδή ό,τι
        # εγκρίθηκε. Ο wrapper (main -> section) αλλάζει σκόπιμα και
        # επαληθεύεται χωριστά με diff γεωμετρίας.
        i = s.index('<section class="left">')
        j = s.index('</section>', s.index('<p class="caption">'))
        return s[i:j]
    assert hero_inner(src) == hero_inner(out), "ΤΟ HERO ΑΛΛΑΞΕ — άκυρο"

    for frag in ('--bg:#FBFAF7', '--accent:#E85D3F', 'font-size:34px',
                 'transform:translateY(-11px) scale(1.08)', 'overflow:clip'):
        assert frag in out, f"χάθηκε: {frag}"


    # Τα assets του hero: ίδια γεωμετρία, δραστικά μικρότερο βάρος.
    # Το hero χρειάζεται 318 x 784 απόδοσης (404 ορατά + 380 pan)· οι πηγές
    # ήταν έως 1280 x 5417 και κατέρρεαν τον renderer στο mobile.
    HERO_SRC = {"taverna-full": 784, "salon-full": 784, "dentist-full": 784,
                "rooms-tall": 404, "cafe-tall": 404}
    for nm, hh in HERO_SRC.items():
        # και στο <img src> και στο pool του script (μονά εισαγωγικά)
        out = out.replace(f'shots/{nm}.jpg', f'shots/hero-{nm}.jpg')
        out = re.sub(rf'(src="shots/hero-{nm}\.jpg" width="318" height=")\d+(")',
                     rf'\g<1>{hh}\g<2>', out)
    # ο buffer της περιστροφής δηλώνει το ύψος του πρώτου site
    out = out.replace('<img class="layer" src="" width="318" height="1064"',
                      '<img class="layer" src="" width="318" height="784"')
    assert 'shots/taverna-full.jpg' not in out, "έμεινε βαριά πηγή στο hero"
    io.open(DEST, "w", encoding="utf-8").write(out)
    print(f"OK -> {DEST.name}  {len(out.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
