# C/D Root-Cause Diagnosis

Date: 2026-08-30  
Scope: the ten themes graded D and the three themes graded C in the existing
58-theme visual baseline.  
Constraint: diagnosis only. No theme, ranking, production, deploy or runtime
file was modified.

## Executive finding

The ten D grades do **not** represent ten independent missing-content defects.
All ten receive populated normalized business data and render it through direct
`services`, `gallery` and `story` maps. Their shared failure is in the audit
capture contract:

1. every affected theme initializes below-fold customer content with
   `opacity: 0` inside a `@supports (animation-timeline: view())` block;
2. visibility is continuously derived from the element's current viewport
   position, rather than being a one-time reveal state;
3. the audit scrolls the page and then returns to the top before taking one
   full-page screenshot with animations disabled;
4. below-fold elements are therefore captured at the start of their view
   timeline, even though a real visitor sees them as they scroll into view.

The repeated root cause explains **10/10 D themes**. It is an audit-harness
artifact, not a normalized-data, adapter, selector or CSS-layout failure in ten
separate customer sites.

## D-theme data trace

The preview path is:

`demoBusinesses[biz] -> withMediaFallback(data) -> artDirect(data, theme) -> <Theme data={data}>`

`withMediaFallback` preserves populated arrays and `artDirect` may reorder
gallery media but does not remove services, gallery or story fields.

| Theme | Empty section in baseline | JSX expects | Actual fixture/data | Root cause | Smallest fix | Shared? |
|---|---|---|---|---|---|---|
| `aegean` | Rooms/amenities, postcards, story | `d.services`, `d.gallery`, `d.STORY_TITLE`, `d.story` | `rooms` fixture contains populated services, lodging gallery and story | `.room`, `.card`, `.storyFrame` are viewport-timeline reveals and were captured off-view at `opacity: 0` | Audit in reduced-motion mode for the static full-page proof; retain a separate viewport-by-viewport motion check | Shared |
| `bloom` | Treatments, gallery windows, story | `d.services`, `d.gallery`, `d.STORY_*`, `d.story`, `d.STORY_IMAGE` | `aesthetics` fixture contains populated treatments, relevant media and story | `.treat`, `.windowItem`, `.storyCard`, `.archSmall` use the same viewport-derived hidden start state | Same audit-harness correction | Shared |
| `canvas` | Services/projects and story | `d.services`; first four `d.gallery` items paired with services; `d.story`, `d.STORY_IMAGE` | `farm` fixture contains four services, gallery and story | `.work`, `.storyInner`, `.storyFig`, `.close > *` are hidden off-view by the timeline | Same audit-harness correction | Shared |
| `canvas` | “Details” grid absent | `d.gallery.slice(4)` | Fixture has four gallery items, so `rest` is empty | Intentional conditional section: the JSX does not render `#work` when `rest.length === 0` | No fix; do not fabricate extra projects | Theme-specific, intentional |
| `ember` | Menu, image wall, story | `d.services`, `d.gallery`, `d.STORY_TITLE`, `d.story`, `d.STORY_IMAGE` | `taverna` fixture contains populated menu/services, food/venue media and story | `.row`, `.tile`, `.secHead`, `.storyText`, `.storyFig` use viewport timelines | Same audit-harness correction | Shared |
| `forge` | “Τι αναλαμβάνω”, recent work, trust/story | `d.services`, `d.gallery`, `d.story`, `d.STORY_IMAGE`; trust from `TRADE/HOURS/AREAS/PHONE` | `carpenter` fixture contains services, project media, story and declared contact/trade fields | `.card`, `.shot`, `.trustItem`, `.storyIn`, `.storyFig` use viewport timelines | Same audit-harness correction | Shared |
| `marble` | Service ledger, dark ethos band, spaces | `d.services`, `d.story`, first three `d.gallery` items | `pharmacy` fixture contains populated services, story and media | `.entry`, `.secHead`, `.ethosInner`, `.space` use viewport timelines | Same audit-harness correction | Shared |
| `motor` | Work sheet, gallery, story | `d.services`, first four `d.gallery` items, `d.story` | `garage` fixture contains populated workshop services, garage media and story | `.check`, `.shot`, `.story > *` use viewport timelines | Same audit-harness correction | Shared |
| `pulse` | Services, facilities, story | `d.services`, first four `d.gallery` items, `d.story` | `gym` fixture contains populated programs/services, facility media and story | `.card`, `.space`, `.storyIn` use viewport timelines | Same audit-harness correction | Shared |
| `runway` | Services, “Δουλειές μας”, story | `d.services`, `d.gallery`, `d.story` | `gym` fixture contains populated services, gallery and story | `.svcRow`, `.look`, `.story > *` use viewport timelines | Same audit-harness correction | Shared |
| `terra` | Products, land/gallery, story | `d.services`, first four `d.gallery` items, `d.story` | `farm` fixture contains populated products/services, farm media and story | `.labelCard`, `.plot`, `.storyIn` use viewport timelines | Same audit-harness correction | Shared |

### Contract checks

- Data exists: yes, for every core section above.
- Rejected by selector/condition: no, except Canvas' deliberately optional
  post-fourth-image details grid.
- Schema/adapter mismatch: no.
- Legacy field expectation: no; all ten use the normalized lowercase arrays and
  supported uppercase identity/copy fields.
- CSS hides valid content: yes, but only as the intended start state of
  scroll-driven motion. The static audit represented that state incorrectly.
- Intentionally decorative empty regions: no confirmed customer-content shell;
  Canvas' absent details section is intentionally not mounted.

## Correct audit remediation

For complete static contact sheets, create the page/context with
`prefers-reduced-motion: reduce` before navigation. These ten styles already
scope the hidden timeline state to `prefers-reduced-motion: no-preference`, so
reduced-motion is the product-supported static representation rather than an
audit-only visual rewrite.

Motion quality must then be assessed separately with viewport-by-viewport
captures or a short recording while scrolling. A single full-page bitmap cannot
truthfully represent a scroll-linked animation at every scroll position.

Risk: **low** for the audit-harness change; **high and unnecessary** for removing
or rewriting motion independently in ten themes.

## C-theme diagnosis

### `educenter-campus`

- Native identity: explicitly built for tutoring schools, language centers,
  education and seminars. The JSX comment and section model are unambiguous.
- Current metadata: category “Επαγγελματικές υπηρεσίες”, primary
  `professional`, verticals `["professional"]`.
- Intended audit fixture: `lawyer`, selected only because `professional` maps to
  that fixture in the audit.
- Diagnosis: coherent education theme, incorrectly registered and audited as
  generic professional services. **Classification should change; no redesign is
  justified.**
- Taxonomy gap: `verticalProfiles.js` currently has no education profile, and
  `DESIGN_SYSTEM_IDS` does not include this theme. It should not be broadly
  recommended until an explicit `education` profile/aliases/fixture exists.

### `freight-lane`

- Native identity: explicitly designed for freight, logistics, removals,
  courier and storage; its information architecture answers what is moved,
  where it goes and when.
- Current metadata: category “Τεχνικά επαγγέλματα”, primary `trade`, verticals
  `["garage", "trade", "wood"]`.
- Intended audit fixture: `plumber`, selected only because `trade` maps to that
  fixture in the audit.
- Diagnosis: coherent logistics theme, incorrectly registered as a generic
  local trade. **Classification should change; no redesign is justified.**
- Taxonomy gap: there is no logistics/transport profile. The existing plumber
  alias list even includes `μετακομίσεις`, which collapses a distinct logistics
  business into emergency trades. Add an explicit logistics profile before
  exposing this theme through recommendation.

### `blue-onepage`

- Native identity and mapping are aligned with generic professional services.
  This is not a fixture mismatch.
- The C grade is genuine product age rather than broken content: the faithful
  older Bootstrap-era one-page composition is dense, stock-corporate and weakly
  specific on mobile.
- It does **not** require a ground-up redesign to reach B. Minimum future work:
  improve mobile section rhythm and secondary type sizing, simplify visual
  density, strengthen hero/CTA hierarchy, and make image crops more coherent.
  Preserve its one-page identity and MIT notice.
- Risk: **medium**, because even targeted CSS changes can drift away from the
  intentionally faithful port and need desktop/mobile visual comparison.

## Remediation plan

| Order | Action | Exact files | Risk |
|---:|---|---|---|
| 1 | Correct static capture semantics and recapture the ten D themes in reduced-motion mode; separately inspect motion while scrolling | `sites/tests/fullVisualThemeAudit.mjs`, generated files under `research/visual-theme-audit/` | Low |
| 2 | Supersede the ten D grades only after human review of corrected captures | `research/visual-theme-audit/VISUAL-AUDIT-REPORT.md` | Low |
| 3 | Add explicit education and logistics vertical contracts/fixtures, then classify the two coherent themes against them | `sites/lib/verticalProfiles.js`, `sites/lib/templates/index.js`, and the canonical catalog generator that owns `TEMPLATE_META`; corresponding vertical-profile/registry tests | Medium |
| 4 | Align backend business detection aliases with the new vertical IDs so education/logistics are not collapsed into `professional`/`plumber` | the vertical detector/mapping in `src/premium_generator.py` and its recommendation/vertical tests | Medium-high; recommendation behavior changes and is outside this diagnosis scope |
| 5 | Apply the smallest Blue Onepage visual refinement and compare at 1440/390/320 | `sites/lib/templates/BlueOnepage.module.css`; `BlueOnepage.jsx` only if semantic structure must change | Medium |

## Answers required by the brief

- D themes sharing one root cause: **10 of 10**.
- D themes requiring a theme-specific customer-data fix: **0**.
- Intentional theme-specific exception: Canvas' post-fourth-image details section.
- `educenter-campus` should change vertical: **yes, to a new explicit education vertical**.
- `freight-lane` should change vertical: **yes, to a new explicit logistics/transport vertical**.
- `blue-onepage` genuinely needs visual work: **yes, targeted refinement rather than a new design**.

## Stop condition

No implementation was performed. No theme, ranking, deployment or production
state was changed.
