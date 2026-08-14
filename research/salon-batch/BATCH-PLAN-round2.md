# Barber / Hair Salon / Beauty Salon — round 2 batch plan

**Why round 2 exists:** round 1 (see `LICENSE-GATE.md`, `SPA-PRONTO-STOP.md`)
researched 10 candidates and found only **1 PORT_OK** (Blue, already ported)
plus 9 dead ends (4 license-blocked, 2 provenance-blocked, 1 GPL, 1 quality-
rejected, 1 not-a-website). Target for this vertical is 10-15 PORT_OK — round 2
needs to find ~9-14 more, from at least 30 total candidates researched.

**Cannot be run from this sandbox** — no network route to `api.deepseek.com`,
GitHub, or any template-studio site (confirmed 2026-08-14, same limitation as
every prior live-network task this session). Every command below is exact and
ready to run on a machine with network access. Claude's role after you run
these: read `research/salon-batch-r2-*/summary.md` + `findings.json`, apply
the quality gate (render each surviving candidate, reject ugly/broken),
resolve ambiguous licenses, dedupe/cross-map, and produce the final manifest.
DeepSeek does discovery + deterministic license checks (the worker already
fetches real `LICENSE` files and GitHub API metadata — see
`src/research_worker.py`'s `_detect_license()`); it does not render pages.

## Exclusion list (paste into every batch's context so DeepSeek doesn't re-surface these)

Already researched, do not resurface unless you have a NEW reason they were misjudged:
`themefisher/blue-bootstrap` (PORTED), `hassanwaheedali/EleganceSalon`,
`motopress/bro-barbershop`, `watchout254/Spa-online-booking-website`,
`Abhisheksingh0303/Salon-Management-System`, `SGrappelli/pronto`,
`learning-zone/website-templates` (Aroma Beauty & Spa, Beauty Salon entries),
`mauricioromagnollo/go-barber`, `IsabelRubim/barbershop`.

## Batch 1 — Established template studios (highest priority)

```bash
python scripts/research.py \
  --task-id salon-batch-r2-studios \
  --objective "Find barber shop / hair salon / beauty salon website templates from established professional template studios (Themefisher, GetHugoThemes, HTML5 UP, Cruip, Colorlib, TemplateMo, Start Bootstrap, FreeHTML5.co, BootstrapMade). For each: exact template name, studio, live demo URL, license terms as stated on the studio's own page, whether it is customer-facing (not admin/SaaS/CRUD). Do NOT include: blue-bootstrap (already ported), EleganceSalon, bro-barbershop, Spa-online-booking-website, Salon-Management-System, pronto, learning-zone/website-templates entries, go-barber, IsabelRubim/barbershop — already researched, see research/salon-batch/LICENSE-GATE.md." \
  --context "Vitrina builds Greek SMB websites — see docs/18-VERTICAL-DESIGN-INTELLIGENCE.md. Need MANY candidates (target 15-20 from this batch alone), not just the first few found. Reject any result that is a SaaS/booking-app product page, admin panel, or has no clear license." \
  --sources \
    "https://themefisher.com/tags/salon" \
    "https://themefisher.com/tags/barber" \
    "https://gethugothemes.com/tags/business/" \
    "https://html5up.net/" \
    "https://cruip.com/templates/" \
    "https://colorlib.com/wp/free-hair-salon-website-templates/" \
    "https://www.templatemo.com/tags/salon" \
    "https://startbootstrap.com/templates?search=salon" \
  --max-pass2 20
```

## Batch 2 — GitHub topic search (clear provenance only)

```bash
python scripts/research.py \
  --task-id salon-batch-r2-github \
  --objective "Find GitHub repositories that are genuine barber/hair-salon/beauty-salon BUSINESS WEBSITE templates (not booking apps, not admin dashboards, not course/bootcamp projects) with a real LICENSE file and clear original authorship. For each candidate note: repo owner, whether README credits an original designer/source, star count, last commit date (staleness signal), fork status. Flag anything that looks like a course/bootcamp/tutorial project (Rocketseat, freeCodeCamp, Udemy clone, etc.) for provenance review rather than auto-accepting the MIT license on the code." \
  --context "Vitrina builds Greek SMB websites. Exclude repos already researched: themefisher/blue-bootstrap, hassanwaheedali/EleganceSalon, motopress/bro-barbershop, watchout254/Spa-online-booking-website, Abhisheksingh0303/Salon-Management-System, SGrappelli/pronto, learning-zone/website-templates, mauricioromagnollo/go-barber, IsabelRubim/barbershop." \
  --sources \
    "https://api.github.com/search/repositories?q=barbershop+website+template&sort=stars" \
    "https://api.github.com/search/repositories?q=hair+salon+website&sort=stars" \
    "https://api.github.com/search/repositories?q=beauty+salon+template&sort=stars" \
    "https://api.github.com/search/repositories?q=topic:barbershop-website" \
    "https://api.github.com/search/repositories?q=topic:salon-website" \
  --max-pass2 20
```

## Batch 3 — Original/independent template authors (portfolio sites, Gumroad, etc.)

```bash
python scripts/research.py \
  --task-id salon-batch-r2-authors \
  --objective "Find barber/hair-salon/beauty-salon website templates from independent designers/developers publishing their own original work (personal portfolios, dev.to showcases, CodePen Pro pens marked original, Gumroad free/paid templates with the designer's own name attached). Prioritize sources where authorship is unambiguous over anonymous aggregators." \
  --context "Vitrina builds Greek SMB websites. Same exclusion list as prior batches — see research/salon-batch/LICENSE-GATE.md for the 10 already researched." \
  --sources \
    "https://codepen.io/search/pens?q=barber%20shop%20website" \
    "https://codepen.io/search/pens?q=hair%20salon%20landing" \
    "https://dribbble.com/tags/barbershop_website" \
  --max-pass2 15
```

## Round 2 result (2026-08-14) — zero new PORT_OK, do not use as-is

- **Batch 1 (studios):** 5/8 source URLs 404'd or returned empty (Themefisher,
  GetHugoThemes, Cruip, Colorlib, TemplateMo tag-path guesses were wrong).
  Start Bootstrap returned only its Angular app shell (client-rendered, no
  usable HTML from a plain fetch). Only `html5up.net` returned real content —
  DeepSeek then classified the ENTIRE HTML5 UP catalog (~44 generic templates,
  none salon-specific) as "ADAPT," and separately **missed that the fetched
  page text literally says "Licensed under the Creative Commons Attribution
  license"** — every finding was recorded `license: LICENSE_UNVERIFIED`
  despite the fact being present in the source DeepSeek was given. Decision:
  **skip HTML5 UP entirely** for this vertical — not salon-specific, requires
  redesign (forbidden by the brief), and the CC-BY attribution question isn't
  worth resolving for generic templates.
- **Batch 2 (GitHub):** found real barbershop-named repos
  (shock-dev/barbershop, samsalgado/Barbershop-Template, 6 more) — all
  correctly LICENSE_BLOCKED, no LICENSE file on any of them. Same pattern as
  round 1: real GitHub barbershop projects almost never ship a license.
- **Batch 3 (independent authors):** dead batch — sources were Dribbble/
  CodePen tag/search pages, not individual attributable pieces. Orchestrator
  error (bad source selection), not a DeepSeek failure. Not retried in round 3
  — low expected yield for the effort.

**Round 3 fixes the batch-1 source problem**: use each studio's actual
catalog/homepage root instead of a guessed tag-filtered path (the same
pattern that worked for html5up.net — root page, not a guessed sub-path).
These still need live verification (this sandbox cannot check reachability
before handoff):

```bash
python scripts/research.py \
  --task-id salon-batch-r3-studios \
  --objective "Find barber shop / hair salon / beauty salon website templates from established professional template studios. Scan each studio's FULL catalog listing for anything genuinely salon/barber/beauty-relevant (service-menu layouts, gallery/portfolio-of-work layouts, booking-adjacent CTAs) — do not just list the whole catalog as 'adaptable.' A generic portfolio/blog/SaaS-landing template that would require redesign to fit a salon is NOT a candidate, even from a reputable studio. Do NOT include any HTML5 UP template (already reviewed, see research/salon-batch/BATCH-PLAN-round2.md) or anything from research/salon-batch/LICENSE-GATE.md's exclusion list. For each candidate, extract and quote the EXACT license text found on the page — do not mark LICENSE_UNVERIFIED if the source content contains a license statement." \
  --context "Vitrina builds Greek SMB websites — see docs/18-VERTICAL-DESIGN-INTELLIGENCE.md. Target 15-20 genuinely relevant candidates from this batch. Reject generic multi-purpose templates that aren't service/gallery-oriented." \
  --sources \
    "https://themefisher.com/" \
    "https://gethugothemes.com/" \
    "https://cruip.com/" \
    "https://colorlib.com/wp/free-html5-templates/" \
    "https://www.templatemo.com/" \
    "https://bootstrapmade.com/free-website-templates/" \
    "https://www.free-css.com/free-css-templates" \
  --max-pass2 20
```

If any of these root URLs also 404 or return an empty/JS-shell page (check
`research/salon-batch-r3-studios/evidence.json` — `"ok": false` or suspiciously
short `"content"` means the fetch failed), that studio needs a browser-based
check (Claude in Chrome, or manual) instead of another guessed URL — don't
keep guessing paths blind a third time.

## After all three batches finish

1. Read `research/salon-batch-r2-*/summary.md` and `findings.json` for each.
2. For every HIGH/MEDIUM candidate, Claude (not DeepSeek) does the quality
   gate: open the live demo, screenshot desktop+mobile, reject anything ugly/
   broken/not-a-business-site, check visual diversity against the categories
   in the original task (luxury dark, editorial, typography-first, booking-
   first, etc.) and against Blue (already ported — don't pick near-duplicates).
3. For ambiguous licenses/provenance (README says MIT but structure looks
   like a bootcamp project, aggregator repos, paid templates), Claude
   inspects directly rather than trusting DeepSeek's classification.
4. Produce the final manifest (schema below) and stop once ≥10 genuine
   PORT_OK candidates exist — do not pad with mediocre entries to hit 15.

## Manifest schema (final output, Claude-produced after validation)

```
id, vertical, source_name, exact_raw_url, official_demo_url, original_author,
source_type, license, license_evidence, design_provenance, commercial_use,
repeated_client_use, asset_restrictions, customer_facing, professional_quality,
visual_direction, architecture, photo_dependency, motion_slider, mobile_quality,
closest_other_candidate, material_difference, fidelity_feasibility, decision
```
`decision` ∈ {PORT_OK, LICENSE_REVIEW, QUALITY_REJECT, LICENSE_BLOCKED,
PROVENANCE_BLOCKED, NOT_A_WEBSITE}
