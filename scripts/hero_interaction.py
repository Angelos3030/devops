#!/usr/bin/env python3
"""Interaction pass πάνω στο εγκεκριμένο hero. ΔΕΝ ξανασχεδιάζει τίποτα.

    python scripts/hero_interaction.py

Είσοδος:  research/homepage-redesign/hero-locked.html   (κλειδωμένο, δεν αγγίζεται)
Έξοδος:   research/homepage-redesign/hero-interactive.html

Αλλάζει ΜΟΝΟ τη δεξιά λωρίδα: markup των πλακιδίων, το CSS τους, τη λεζάντα
και ένα script. Αριστερή στήλη, τυπογραφία, παλέτα και διαχωριστικό μένουν
byte-πρὸς-byte ίδια.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "homepage-redesign"
SRC = OUT / "hero-locked.html"
DEST = OUT / "hero-interactive.html"

PREVIEW = "https://sites-production-da56.up.railway.app/preview/"

# ── Νέο markup δεξιάς λωρίδας ────────────────────────────────────────────
RIGHT_NEW = '''  <section class="right">
    <p class="lane-label">Πραγματικά site που φτιάξαμε.</p>

    <div class="tiles" id="tiles">
      <a class="tile t1 rotator" href="{p}warmth?biz=taverna" target="_blank" rel="noopener"
         data-label="Ταβέρνα · Θεσσαλονίκη" data-pan="380">
        <img class="layer on" src="shots/taverna-full.jpg" width="318" height="1064"
             alt="Ιστοσελίδα ταβέρνας που φτιάξαμε">
        <img class="layer" src="" width="318" height="1064" alt="" aria-hidden="true">
      </a>
      <a class="tile t2" href="{p}beauty-atelier?biz=salon" target="_blank" rel="noopener"
         data-label="Κομμωτήριο · Γλυφάδα" data-pan="380">
        <img class="layer on" src="shots/salon-full.jpg" width="318" height="1346"
             alt="Ιστοσελίδα κομμωτηρίου που φτιάξαμε">
      </a>
      <a class="tile t3" href="{p}aegean?biz=rooms" target="_blank" rel="noopener"
         data-label="Δωμάτια · Πάρος" data-pan="0">
        <img class="layer on" src="shots/rooms-tall.jpg" width="318" height="497"
             alt="Ιστοσελίδα για δωμάτια με θέα που φτιάξαμε" loading="lazy">
      </a>
    </div>

    <p class="caption">
      <span class="cap-default">ταβέρνα · κομμωτήριο · οδοντιατρείο · υδραυλικός · καφετέρια · δωμάτια</span>
      <span class="cap-active" aria-live="polite"></span>
    </p>
  </section>'''.replace("{p}", PREVIEW)

# ── Νέο CSS πλακιδίων (desktop) ──────────────────────────────────────────
TILES_CSS_NEW = '''  .tiles{
    position:relative;
    /* Το padding μεγαλώνει ΜΟΝΟ την περιοχή αποκοπής ώστε το ενεργό πλακίδιο
       να μπορεί να ανέβει και να μεγαλώσει χωρίς να κοπεί. Το content box
       παραμένει 492px και τα πλακίδια στις ίδιες ακριβώς συντεταγμένες. */
    height:564px;
    padding:44px 0 28px;
    margin:-14px 0 -28px;
    /* clip, ΟΧΙ hidden: το hidden παραμένει scroll container και το
       scrollIntoView (hover/focus στο 3ο πλακίδιο) κυλούσε την ομάδα
       αριστερά, καταστρέφοντας το σκόπιμο κόψιμο. */
    overflow:clip;
    pointer-events:none;
  }
  .tile{
    position:absolute;
    display:block;
    width:318px;
    height:404px;
    overflow:hidden;
    background:var(--warm);
    border:1px solid var(--line);
    border-radius:10px;
    box-shadow:0 1px 2px rgba(23,23,20,.05), 0 10px 28px rgba(23,23,20,.07);
    pointer-events:auto;
    text-decoration:none;
    color:inherit;
    transform-origin:left center;
    transition:transform .32s cubic-bezier(.22,.7,.3,1),
               opacity .32s cubic-bezier(.22,.7,.3,1),
               box-shadow .32s cubic-bezier(.22,.7,.3,1);
  }
  .tile .layer{
    position:absolute;
    top:0; left:0;
    width:100%;
    height:auto;
    opacity:0;
    transform:translateY(0);
    transition:opacity .6s ease, transform .6s cubic-bezier(.22,.7,.3,1);
  }
  .tile .layer.on{ opacity:1; }
  .tile.is-active{
    transform:translateY(-11px) scale(1.08);
    z-index:10;
    box-shadow:0 2px 6px rgba(23,23,20,.06), 0 20px 48px rgba(23,23,20,.14);
  }
  .tiles.has-active .tile:not(.is-active){
    transform:scale(.98);
    opacity:.82;
  }
  .tile:focus-visible{ outline:2px solid var(--accent); outline-offset:3px; }
  /* +44px = το padding-top του .tiles· τα abspos παιδιά τοποθετούνται ως προς
     το padding box, οπότε το offset μπαίνει εδώ για να μείνουν στις
     εγκεκριμένες συντεταγμένες 252 / 296 / 340. */
  .t1{ left:0;     top:44px;  z-index:1; }
  .t2{ left:192px; top:88px;  z-index:2; }
  .t3{ left:384px; top:132px; z-index:3; }
  .caption{
    position:relative;
    margin:24px 0 0;
    min-height:21px;
    font-size:14px;
    font-weight:400;
    line-height:1.5;
    color:var(--secondary);
  }
  .cap-default,.cap-active{ transition:opacity .16s ease; }
  .cap-active{ position:absolute; left:0; top:0; right:0; opacity:0; }
  .tiles-active .cap-default{ opacity:0; }
  .tiles-active .cap-active{ opacity:1; }

  @media (prefers-reduced-motion: reduce){
    *{ transition:none !important; animation:none !important; }
    .tile.is-active{ transform:none; }
    .tiles.has-active .tile:not(.is-active){ transform:none; opacity:1; }
    .tile .layer{ transition:none !important; }
  }'''

# ── Νέο CSS πλακιδίων (mobile) ───────────────────────────────────────────
MOBILE_CSS_NEW = '''    .tiles{
      position:static;
      height:auto;
      display:flex;
      gap:6px;
      padding:0 24px 4px;
      margin:19px 0 0;
      overflow-x:auto;
      overflow-y:hidden;
      scroll-snap-type:x mandatory;
      scroll-padding-left:24px;
      scrollbar-width:none;
      -webkit-overflow-scrolling:touch;
      pointer-events:auto;
    }
    .tiles::-webkit-scrollbar{ display:none; }
    .tile{
      position:relative;
      /* Μηδενίζει τα desktop offsets: με position:relative τα top/left των
         .t1/.t2/.t3 θα μετατόπιζαν ακόμη τα πλακίδια μέσα στο flex row. */
      top:0;
      left:0;
      flex:0 0 84vw;
      width:84vw;
      height:auto;
      aspect-ratio:318 / 404;
      scroll-snap-align:start;
      transform:none !important;
      opacity:1 !important;
      box-shadow:0 1px 2px rgba(23,23,20,.05), 0 8px 20px rgba(23,23,20,.06);
    }
    .tile .layer{ transform:none !important; }
    .caption{ margin:16px 0 0; padding:0 24px; }
    .cap-active{ left:24px; right:24px; }'''

SCRIPT_NEW = '''<script>
(function () {
  var reduce  = window.matchMedia('(prefers-reduced-motion: reduce)');
  var desktop = window.matchMedia('(min-width: 900px)');
  var tiles   = document.getElementById('tiles');
  var right   = document.querySelector('.right');
  var capA    = document.querySelector('.cap-active');
  var form    = document.getElementById('brief-form');
  var items   = [].slice.call(tiles.querySelectorAll('.tile'));

  var active = null, panTimer = null;

  /* ── hover / focus: ένα site έρχεται μπροστά ── */
  function activate(t) {
    if (active === t) return;
    deactivate();
    active = t;
    t.classList.add('is-active');
    tiles.classList.add('has-active');
    right.classList.add('tiles-active');
    capA.textContent = t.getAttribute('data-label') + ' · Δες το site ↗';
    if (!desktop.matches || reduce.matches) return;
    var d = parseInt(t.getAttribute('data-pan'), 10) || 0;
    if (!d) return;                       /* λίγο κατακόρυφο υλικό → χωρίς pan */
    var img = t.querySelector('.layer.on');
    if (!img) return;
    panTimer = setTimeout(function () {
      img.style.transitionDuration = '3.2s';
      img.style.transform = 'translateY(-' + d + 'px)';
    }, 250);
  }

  function deactivate() {
    clearTimeout(panTimer);
    if (!active) return;
    var img = active.querySelector('.layer.on');
    if (img) {
      img.style.transitionDuration = '.6s';
      img.style.transform = 'translateY(0)';
    }
    active.classList.remove('is-active');
    active = null;
    tiles.classList.remove('has-active');
    right.classList.remove('tiles-active');
  }

  items.forEach(function (t) {
    t.addEventListener('pointerenter', function (e) {
      if (e.pointerType === 'mouse') activate(t);
    });
    t.addEventListener('pointerleave', function (e) {
      if (e.pointerType === 'mouse') deactivate();
    });
    t.addEventListener('focus', function () { activate(t); });
    t.addEventListener('blur',  function () { deactivate(); });
  });

  /* ── παθητική εναλλαγή ΜΟΝΟ του πίσω πλακιδίου ── */
  var pool = [
    { src: 'shots/taverna-full.jpg', pan: 380,
      href: 'PREVIEWwarmth?biz=taverna',
      label: 'Ταβέρνα · Θεσσαλονίκη',
      alt: 'Ιστοσελίδα ταβέρνας που φτιάξαμε' },
    { src: 'shots/cafe-tall.jpg', pan: 0,
      href: 'PREVIEWbakery-editorial?biz=cafe',
      label: 'Καφετέρια · Αλκυόνη',
      alt: 'Ιστοσελίδα καφετέριας που φτιάξαμε' },
    { src: 'shots/dentist-full.jpg', pan: 380,
      href: 'PREVIEWclinic-triage?biz=dentist',
      label: 'Οδοντιατρείο · Χαλάνδρι',
      alt: 'Ιστοσελίδα οδοντιατρείου που φτιάξαμε' }
  ];
  var rot = tiles.querySelector('.rotator');
  var layers = rot ? [].slice.call(rot.querySelectorAll('.layer')) : [];
  var idx = 0, rotTimer = null, resumeTimer = null, paused = false;

  function schedule() {
    clearTimeout(rotTimer);
    if (!rot || layers.length < 2 || reduce.matches || !desktop.matches) return;
    rotTimer = setTimeout(step, 5000);
  }

  function step() {
    if (paused || active) { schedule(); return; }
    var next = pool[(idx + 1) % pool.length];
    var cur  = layers[0].classList.contains('on') ? layers[0] : layers[1];
    var off  = cur === layers[0] ? layers[1] : layers[0];
    var pre  = new Image();
    pre.onload = function () {
      off.src = next.src;
      off.alt = next.alt;
      off.removeAttribute('aria-hidden');
      off.style.transitionDuration = '';
      off.style.transform = 'translateY(0)';
      off.classList.add('on');
      cur.classList.remove('on');
      cur.alt = '';
      cur.setAttribute('aria-hidden', 'true');
      rot.href = next.href;
      rot.setAttribute('data-label', next.label);
      rot.setAttribute('data-pan', next.pan);
      idx = (idx + 1) % pool.length;
      schedule();
    };
    pre.onerror = function () { schedule(); };
    pre.src = next.src;
  }

  function pause() {
    paused = true;
    clearTimeout(rotTimer);
    clearTimeout(resumeTimer);
  }
  function resumeSoon() {
    clearTimeout(resumeTimer);
    resumeTimer = setTimeout(function () { paused = false; schedule(); }, 4000);
  }

  right.addEventListener('pointerenter', pause);
  right.addEventListener('pointerleave', resumeSoon);
  right.addEventListener('focusin',  pause);
  right.addEventListener('focusout', resumeSoon);
  if (form) {
    form.addEventListener('focusin', pause);
    form.addEventListener('input',   pause);
    form.addEventListener('focusout', resumeSoon);
  }
  schedule();

  /* Μόνο αποτροπή submit σε κενό πεδίο — καμία ψεύτικη λειτουργία. */
  if (form) {
    form.addEventListener('submit', function (e) {
      var t = document.getElementById('brief');
      if (!t.value.trim()) { e.preventDefault(); t.focus(); }
    });
  }
})();
</script>'''.replace("PREVIEW", PREVIEW)


def patch(src: str) -> str:
    n = 0

    # 1. markup δεξιάς λωρίδας
    src, k = re.subn(r'  <section class="right">.*?</section>', RIGHT_NEW, src, flags=re.S)
    assert k == 1, f"δεξιά λωρίδα: {k} αντικαταστάσεις"
    n += k

    # 2. CSS από .tiles έως και το τέλος του .caption (desktop)
    src, k = re.subn(
        r'  \.tiles\{.*?\n  \.caption\{[^}]*\}',
        TILES_CSS_NEW.rstrip(), src, count=1, flags=re.S)
    assert k == 1, f"desktop CSS: {k}"
    n += k

    # 3. το παλιό reduced-motion block έφυγε μέσα στο νέο· σβήσε το διπλό
    src, k = re.subn(
        r'\n\n  @media \(prefers-reduced-motion: reduce\)\{\n    \*\{ transition:none !important; \}\n  \}',
        '', src, count=1)
    assert k == 1, f"παλιό reduced-motion: {k}"
    n += k

    # 4. mobile block των πλακιδίων
    src, k = re.subn(
        r'    \.tiles\{\n      height:302px;.*?\n    \.caption\{ margin:16px 0 0; padding:0 24px; \}',
        MOBILE_CSS_NEW.rstrip(), src, count=1, flags=re.S)
    assert k == 1, f"mobile CSS: {k}"
    n += k

    # 5. αντικατάσταση του script
    src, k = re.subn(r'<script>.*?</script>', SCRIPT_NEW, src, count=1, flags=re.S)
    assert k == 1, f"script: {k}"
    n += k

    return src


def main() -> None:
    original = io.open(SRC, encoding="utf-8").read()
    out = patch(original)

    # Επαλήθευση ότι η αριστερή στήλη δεν άλλαξε ούτε κατά χαρακτήρα
    def left_block(s: str) -> str:
        return re.search(r'<section class="left">.*?</section>', s, re.S).group(0)
    assert left_block(original) == left_block(out), "Η ΑΡΙΣΤΕΡΗ ΣΤΗΛΗ ΑΛΛΑΞΕ — άκυρο"

    for frag in ('--bg:#FBFAF7', '--text:#171714', '--accent:#E85D3F',
                 '--warm:#F5EFE7', '--line:#E8E2D9',
                 '.divider{', 'font-size:34px', 'font-size:28px'):
        assert frag in out, f"χάθηκε: {frag}"
    assert 'shots/plumber-full.jpg' not in out, "ο υδραυλικός έμεινε στα αρχικά τρία"

    io.open(DEST, "w", encoding="utf-8").write(out)
    print(f"OK -> {DEST.name}  {len(out.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
