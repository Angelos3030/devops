# Vitrina Design Spec (spec-first workflow)

Adapted from the open "spec first, code second" web-design approach. Before generating
HTML, write a short `DESIGN.md`-style spec so the three previews stay consistent and the
output does not look AI-generated. Keep it lightweight — this is for a one-file static
Greek SMB site, not an app.

## Workflow

1. **Understand** — pull cues from the vertical, brand profile, and any reference the
   owner gives (existing logo, photo, competitor site). Fall back to the chosen route in
   `design-routes.md` when no cue exists.
2. **Spec** — fill the 9 sections below (2–4 lines each is enough).
3. **Generate** — produce static HTML that obeys the spec, then self-audit against the
   quality checklist before showing the preview.

## The 9 Sections

1. **Color** — grounding dark, one accent (CTA), light panel, one muted secondary. Define
   exact hex per route. Ensure text/background contrast ≥ 4.5:1.
2. **Typography** — one display/heading face + one body face. Define scale: H1, H2, body,
   small. Greek-safe fonts only (e.g. Inter, Manrope, Roboto, Noto Sans, Source Sans —
   verify Greek glyph coverage; avoid faces with no Greek).
3. **Components** — the reusable blocks present: sticky nav, hero, proof row, services/menu
   grid, story/trust, gallery, map/contact, final CTA, fixed mobile CTA.
4. **Layout** — max content width (1100–1200px), section vertical rhythm, grid columns per
   section, consistent spacing scale (4 / 8 / 16 / 24 / 48 / 80px).
5. **Motion** — restrained only: subtle scroll-reveal/fade on sections, hover lift on
   cards/buttons. No autoplay, no parallax overload. Honor `prefers-reduced-motion`.
6. **Depth** — soft shadows on cards and the sticky nav, one elevation level for the mobile
   CTA. Keep radii ≤ 8px unless the template defines otherwise.
7. **Do's & Don'ts** — concrete Greek copy, real imagery, one obvious action per screen.
   No "experience excellence", no placeholder boxes, no e-shop flow unless asked.
8. **Responsive** — see breakpoints below.
9. **Accessibility** — see checklist below.

## Responsive Breakpoints (static HTML, mobile-first)

| Range | Target | Rules |
|-------|--------|-------|
| ≤ 480px | phone | single column, fixed bottom CTA bar, tap targets ≥ 44px, nav collapses to call/menu |
| 481–768px | large phone / small tablet | single or 2-col grids, hamburger or simplified nav |
| 769–1024px | tablet | 2-col service/menu grids, hero text + image side by side |
| ≥ 1025px | desktop | full multi-column layout, max content width 1100–1200px centered |

- Build mobile-first; add complexity at larger widths with `min-width` media queries.
- Never allow horizontal overflow at any width (test 360px and 1440px).
- Images: `max-width:100%`, `height:auto`; use `srcset`/`loading="lazy"` where helpful.
- The fixed mobile CTA must not cover the footer or the last section's content.

## Accessibility Checklist

- [ ] Text/background contrast ≥ 4.5:1 (≥ 3:1 for large headings).
- [ ] Every image has meaningful `alt` (or `alt=""` if decorative).
- [ ] One `<h1>` per page; headings nest in order.
- [ ] Tap/click targets ≥ 44×44px on mobile.
- [ ] `tel:` links for phone; map has an accessible label.
- [ ] Visible focus state on links/buttons; logical tab order.
- [ ] `prefers-reduced-motion` disables non-essential animation.
- [ ] `<html lang="el">` set; meta viewport present.

## 100-Point Quality Self-Audit (before showing a preview)

- [ ] First viewport shows business name, city, and a clear action.
- [ ] No unresolved `{{PLACEHOLDER}}` tokens.
- [ ] All nav anchors point to sections that exist.
- [ ] Palette has dark + accent + light + one neutral (not one-note).
- [ ] Copy is natural Greek, no translated clichés or invented claims.
- [ ] Responsive verified at 360px, 768px, 1440px — no overflow.
- [ ] Accessibility checklist above passes.
- [ ] Page works as a standalone static HTML file.
- [ ] Mobile CTA is obvious, thumb-friendly, and not overlapping content.

## Three Previews Mapping

When the owner has not chosen a style, generate three specs/previews from
`design-routes.md`, typically:

- Preview 1 → `premium` or `editorial`
- Preview 2 → `warm`
- Preview 3 → `minimal`

Same content and structure across all three; only color, type, and layout emphasis change.
