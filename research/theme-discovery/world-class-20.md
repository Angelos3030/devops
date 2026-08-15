# Vitrina World-Class Theme Discovery

**Date:** 2026-08-13  
**Scope:** Research and visual discovery only. No theme, production code, ranking, design-system, or `STATUS.md` changes.  
**Implementation authority for any future work:** `skills/vitrina-theme-builder/SKILL.md`

## Method

- Inspected the current 37-theme Vitrina library and rejected color/font-only variants.
- Searched public showcases, Webflow/Framer templates, Codrops experiments, editorial sites, product brands and real local-business funnels.
- Ran the mandated repository research worker. Aggregator homepages produced weak evidence, so final selection used exact live demos/pages.
- Visually inspected live finalists primarily at 1280x720 and checked representative responsive behavior at approximately 390x844.
- No external screenshots, source, CSS, markup, text, images, fonts or assets are stored here.
- Proprietary sites are `VISUAL_REFERENCE_ONLY`. Codrops examples are marked `CODE_REUSE_ALLOWED` only because its official licensing page states downloadable demos are MIT unless specifically noted; every exact archive must still be rechecked before reuse.

## Collection Balance

| Group | Directions |
|---|---:|
| Cinematic / fullscreen / slider | 5 |
| Editorial / magazine / commerce | 3 |
| Typography-first / no-photo | 3 |
| Bento / asymmetric / modular | 2 |
| Motion / interactive | 3 |
| Premium / luxury | 3 |
| Bold / experimental | 2 |
| Conversion-first local business | 4 |

Categories overlap intentionally. The collection contains four materially different slider models: horizontal filmstrip, vertical snap slides, split-screen service carousel and grid-to-fullscreen catalog. A draggable inventory selector is included as a product capability, not mislabeled as a normal theme.

## Exactly 20 Directions

### 1. Chromatic Fullscreen Chapters

- **Reference:** [Haze for Framer](https://haze.framer.website/) · Framer Marketplace · `VISUAL_REFERENCE_ONLY`
- **Category / type:** cinematic, fullscreen · **THEME**
- **Architecture/navigation:** one idea and CTA per full-viewport color chapter; compact menu and chapter progression.
- **Motion/mobile:** vertical chapter transitions; at 390px it becomes clean stacked chapters with no horizontal overflow. Reduced motion can use ordinary scrolling.
- **Photo dependency:** **A** — excellent without photography.
- **Best verticals:** creative studio, beauty, consultant, fitness.
- **Closest Vitrina:** `one-screen`. Similar concentrated viewport, but Haze is a multi-chapter narrative rather than one fixed hero. **Not covered.**
- **Independent concept:** color-coded service chapters, progress indicator, one decision per viewport.
- **Do not copy:** Framer project, palette, avatar, copy, assets or transition choreography.
- **Difficulty:** medium.
- **Scores:** Wow 8 · Distinct 8 · SMB 8 · Mobile 9 · No-photo 10 · Conversion 7 · Feasibility 8.

### 2. Horizontal Filmstrip

- **Reference:** [Hokaido](https://hokaido.webflow.io/) · Made in Webflow · `VISUAL_REFERENCE_ONLY`
- **Category / type:** cinematic, slider · **THEME**
- **Architecture/navigation:** services/projects form the whole horizontal page architecture, with reel-like transitions to details.
- **Motion/mobile:** wheel/trackpad/swipe progression and layered parallax. At 390px it rendered without overflow; a Vitrina version needs visible arrows/progress and a vertical fallback.
- **Photo dependency:** **C** — fundamentally image-led.
- **Best verticals:** carpenter, architect, hotel, photographer.
- **Closest Vitrina:** `infinite`. Both are continuous portfolios; only this direction makes the entire document horizontal. **Not covered.**
- **Independent concept:** finite horizontal work reel with counter, touch affordance and vertical mobile mode.
- **Do not copy:** cloneable Webflow project, movie content, images, typography or transitions.
- **Difficulty:** high.
- **Scores:** 9 · 9 · 7 · 7 · 3 · 6 · 6.

### 3. Draggable Property Atlas

- **Reference:** [Nieuw Bergen](https://nieuwbergen.com/) · independent showcase · `VISUAL_REFERENCE_ONLY`
- **Category / type:** cinematic, interactive · **PRODUCT CAPABILITY**
- **Architecture/navigation:** immersive destination narrative connected to a visual inventory/availability selector.
- **Motion/mobile:** draggable parallax catalog. Mobile hero was coherent at 390px; selector should gain large targets and a list fallback.
- **Photo dependency:** **C**.
- **Best verticals:** real estate, hotel, rentals, multi-location.
- **Closest Vitrina:** `cinematic`. Shared atmosphere, but inventory interaction makes this a product surface. **Not covered.**
- **Independent concept:** data-backed selector connected to availability and lead capture.
- **Do not copy:** property data, photography, maps, branding or interaction details.
- **Difficulty:** very high.
- **Scores:** 10 · 9 · 6 · 7 · 2 · 8 · 4.

### 4. Vertical Snap Story

- **Reference:** [Fullscreen Scrolling Slideshow](https://tympanus.net/Development/FullscreenScroll/) · Codrops · `CODE_REUSE_ALLOWED` (MIT default; exact download must be checked again)
- **Category / type:** cinematic, slider · **THEME**
- **Architecture/navigation:** one full-screen story frame at a time, fixed labels and chapter progress.
- **Motion/mobile:** scroll/drag/keyboard snap with image displacement. At 390px it stayed coherent, though controls need larger tap targets and stronger contrast.
- **Photo dependency:** **C**.
- **Best verticals:** hotel, restaurant, tourism, premium craft.
- **Closest Vitrina:** `cinematic`; the material difference is discrete snap states instead of a normal scrolling document. **Not covered.**
- **Independent concept:** accessible vertical slide narrative with normal-document and reduced-motion fallbacks.
- **Do not copy:** imagery, text, typography or timing; code only after per-artifact license/provenance review.
- **Difficulty:** high.
- **Scores:** 9 · 9 · 7 · 7 · 3 · 6 · 6.

### 5. Grid-to-Fullscreen Catalog

- **Reference:** [Grid to Fullscreen Animations](https://tympanus.net/Tutorials/GridToFullscreenAnimations/) · Codrops · `CODE_REUSE_ALLOWED` with the same MIT recheck requirement.
- **Category / type:** modular, motion · **MOTION SYSTEM**
- **Architecture/navigation:** dense catalog expands one item into a focused story and returns to the same spatial position.
- **Motion/mobile:** shared-element grid/detail transition; mobile uses two/one-column index and disables expensive transforms when needed.
- **Photo dependency:** **B**.
- **Best verticals:** salon, bakery, restaurant, retail, portfolio.
- **Closest Vitrina:** `grid`. The new value is spatial continuity and detail state, not another grid. **Not covered as motion system.**
- **Independent concept:** reusable catalog-to-detail transition for work, menu and treatments.
- **Do not copy:** demo artwork/layout; code needs exact license verification and retained provenance.
- **Difficulty:** high.
- **Scores:** 9 · 8 · 8 · 7 · 6 · 7 · 6.

### 6. Live Type Specimen

- **Reference:** [Heavyweight Digital Type Foundry](https://heavyweight-type.com/) · independent commercial site · `VISUAL_REFERENCE_ONLY`
- **Category / type:** typography, no-photo · **THEME**
- **Architecture/navigation:** a living headline is the visual system; proof and CTA orbit it instead of appearing as cards.
- **Motion/mobile:** animated phrase/type state; on mobile the line breaks are authored and the interaction becomes optional tap states.
- **Photo dependency:** **A**.
- **Best verticals:** lawyer, consultant, accountant, creative studio.
- **Closest Vitrina:** `type-gallery`. Here type is interactive content, not merely a gallery treatment. **Not covered.**
- **Independent concept:** Greek kinetic headline generator backed by local fonts and business proof tokens.
- **Do not copy:** fonts, phrases, black/mustard identity, capsule menu or choreography.
- **Difficulty:** medium.
- **Scores:** 8 · 9 · 8 · 8 · 10 · 7 · 8.

### 7. Archive Index

- **Reference:** [Experimental Jetset archive](https://www.jetset.nl/) · independent studio · `VISUAL_REFERENCE_ONLY`
- **Category / type:** editorial, brutalist, no-photo · **THEME**
- **Architecture/navigation:** the homepage is a sortable chronological/alphabetical directory; the index itself is the identity.
- **Motion/mobile:** almost no motion required. Mobile becomes a filtered ordered list with sticky controls.
- **Photo dependency:** **A**.
- **Best verticals:** lawyer, architect, consultant, professional directory, repair catalog.
- **Closest Vitrina:** `sidebar`. Both are index-like, but this eliminates the normal content page and makes the directory primary. **Not covered.**
- **Independent concept:** searchable service/case index with status, date and category columns.
- **Do not copy:** archive content, typography, strike-through language or studio identity.
- **Difficulty:** low.
- **Scores:** 6 · 10 · 7 · 8 · 10 · 5 · 9.

### 8. Newsstand Mosaic

- **Reference:** [Slanted](https://www.slanted.de/) · magazine/shop · `VISUAL_REFERENCE_ONLY`
- **Category / type:** editorial, magazine · **THEME**, but **reject as new theme**
- **Architecture/navigation:** mixed-scale lead stories, updates, commerce and topic rails create multiple reading speeds.
- **Motion/mobile:** optional ticker/category rails; mobile becomes lead story plus compact feed.
- **Photo dependency:** **B**.
- **Best verticals:** cultural venue, local publication, restaurant journal, community business.
- **Closest Vitrina:** `magazine`. The reference improves feed/category behavior but does not justify another theme. **Covered.**
- **Independent concept:** extract stronger feed and horizontal category-rail primitives into `magazine`.
- **Do not copy:** publication content, artwork, products or composition.
- **Difficulty:** medium.
- **Scores:** 7 · 7 · 6 · 8 · 7 · 6 · 8.

### 9. Editorial Commerce Counter

- **Reference:** [Redbrick Coffee](https://redbrick.coffee/) · independent commerce · `VISUAL_REFERENCE_ONLY`
- **Category / type:** editorial, premium, commerce · **THEME**
- **Architecture/navigation:** oversized editorial promise shares the viewport with one tactile product image; catalog/order rail follows immediately.
- **Motion/mobile:** swipeable product rails are optional. Mobile stacks headline/image/catalog and repeats the order action.
- **Photo dependency:** **B**.
- **Best verticals:** cafe, bakery, deli, restaurant, retail.
- **Closest Vitrina:** `bakery-breadman`. Material difference: active storefront navigation and product system joined to magazine typography. **Not covered.**
- **Independent concept:** editorial storefront with persistent order rail and seasonal message modules.
- **Do not copy:** logo, red identity, packaging, photos, copy or navigation.
- **Difficulty:** medium.
- **Scores:** 8 · 8 · 9 · 9 · 7 · 9 · 8.

### 10. Spatial Material Catalog

- **Reference:** [Impronta](https://www.improntahome.com/) · architecture/product · `VISUAL_REFERENCE_ONLY`
- **Category / type:** premium, asymmetric, slider · **THEME**
- **Architecture/navigation:** projects occupy a controlled stage with numbered states, sparse annotations and material-led inquiry.
- **Motion/mobile:** architectural project slider; mobile should become numbered vertical cards with a clear swipe cue.
- **Photo dependency:** **C**.
- **Best verticals:** carpenter, kitchen studio, interior designer, architect.
- **Closest Vitrina:** `canvas`. The material catalog and per-item specification/inquiry are the material difference. **Not covered.**
- **Independent concept:** numbered material/project stage with specs and inquiry attached to each item.
- **Do not copy:** project photos, loader, menu language or transitions.
- **Difficulty:** high.
- **Scores:** 9 · 8 · 7 · 7 · 3 · 7 · 6.

### 11. Modular Product OS

- **Reference:** [Nothing](https://nothing.tech/) · product brand · `VISUAL_REFERENCE_ONLY`; live page was unstable during automated review and requires re-review.
- **Category / type:** bento, modular · **LAYOUT PRIMITIVE**, not a new theme.
- **Architecture/navigation:** semantic modules combine specs, offers, actions and product states in a strict system.
- **Motion/mobile:** small state transitions and rails; modules preserve semantic order in one column.
- **Photo dependency:** **B**.
- **Best verticals:** retail, electronics, gym, clinic, packaged services.
- **Closest Vitrina:** `bento`. This is a better module contract, not a sufficiently new architecture. **Covered.**
- **Independent concept:** add semantic module types and content contracts to `bento`.
- **Do not copy:** dot-matrix brand language, glyphs, renders, palette or dimensions.
- **Difficulty:** medium.
- **Scores:** 8 · 7 · 8 · 9 · 8 · 8 · 8.

### 12. Care Pathway

- **Reference:** [One Medical](https://www.onemedical.com/) · healthcare product · `VISUAL_REFERENCE_ONLY`
- **Category / type:** premium, conversion-first · **THEME**, but **reject as new theme**
- **Architecture/navigation:** empathetic outcome hero leads to audience, location, service and start pathways.
- **Motion/mobile:** low-motion progressive disclosure; mobile retains one promise and one clear action.
- **Photo dependency:** **B**.
- **Best verticals:** doctor, dentist, physiotherapist, diagnostic center.
- **Closest Vitrina:** `clinic-triage`. It exposes major pathway improvements but is not a separate theme. **Covered.**
- **Independent concept:** strengthen clinic-triage with audience/location pathways and outcome-led proof.
- **Do not copy:** brand, membership claims, photography, copy or curved image treatment.
- **Difficulty:** medium.
- **Scores:** 8 · 7 · 9 · 10 · 7 · 10 · 9.

### 13. Booking Ritual

- **Reference:** [Masazaki](https://masazaki.gr/) · Greek local business · `VISUAL_REFERENCE_ONLY`
- **Category / type:** conversion-first, beauty · **PRODUCT CAPABILITY**
- **Architecture/navigation:** treatment discovery, booking and gift purchase are parallel first-class journeys.
- **Motion/mobile:** the hero may rotate but taxonomy and booking state matter more; mobile needs sticky booking and thumb-friendly categories.
- **Photo dependency:** **B**.
- **Best verticals:** massage, nails, beauty, spa, wellness.
- **Closest Vitrina:** `beauty-atelier`. The difference is a transactional catalog with location, duration, staff and booking. **Not covered.**
- **Independent concept:** reusable booking data contract rendered by every beauty theme.
- **Do not copy:** logo, beige identity, photos, Greek copy, icons or booking UI.
- **Difficulty:** high.
- **Scores:** 7 · 8 · 10 · 9 · 6 · 10 · 7.

### 14. Service-Area Finder

- **Reference:** [Aspect](https://www.aspect.co.uk/) · home services · `VISUAL_REFERENCE_ONLY`
- **Category / type:** conversion-first local service · **PRODUCT CAPABILITY**
- **Architecture/navigation:** urgent promise flows directly into trade choice, area/postcode check and availability.
- **Motion/mobile:** no slider needed; mobile stacks qualification inputs before secondary content and keeps call/booking accessible.
- **Photo dependency:** **A**.
- **Best verticals:** plumber, electrician, locksmith, HVAC, cleaning.
- **Closest Vitrina:** `callout`. Availability and routing turn the page into a lead tool. **Not covered.**
- **Independent concept:** service-area eligibility plus urgency intake available across technician themes.
- **Do not copy:** brand, van image, prices, copy or form appearance.
- **Difficulty:** high.
- **Scores:** 7 · 8 · 10 · 10 · 9 · 10 · 7.

### 15. Scientific Immersion

- **Reference:** [Precision Neuroscience](https://precisionneuro.io/) · medical technology · `VISUAL_REFERENCE_ONLY`
- **Category / type:** premium, motion · **THEME**
- **Architecture/navigation:** a moving scientific field carries one promise; restrained evidence chapters establish trust.
- **Motion/mobile:** ambient visual/video plus reveals; mobile must use an optimized still/short loop and preserve evidence order.
- **Photo dependency:** **B**.
- **Best verticals:** specialist doctor, laboratory, advanced manufacturing, technology consultant.
- **Closest Vitrina:** `living`. The evidence system integrated into the immersive field is the material difference. **Not covered.**
- **Independent concept:** evidence-led immersive hero with low-bandwidth and reduced-motion modes.
- **Do not copy:** claims, neural media, branding, footage or capsule navigation.
- **Difficulty:** high.
- **Scores:** 10 · 8 · 6 · 7 · 6 · 7 · 5.

### 16. Treatment Menu Editorial

- **Reference:** [Genevieve](https://genevieve.ie/) · beauty · `VISUAL_REFERENCE_ONLY`
- **Category / type:** premium, editorial · **THEME**, but **reject as new theme**
- **Architecture/navigation:** editorial story alternates with treatment menus and appointment prompts.
- **Motion/mobile:** restrained gallery; mobile lets typography and service lists lead.
- **Photo dependency:** **B**.
- **Best verticals:** beauty, nails, hair, wellness, skin clinic.
- **Closest Vitrina:** `beauty-atelier`. Valuable service-menu rhythm, but not a different enough theme. **Covered.**
- **Independent concept:** feed menu rhythm and booking cadence into `beauty-atelier`.
- **Do not copy:** identity, treatment copy, photography or art direction.
- **Difficulty:** medium.
- **Scores:** 8 · 7 · 9 · 9 · 7 · 9 · 8.

### 17. Price-Led Service Board

- **Reference:** [RDS Nails & Beauty](https://rdsnailsandbeauty.ie/) · beauty · `VISUAL_REFERENCE_ONLY`
- **Category / type:** conversion-first, typography · **THEME + DATA CONTRACT**
- **Architecture/navigation:** services, durations and prices precede brand storytelling; category anchors support rapid decisions.
- **Motion/mobile:** static accessible pricing; mobile accordion or sticky category index handles long lists.
- **Photo dependency:** **A**.
- **Best verticals:** nails, barber, hair, massage, beauty.
- **Closest Vitrina:** `beauty-atelier`. Making price the hero creates materially different buying behavior. **Not covered.**
- **Independent concept:** structured service/duration/price theme with direct booking per row.
- **Do not copy:** prices, service wording, identity or visual styling.
- **Difficulty:** low.
- **Scores:** 7 · 8 · 10 · 9 · 10 · 10 · 9.

### 18. Quiet Destination Journal

- **Reference:** [Aman](https://www.aman.com/) · luxury hospitality · `VISUAL_REFERENCE_ONLY`
- **Category / type:** premium, luxury · **THEME**
- **Architecture/navigation:** destination chapters, quiet service detail and globally persistent reservation path.
- **Motion/mobile:** slow editorial gallery rather than an autoplay sales carousel; mobile presents one story at a time with compact date/booking controls.
- **Photo dependency:** **C**.
- **Best verticals:** hotel, villa, premium restaurant, spa, real estate.
- **Closest Vitrina:** `coast`. The destination/reservation system is the structural difference. **Not covered.**
- **Independent concept:** quiet hospitality journal with availability CTA and destination chapters.
- **Do not copy:** brand, imagery, copy, booking UI or exact art direction.
- **Difficulty:** high.
- **Scores:** 9 · 8 · 7 · 8 · 2 · 8 · 6.

### 19. Split-Screen Service Carousel

- **Reference:** [Codrops Full Width Image Slider](https://tympanus.net/codrops/2013/02/26/full-width-image-slider/comment-page-2/) · `CODE_REUSE_ALLOWED` subject to exact MIT archive verification.
- **Category / type:** slider, asymmetric · **THEME + COMPONENT**
- **Architecture/navigation:** stable service summary and CTA share the viewport with a changing image/detail panel.
- **Motion/mobile:** labeled previous/next/dots; mobile stacks text above media, supports swipe and never hides the CTA inside a slide.
- **Photo dependency:** **B**.
- **Best verticals:** dentist, beauty, carpenter, restaurant, consultant.
- **Closest Vitrina:** `split`. The changing service/story half is the material difference. **Not covered.**
- **Independent concept:** accessible labeled split-carousel driven by structured service data.
- **Do not copy:** demo images, text or implementation without final license/provenance review.
- **Difficulty:** medium.
- **Scores:** 8 · 8 · 9 · 8 · 7 · 9 · 8.

### 20. Poster Manifesto / Living Information Canvas

- **References:** [Bureau Borsche](https://bureauborsche.com/) and [More Mud](https://moremud.co/) · independent studios · `VISUAL_REFERENCE_ONLY`
- **Category / type:** bold, experimental, spatial motion · **THEME** for the canvas; poster chapter behavior belongs in existing `poster`.
- **Architecture/navigation:** declarations, labels and fragments coexist on a spatial canvas rather than rectangular sections.
- **Motion/mobile:** cursor/scroll relationships on desktop; a deterministic authored sequence on touch with no overlaps.
- **Photo dependency:** **A/B** depending on vertical.
- **Best verticals:** gym, barber, music venue, youth brand, bold restaurant, creative service.
- **Closest Vitrina:** `poster` and `kinetic`. Poster chapters are covered; constraint-based spatial information is not. **Partially covered.**
- **Independent concept:** constraint-based spatial canvas with explicit mobile reading order.
- **Do not copy:** studio work, typefaces, graphic fragments, cursor system or compositions.
- **Difficulty:** very high.
- **Scores:** 9 · 10 · 5 · 6 · 8 · 5 · 4.

## Top 10 for Vitrina

This is optimized for collection diversity, not average score:

1. **Service-Area Finder** — highest direct recurring/business value for technicians.
2. **Horizontal Filmstrip** — biggest navigation-model gap.
3. **Price-Led Service Board** — excellent zero-photo conversion direction.
4. **Chromatic Fullscreen Chapters** — broad, memorable and low-photo.
5. **Live Type Specimen** — genuine premium no-photo identity.
6. **Vertical Snap Story** — distinct cinematic architecture.
7. **Archive Index** — radically different, fast and inexpensive.
8. **Editorial Commerce Counter** — strong cafe/bakery/retail fit.
9. **Booking Ritual** — turns beauty sites into recurring operational products.
10. **Split-Screen Service Carousel** — a practical slider architecture across many verticals.

`Care Pathway` is strategically excellent but excluded from the Top 10 because `clinic-triage` can absorb it. `Grid-to-Fullscreen Catalog` is a high-value motion primitive, not a theme slot. `Draggable Property Atlas` is powerful but belongs later, after inventory/availability contracts exist.

## What Vitrina Is Missing

Ranked by improvement to **perceived customer choice**, while noting the correct implementation layer:

1. **Service-area + availability qualification** — product capability.
2. **Horizontal page architecture** — theme.
3. **Price-first service board** — theme plus structured data contract.
4. **Accessible fullscreen chapter/snap system** — theme plus motion system.
5. **Booking-ready treatment catalog** — product capability plus data contract.
6. **Interactive zero-photo type specimen** — theme.
7. **Index/directory homepage** — theme.
8. **Split-screen labeled service carousel** — theme plus component.
9. **Grid-to-detail spatial transition** — motion system.
10. **Inventory-aware visual selector** — product capability.

Do **not** implement all ten. The best first tranche for maximum diversity per unit of risk is: Service-Area Finder, Price-Led Service Board, Chromatic Fullscreen Chapters, Archive Index and Horizontal Filmstrip.

## Slider Taxonomy for Vitrina

| Slider pattern | Appropriate use | Layer |
|---|---|---|
| Hero image slider | Only when each slide has a distinct offer; never generic autoplay | Component |
| Fullscreen slide navigation | Hotels, restaurants, premium craft narratives | Theme |
| Horizontal page architecture | Portfolios, architects, carpenters, hotels | Theme |
| Service carousel | Multi-service businesses with stable CTA | Component or split theme |
| Before/after slider | Renovation, beauty, dentistry | Component |
| Project/story slider | Architecture, kitchens, real estate | Component or theme when it controls navigation |
| Split-screen slider | Service comparison and case storytelling | Theme + component |
| Vertical snap slides | Immersive destination/brand story | Theme + motion system |

## License / Reuse Report

- **Repositories reviewed:** the repository research worker inspected GitHub and public source ecosystems; no GitHub project passed both the visual-distinctiveness and exact-license threshold strongly enough to enter the final 20.
- **Licenses accepted:** Codrops downloadable demos, provisionally under its official MIT default. Exact demo notices must be rechecked before any future code reuse.
- **Licenses rejected for template redistribution:** Framer Marketplace and Webflow template/clone content. They remain visual references because template-product redistribution is restricted or not clearly granted.
- **License unverified:** no unverified source is recommended for code reuse.
- **Components reused/adapted:** 0 / 0.
- **Dependencies added:** 0.
- **Attribution required now:** none; this report links and names references. Future MIT reuse must retain copyright/license notices.
- **Themes created:** 0.
- **QA:** JSON validation and collection-count checks only; no implementation QA applies.
- **Known risks:** some showcase pages use cookies, bot protection or heavy WebGL/video; `Nothing`, `LoveFrom`, and `Impronta` were partially blocked/unstable and require re-inspection before implementation decisions.

## Final Verdict

**Yes.** If these 20 directions appeared side-by-side in the Vitrina chooser, a normal customer would perceive genuinely different website ideas because the collection changes navigation model, information architecture, interaction and buying journey—not only palette and typography.

The final chooser should not necessarily expose all 20 references as 20 new themes. Four are stronger as product capabilities, motion systems or upgrades to existing themes. That distinction prevents the theme library from growing numerically while remaining structurally repetitive.
