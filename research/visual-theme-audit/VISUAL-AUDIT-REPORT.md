# Vitrina Commercial Theme Visual Audit

Audit date: 2026-08-30  
Baseline: commit `69f7b51c384ed2030c79e55dc3e7d339143c826b`, dirty worktree preserved  
Scope: exactly the 58 entries in `COMMERCIAL_THEMES`  
Viewports: 1440px desktop, 390px mobile, 320px when the detector requested a narrow check  
Method: production build in isolated `.next-visual-product-audit`; realistic vertical fixture per theme; full-page scroll sweep before capture; automated measurements followed by human visual review.

## Verdict

**58/58 audited. No theme files were changed.**

| Grade | Meaning | Count |
|---|---|---:|
| A | Production quality | 30 |
| B | Good, minor visual issue | 28 |
| C | Needs meaningful visual correction | 0 |
| D | Should not currently be customer-facing | 0 |

> **Audit correction, 2026-08-31:** the ten original D grades were caused by
> full-page capture of scroll-linked `animation-timeline: view()` elements at
> their off-viewport `opacity: 0` state. Reduced-motion recapture plus a separate
> normal-motion scroll check produced six A and four B grades. Full evidence:
> [`REMEDIATION-REPORT.md`](REMEDIATION-REPORT.md).

## Contact Sheets

- Combined desktop/mobile: [`before/contact-sheets/`](before/contact-sheets/)
- Desktop-only: [`before/desktop-contact-sheets/`](before/desktop-contact-sheets/)
- Mobile-only: [`before/mobile-contact-sheets/`](before/mobile-contact-sheets/)
- Raw measurements: [`before/measurements.json`](before/measurements.json)
- All full-page screenshots: [`before/screenshots/`](before/screenshots/)

## Per-theme Findings

| Theme | Grade | Intended fit | Human visual finding |
|---|:---:|---|---|
| aegean | A | rooms | Complete premium lodging flow with strong destination hero, amenities, postcard gallery, story and clear booking CTA. |
| airspace-office | B | professional | Clean and usable, but generic office stock imagery and restrained hierarchy make it feel less distinctive than the A group. |
| area-first | B | trade | Strong lead-generation structure; hero copy/form becomes visually dense at 390px and the narrow rhythm is cramped. |
| bakery-editorial | A | bakery | Cohesive editorial bakery identity, strong imagery, good Greek typography and deliberate mobile flow. |
| barber-shop | B | beauty | Warm, credible salon page; image temperature/crop varies across sections and the long gallery rhythm is uneven. |
| beauty-atelier | A | aesthetics | Premium art direction, appropriate media, strong service hierarchy and a deliberate mobile transformation. |
| bigspring-advisory | A | professional | Clear consultancy identity, excellent hierarchy and CTAs, balanced desktop/mobile composition. |
| billys-barber | B | beauty | Good salon fit, but the monochrome barber hero and mixed salon gallery feel less unified than the strongest beauty themes. |
| bloom | A | aesthetics | Cohesive premium aesthetics identity with strong treatments, arch-led gallery, story and conversion flow. |
| blue-onepage | B | professional | Preserved classic one-page identity with improved typography, CTA clarity, semantic slider controls and a substantially calmer two-column mobile gallery. |
| callout | A | trade | Excellent emergency-service hierarchy, visible quote CTA and credible trade imagery on both viewports. |
| canvas | B | farm | Distinct and complete editorial farm site; unusually long, sparse rhythm is the only broad-sellability concern. |
| chapter-snap | B | rooms | Distinct, responsive full-screen chapters; aggressive color combinations reduce broad lodging suitability and need human brand approval. |
| cinematic | A | food | Strong restaurant storytelling, food-led imagery, controlled dark palette and good CTA placement. |
| clean-work | B | trade | Clear and responsive service page, but conventional cards, small visual proof and generic blue styling limit premium perception. |
| clinic-triage | B | dentist | Credible clinic structure and imagery; dense below-fold information and compressed mobile rhythm need minor refinement. |
| coast | B | rooms | Complete and appropriate lodging page; repeated white cards and many small thumbnails make it feel somewhat template-like. |
| constra-build | A | trade | Strong construction language, bold proof/CTA blocks and deliberate responsive composition. |
| counter-menu | A | cafe | Distinct menu-first concept with bold typography, clear daypart offer and strong mobile identity. |
| directory-index | B | professional | Deliberate directory composition and clean Greek text, but sparse visual proof and subdued conversion CTA make it niche. |
| dispatch | A | trade | Excellent one-screen emergency trade product: phone, availability, areas and services are immediately scannable. |
| educenter-campus | A | education | Coherent premium education identity, now backed by the correct taxonomy, classroom content and relevant media across desktop and mobile. |
| elegance-salon | A | beauty | Premium salon art direction, coherent typography/media and a complete high-quality customer journey. |
| ember | A | food | Complete, high-impact restaurant page with menu, appetizing gallery, story and strong reservation CTA. |
| forge | B | wood | Complete carpenter site with strong work proof; long mobile gallery and industrial styling make it slightly less universal. |
| freight-lane | A | logistics | Strong logistics hierarchy and industrial composition, now backed by transport-specific content and verified warehouse media. |
| frost-bakery | B | bakery | Clean and responsive; abstract hero spheres do not establish bakery/product appetite as strongly as photographic competitors. |
| grecko-table | A | food | Cohesive restaurant identity, excellent food imagery and alternating storytelling that holds up on mobile. |
| gymso-fitness | B | gym | Appropriate fitness imagery and complete structure; typography and cards feel conventional rather than premium-distinctive. |
| heritage-bakery | A | bakery | Strong local-history narrative, appetizing media, confident typography and varied section rhythm. |
| horizontal-story | A | wood | Unmistakably different horizontal showroom composition, excellent project media and strong identity. |
| infinite | A | garage | Credible dark automotive showroom, strong project gallery and effective contrast/CTA rhythm. |
| kinetic | A | garage | Bold editorial automotive treatment with clear services, visual proof and a distinctive responsive system. |
| klassy-cafe | B | cafe | Complete café page with suitable imagery; small typography and dense thumbnail grids weaken scanability. |
| living | B | massage | Calm, relevant and coherent; circular crops and a long narrow image rhythm are slightly awkward on mobile. |
| marble | A | pharmacy | Polished pharmacy presentation with excellent hierarchy, service ledger, story and relevant product imagery. |
| medic-care | B | doctor | Clean, trustworthy medical presentation; repeated dark booking strips and modest hierarchy feel more functional than premium. |
| microbakery-lab | A | bakery | Highly distinctive experimental bakery identity with disciplined red/black typography and strong product photography. |
| morning-journal | A | bakery | Excellent editorial local-bakery narrative, coherent color system and strong full-page rhythm. |
| moso-interior | B | wood | Strong woodworking imagery and useful gallery, but dense overlays/cards and long content rhythm reduce clarity. |
| motor | A | garage | Complete, credible garage experience with excellent contrast, work-sheet structure and service proof. |
| neighborhood-market | A | cafe | Distinct modular café identity, energetic but controlled color and strong mobile transformation. |
| novena-care | B | dentist | Professional and trustworthy dental design; some sections are sparse and the mobile page becomes long and visually repetitive. |
| price-first | B | beauty | Clear pricing-first salon offer and good conversion intent; compact type and generic gallery media keep it below the premium leaders. |
| property-atlas | A | realestate | Strong property-led narrative, relevant listings imagery, clear enquiry path and coherent responsive layout. |
| pulse | B | gym | Clean and complete gym page; visually more generic and vertically long on mobile than the catalog leaders. |
| quiet | B | pharmacy | Distinct editorial pharmacy voice and strong type; the oversized headline is demanding at narrow widths and the CTA is subdued. |
| runway | B | gym | Complete and distinctive monochrome fitness direction; its fashion handwriting and horizontal gallery are intentionally niche. |
| scandinavian-coffee | B | cafe | Cohesive café editorial style; repeated media and small body type reduce variety and legibility. |
| signature | B | dentist | Trustworthy dental structure and good hero; mixed lower-page imagery and conventional card rhythm weaken identity consistency. |
| terra | A | farm | Cohesive farm/product identity with product cards, land photography, provenance story and ordering CTA. |
| thomson-stylist | B | beauty | Complete, clean and appropriately salon-focused; the gallery/card system feels conventional and less art-directed. |
| type-gallery | A | gym | Bold typography-first fitness identity, strong contrast and a genuinely distinct mobile composition. |
| vertical-snap | A | rooms | High-impact lodging experience with deliberate full-screen typography and strong media; visually extreme but internally coherent. |
| vex-counter | B | cafe | Strong typographic café opening and relevant images; large gaps and dense menu/gallery transitions need minor rhythm refinement. |
| villa-agency | A | realestate | Complete premium listings presentation, strong property imagery, clear enquiry sections and stable mobile flow. |
| volt | B | gym | Strong gym hero and color identity; large sparse body bands and limited service proof weaken the lower half. |
| warmth | A | food | Complete, appetizing restaurant page with clear menu/story/CTA flow and strong mobile behavior. |

## Top 10

1. `elegance-salon`
2. `grecko-table`
3. `beauty-atelier`
4. `microbakery-lab`
5. `morning-journal`
6. `callout`
7. `constra-build`
8. `property-atlas`
9. `horizontal-story`
10. `cinematic`

These are the clearest examples of complete composition, vertical fit, useful conversion hierarchy and a distinct identity that survives mobile.

## Former Bottom 10 — Corrected

The original bottom-ten list is superseded. All ten apparent empty-section
failures were audit artifacts. Corrected grades: six A, four B, zero D. This
limited remediation did not re-rank the entire 58-theme catalog.

## Prioritized Confirmed Defects

### P0 — none after corrected capture

The prior ten P0 entries are withdrawn. The customer content is present and the
normal-motion scroll check confirms it becomes visible and remains stable.

### P1 — resolved

The three approved C-theme remediations are complete. Evidence and exact changes are recorded in [`FINAL-C-REMEDIATION.md`](FINAL-C-REMEDIATION.md).

## Repeated Systemic Problems

1. **Static audit versus scroll-linked motion:** full-page screenshots must use
   the product's reduced-motion representation. Motion quality requires a
   separate scroll pass; one full-page bitmap cannot represent every view
   timeline position.
2. **Vertical metadata versus native identity:** `educenter-campus` and `freight-lane` are visually coherent on their own, but the current registered primary vertical drives unrelated synthetic business data into them.
3. **Overlong mobile rhythm:** several B themes preserve all desktop sections but create a very long 390px page with repeated cards and weak transitions.
4. **Generic stock proof:** multiple otherwise sound B themes use broadly relevant but weakly distinctive stock imagery, reducing perceived custom value.
5. **Small secondary typography:** dense café, clinic and trade layouts often use body/meta text that becomes visually weak at 390px even without technical clipping.

## Automated Warnings That Were False Positives

- The detector marked 108 desktop/mobile results suspicious and requested 320px captures for 56 themes. Human review confirmed no horizontal overflow and no broken image assets.
- DOM overlap detection frequently reported nested/intentional text geometry (buttons, inline links, giant display type) as overlap. `vertical-snap`, `directory-index`, `blue-onepage` and many mobile CTAs account for most of these signals.
- The first capture attempt falsely suggested missing content because a full-page
  bitmap cannot represent every position of a scroll-linked view timeline. A
  scroll sweep followed by returning to the top still leaves off-viewport
  elements at their hidden timeline state. The corrected static baseline uses
  reduced motion before navigation and validates normal motion separately.
- Google map placeholders are intentional click-to-load privacy UI, not broken media.

Automated checks remain useful for triage, but the current overlap/suspicion thresholds are not suitable as a pass/fail visual gate.

## Human Visual Decisions Required

- `chapter-snap`: decide whether its intentionally aggressive palette is acceptable for customer-facing lodging choices.
- `directory-index`: decide whether the intentionally sparse single-screen directory is sufficiently conversion-oriented.
- `quiet`: decide whether the oversized editorial Greek headline is desirable or too demanding for broad pharmacy use.
- `vertical-snap`: decide whether the extreme full-screen typography should remain broadly exposed or only shown to bold-brand customers.
- `horizontal-story`: confirm that desktop horizontal navigation is understandable in the chooser preview, not only on the full site.

These are design-positioning decisions, not confirmed runtime defects.

## Exact Files Requiring Modification If Fixes Are Approved

No files below were modified during this audit.

### Former P0 theme files

No theme JSX/CSS modification is required for the withdrawn empty-section
findings. The remediation changed audit tooling only.

### P1 theme files

- `sites/lib/templates/BlueOnepage.jsx`, `sites/lib/templates/BlueOnepage.module.css`
- `sites/lib/templates/EducenterCampus.jsx`, `sites/lib/templates/EducenterCampus.module.css`
- `sites/lib/templates/FreightLane.jsx`, `sites/lib/templates/FreightLane.module.css`

There are no remaining P0 theme edits from this finding. Ranking/metadata
changes remain explicitly outside this audit and were not made.

## Stop Condition

Baseline, classification, screenshots and prioritized findings are complete. No visual fixes, ranking changes, deploys, pushes or production actions were performed. Awaiting human screenshot review.
