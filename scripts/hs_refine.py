#!/usr/bin/env python3
"""Δεύτερο πέρασμα σύνθεσης στις ενότητες 2–5. Hero και portfolio ΔΕΝ αγγίζονται.

    python scripts/hs_refine.py

Επεξεργάζεται επιτόπου το scripts/homepage_sections.py: αντικαθιστά το markup
και το CSS των ενοτήτων «Τι αναλαμβάνουμε», «Πώς γίνεται», «Τιμή» και
«Τελικό CTA». Ό,τι αφορά hero, portfolio και footer μένει ως έχει.
"""
from __future__ import annotations

import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "homepage_sections.py"

# ── Markup ενοτήτων 2–5 ──────────────────────────────────────────────────
NEW_SECTIONS = '''  <section class="sec sec-handles" id="handles">
    <div class="sec-head">
      <h2>Τι αναλαμβάνουμε.</h2>
      <p>Τέσσερα πράγματα, και κανένα δεν πέφτει πάνω σου.</p>
    </div>

    <div class="hd hd-build">
      <div class="hd-said">
        <span class="hd-name">Κατασκευή site</span>
        <p>Σχέδιο φτιαγμένο για το επάγγελμά σου, όχι έτοιμο κουτί.</p>
      </div>
      <div class="hd-fan" aria-hidden="true">
        <img src="shots/taverna-full.jpg" width="128" height="428" alt="" loading="lazy">
        <img src="shots/salon-full.jpg" width="128" height="542" alt="" loading="lazy">
        <img src="shots/rooms-tall.jpg" width="128" height="200" alt="" loading="lazy">
        <img src="shots/cafe-tall.jpg" width="128" height="200" alt="" loading="lazy">
        <img src="shots/dentist-full.jpg" width="128" height="450" alt="" loading="lazy">
        <img src="shots/plumber-full.jpg" width="128" height="316" alt="" loading="lazy">
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
      <a class="pr-cta" href="#brief">Ξεκίνα — πρώτος μήνας δωρεάν</a>
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
      <img src="shots/cafe-tall.jpg" width="228" height="356" alt="" loading="lazy">
      <img src="shots/dentist-full.jpg" width="228" height="802" alt="" loading="lazy">
      <img src="shots/plumber-full.jpg" width="228" height="563" alt="" loading="lazy">
      <img src="shots/salon-full.jpg" width="228" height="965" alt="" loading="lazy">
    </div>
  </section>

'''

# ── CSS ενοτήτων 2–5 ─────────────────────────────────────────────────────
NEW_CSS = '''  /* ── 2. Τι αναλαμβάνουμε ── */
  .sec-handles{ background:var(--warm); }
  .hd{ display:grid; grid-template-columns:300px minmax(0,1fr); gap:40px; align-items:start; }
  .hd-said .hd-name{
    display:block; font-size:13px; font-weight:600;
    letter-spacing:.1em; text-transform:uppercase; color:var(--accent);
  }
  .hd-said p{ margin:10px 0 0; font-size:16px; line-height:1.55; color:var(--secondary); }

  /* βεντάλια από πραγματικά site — κλιμακωτή, κόβεται δεξιά όπως στο hero */
  .hd-build{ padding-bottom:44px; border-bottom:1px solid var(--line); }
  .hd-fan{ position:relative; height:212px; overflow:clip; }
  .hd-fan img{
    position:absolute; top:0; width:128px; height:170px;
    object-fit:cover; object-position:top;
    border:1px solid var(--line); border-radius:7px; background:#fff;
    box-shadow:0 1px 2px rgba(23,23,20,.05), 0 8px 20px rgba(23,23,20,.06);
  }
  .hd-fan img:nth-child(1){ left:0;     top:0;  }
  .hd-fan img:nth-child(2){ left:112px; top:8px; }
  .hd-fan img:nth-child(3){ left:224px; top:16px; }
  .hd-fan img:nth-child(4){ left:336px; top:24px; }
  .hd-fan img:nth-child(5){ left:448px; top:32px; }
  .hd-fan img:nth-child(6){ left:560px; top:40px; }

  .hd-pair{
    display:grid; grid-template-columns:1fr 1fr; gap:56px;
    padding:44px 0; border-bottom:1px solid var(--line);
  }
  .hd-pair .hd{ grid-template-columns:1fr; gap:22px; }
  .hd-panel{
    background:#fff; border:1px solid var(--line); border-radius:12px;
    padding:20px 22px; display:grid; gap:6px;
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

  .hd-edit{ padding-top:44px; align-items:center; }
  .hd-chat{ display:grid; gap:10px; justify-items:start; font-size:16px; max-width:460px; }
  .hd-chat .ask{
    background:#fff; border:1px solid var(--line);
    border-radius:16px 16px 16px 4px; padding:12px 18px; color:var(--text);
  }
  .hd-chat .ans{
    justify-self:end; background:var(--text); color:var(--bg);
    border-radius:16px 16px 4px 16px; padding:12px 18px; font-weight:500;
  }

  /* ── 3. Πώς γίνεται — μία συνεχής γραμμή ── */
  .sec-how{ padding-top:60px; padding-bottom:60px; }
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
    padding-top:88px; padding-bottom:88px;
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
    padding-right:0; padding-top:84px; padding-bottom:84px;
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

'''

# ── Mobile: αντικαθίσταται το τμήμα των ενοτήτων 2–5 ─────────────────────
OLD_MOBILE = '''    .hd-row{ grid-template-columns:1fr; gap:10px; padding:20px 0; }
    .hd-proof{ justify-self:start; }
    .hd-nap{ text-align:left; }
    .hd-chat{ justify-items:start; }

    .hw{ grid-template-columns:1fr 1fr; }
    .hw li{ padding:18px 16px 14px 0; }
    .hw li:nth-child(n+3){ border-top:1px solid var(--line); }
    .hw li:nth-child(n+3)::before{ top:-1px; }

    .pr-amount{ font-size:36px; }

    .sec-final{ grid-template-columns:1fr; gap:32px; }
    .fc-copy h2{ font-size:22px; }
    .fc-proof img{ width:calc((100% - 28px) / 3); height:auto; aspect-ratio:150 / 196; }'''

NEW_MOBILE = '''    .hd{ grid-template-columns:1fr; gap:18px; }
    .hd-build{ padding-bottom:32px; }
    .hd-fan{ height:150px; margin:0 -24px; padding:0 24px; }
    .hd-fan img{ width:96px; height:128px; }
    .hd-fan img:nth-child(1){ left:24px; }
    .hd-fan img:nth-child(2){ left:108px; top:7px; }
    .hd-fan img:nth-child(3){ left:192px; top:14px; }
    .hd-fan img:nth-child(4){ left:276px; top:21px; }
    .hd-fan img:nth-child(5){ left:360px; top:28px; }
    .hd-fan img:nth-child(6){ left:444px; top:35px; }
    .hd-pair{ grid-template-columns:1fr; gap:32px; padding:32px 0; }
    .hd-edit{ padding-top:32px; }
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
    .pr-cta,.fc-cta{ width:100%; }

    .sec-final{ grid-template-columns:1fr; gap:34px; }
    .fc-copy h2{ font-size:22px; }
    .fc-proof{ height:250px; margin:0 -24px; padding:0 24px; }
    .fc-proof img{ width:168px; height:218px; }
    .fc-proof img:nth-child(1){ left:24px; }
    .fc-proof img:nth-child(2){ left:164px; top:12px; }
    .fc-proof img:nth-child(3){ left:304px; top:24px; }
    .fc-proof img:nth-child(4){ left:444px; top:36px; }'''


def main() -> None:
    s = io.open(TARGET, encoding="utf-8").read()

    i = s.index('  <section class="sec sec-handles"')
    j = s.index('  <footer class="ft">')
    s = s[:i] + NEW_SECTIONS + s[j:]

    k = s.index('  /* ── 2. Τι αναλαμβάνουμε ── */')
    m = s.index('  /* ── 6. Footer ── */')
    s = s[:k] + NEW_CSS + s[m:]

    assert OLD_MOBILE in s, "δεν βρέθηκε το mobile τμήμα"
    s = s.replace(OLD_MOBILE, NEW_MOBILE, 1)

    # το portfolio και το hero μένουν ανέγγιχτα
    for frag in ('.pf-item{', 'sec sec-pf', '.ft-brand{', 'Έξι επιχειρήσεις'):
        assert frag in s, f"χάθηκε: {frag}"

    io.open(TARGET, "w", encoding="utf-8").write(s)
    print("OK — ενημερώθηκε το homepage_sections.py")


if __name__ == "__main__":
    main()
