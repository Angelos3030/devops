# Former-D Theme Audit Remediation

Date: 2026-08-31  
Scope: `aegean`, `bloom`, `canvas`, `ember`, `forge`, `marble`, `motor`,
`pulse`, `runway`, `terra` only.

## Method

- Static full-page screenshots were captured with
  `prefers-reduced-motion: reduce` set on the Playwright context **before**
  navigation.
- All ten were captured at 1440, 390 and 320 pixels.
- Normal-motion checks then exercised every element using a CSS
  `animation-timeline: view()` at 1440 and 390 while scrolling through its
  activation range.
- No theme JSX or CSS was changed.

## Re-grades

| Theme | Previous | Corrected | Visual reason | Genuine remaining defect |
|---|:---:|:---:|---|---|
| `aegean` | D | A | Complete lodging journey with strong destination hero, clear amenities, postcard gallery, story and booking CTA; mobile transformation is deliberate and readable. | None confirmed. |
| `bloom` | D | A | Cohesive premium aesthetics identity, excellent treatment imagery, strong arch motif and a complete conversion flow on both viewports. | None confirmed. The mobile page is long, but its sequence remains purposeful rather than repetitive filler. |
| `canvas` | D | B | Distinct editorial farm presentation with strong photography and complete service/story/contact content. | Desktop and mobile rhythm is unusually long and sparse; this is an intentional art direction but a minor broad-sellability concern. |
| `ember` | D | A | High-impact restaurant identity with a readable menu, appetizing gallery, coherent story band and strong reservation CTA. | None confirmed. |
| `forge` | D | B | Complete carpenter site with strong work proof, scannable services and clear phone conversion. | Eight stacked project cards make the 390/320 journey long; hazard-stripe language is strong but may not suit every premium furniture brand. |
| `marble` | D | A | Polished pharmacy presentation with excellent hierarchy, service ledger, restrained story band and relevant product imagery. | None confirmed. |
| `motor` | D | A | Complete, credible garage experience with excellent contrast, work-sheet structure, service proof and an effective mobile flow. | None confirmed. |
| `pulse` | D | B | Clean, usable gym page with programs, facility proof, philosophy and trial CTA fully present. | Visually competent but more generic than the catalog's strongest fitness themes; long stacked mobile gallery. |
| `runway` | D | B | Distinct monochrome fitness/fashion direction, clear services, project gallery and complete conversion path. | Fashion handwriting and horizontally presented work are intentionally niche and need brand fit approval for a broad gym audience. |
| `terra` | D | A | Cohesive farm/product identity with strong earthy palette, product cards, land photography, provenance story and ordering CTA. | None confirmed. |

## Motion health

Across desktop and mobile:

- **216/216 scroll-linked element checks became visible and remained visible**
  at their readable activation position.
- No element remained permanently hidden.
- No flashing, jumping or unexpected disappearance was observed.
- Post-load layout-shift score was `0.0000` for every theme/viewport.
- Maximum sampled element movement after settling was `0px`.
- Horizontal overflow: `0px` for every theme/viewport.
- Console errors: 0. Page errors: 0.

Evidence: [`motion-health.json`](remediated/motion-health.json).

## Screenshot evidence

- [Combined contact sheet 1](remediated/contact-sheets/sheet-01.jpg)
- [Combined contact sheet 2](remediated/contact-sheets/sheet-02.jpg)
- [Desktop contact sheet](remediated/desktop-contact-sheets/sheet-01.jpg)
- [Mobile contact sheet](remediated/mobile-contact-sheets/sheet-01.jpg)
- [320px contact sheet](remediated/narrow-contact-sheets/sheet-01.jpg)
- [All corrected screenshots](remediated/screenshots/)
- [Static measurements](remediated/measurements.json)

## Corrected catalog distribution

| Grade | Before | After |
|---|---:|---:|
| A | 22 | **28** |
| B | 23 | **27** |
| C | 3 | **3** |
| D | 10 | **0** |

The six A and four B promotions are based on human visual review, not simply on
content becoming visible.

## Stop condition

The approved audit remediation is complete. No theme, taxonomy, recommendation,
backend, production or deployment change was made.
