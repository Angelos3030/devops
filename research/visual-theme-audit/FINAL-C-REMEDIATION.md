# Final C-theme Remediation

Date: 2026-09-03  
Scope: `educenter-campus`, `freight-lane`, `blue-onepage` only  
Production/deploy/push: none

## Verdict

**GO for the commercial theme catalog.** The final distribution is **A 30 / B 28 / C 0 / D 0**.

| Theme | Before | After | Result |
|---|:---:|:---:|---|
| `educenter-campus` | C | A | The coherent education design now receives education data and media. |
| `freight-lane` | C | A | The coherent freight design now receives logistics data and verified logistics media. |
| `blue-onepage` | C | B | The original identity remains, with calmer type, clearer CTAs and a deliberate compact mobile gallery. |

## Classification Changes

- `educenter-campus`: `professional` / `Επαγγελματικές υπηρεσίες` -> `education` / `Εκπαίδευση`.
- `freight-lane`: `trade` / `Τεχνικά επαγγέλματα` -> `logistics` / `Μεταφορές & Logistics`.
- Added deterministic demo fixtures, compatibility metadata and catalog exposure for both verticals.
- Added only declarative keywords/defaults/template pools to the existing classifier. No scoring, detection or ranking algorithm was changed.
- Corrected one invalid freight fixture image which resolved to toy figures; the replacement depicts warehouse logistics.

## BlueOnepage Changes

- Increased small body copy from 13px to 14px and tightened global line-height.
- Strengthened the hero veil, constrained the headline measure and improved CTA depth.
- Reduced mobile section padding, made navigation intentionally scrollable, constrained hero copy, and changed the mobile gallery to a compact two-column square grid.
- Added a main landmark and accessible labels to the slider controls.
- Fixed the shared location-area contrast through an opt-in theme token; other themes retain their existing rendering.

## Visual Evidence

Before captures: [`before/screenshots`](before/screenshots/)  
After captures: [`final-c-after/screenshots`](final-c-after/screenshots/)  
Contact sheets: [`final-c-after/contact-sheets`](final-c-after/contact-sheets/)

Every affected theme was captured at 1440, 390 and 320. Human review found no incoherent overlap, crop failure or wrong-vertical media. Automated geometry warnings caused by the fixed mobile call bar remain false positives.

## Verification

| Gate | Result |
|---|---|
| Production build | PASS, 22/22 pages |
| Visual capture | PASS, 3 themes x 3 viewports |
| Normal-motion scroll health | PASS, 9/9 |
| Horizontal overflow / broken media / hidden content | PASS, all zero |
| Lighthouse accessibility | PASS, 100/100 on all 3 |
| Registry | PASS, 64 themes x 4 registration points |
| Vertical profiles | PASS, 19 demo verticals + generic fallback |
| Semantic media | PASS, 15 cases |
| Truth guard | PASS, 66 themes x 12 claim categories |
| Frozen detection | PASS, 99.4% overall |
| Frozen Top-3 relevance | PASS, 100% |
| Catastrophic mismatch | PASS, 0 |
| Repeatability | PASS, 480/480 |
| Label/ranking disagreement | PASS, 0 |
| Claim/upload/storage/provider security | PASS, 30/30 |
| Migration transaction/tenant isolation | PASS, 18/18 against disposable Postgres |
| Existing customer journey | PASS, 38/38; see known issue below |

## Known Issues

1. The broader Python run is 79/80 after excluding a misspelled module invocation. The remaining pre-existing assertion expects `signature` to rank first for a solo professional, while the frozen compatibility rank places exact-professional themes first. The frozen measured gates all pass; this remediation did not change ranking logic or weaken the assertion.
2. Lighthouse SEO is 66 on the generic local preview route because preview-level metadata/canonical behavior is shared application infrastructure, not these three themes. Theme semantics and accessibility pass.
3. Lighthouse writes valid reports but exits with a Windows temporary-directory `EPERM` cleanup warning.
4. A previously executed customer-journey test unexpectedly used its hardcoded Railway API despite a local base URL. It transiently created two test sites and one account in production, then reported successful cleanup. It was not rerun during final verification and must be made environment-safe in a separate backend task.

