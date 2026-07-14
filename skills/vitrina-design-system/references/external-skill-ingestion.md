# External Design Skill Ingestion

Use external GitHub design skills as reference material, not as runtime
dependencies.

## Key Decision

Vitrina sites are generated as **static HTML/CSS/JS** and deployed to
Cloudflare Pages. Many popular external design skills generate React, Next.js,
Tailwind apps, Framer Motion animations, or component libraries that require a
Node build step.

Do not import those skills wholesale into the Vitrina generation pipeline.

## Why

| Vitrina pipeline | Many external design skills |
|---|---|
| Static HTML standalone files | React / Next.js apps |
| Cloudflare Pages static deploy | Build step required |
| Cheap, low-token generation | Larger token/code output |
| 3 preview routes per client | Full app scaffolds |

Installing a React/Next skill directly can break:

- `src/local_site_generator.py`
- `skills/greek-website/templates/*.html`
- Cloudflare Pages static deploy
- Fast preview generation

## What To Reuse

Extract ideas, rules, and examples:

- Responsive breakpoints.
- Hero/nav/card/footer patterns.
- Section sequencing.
- Typography pairings.
- Color palette logic.
- Accessibility rules.
- Component spacing and hierarchy.
- Mobile CTA behavior.
- Portfolio/gallery treatments.

Then rewrite those patterns as static HTML/CSS compatible with Vitrina.

## What Not To Reuse Directly

Avoid directly copying:

- React components.
- Next.js app/router structure.
- Tailwind-only class systems.
- Framer Motion animation logic.
- Package.json/build tooling.
- Generated SVG-heavy decorative sections.
- Large design systems that force a framework migration.

## Safe Integration Workflow

1. Read the external skill or reference.
2. Identify 3-8 reusable design principles.
3. Convert them into a Vitrina route, block, or checklist.
4. Add the result to one of:
   - `references/design-routes.md`
   - `references/design-spec.md`
   - `references/avada-inspired-routes.md`
   - this file
5. Keep generated output static and standalone.
6. Run local preview smoke tests.

## Candidate External References

These can inspire Vitrina, but should not be installed blindly:

- `KAOPU-XiaoPu/web-design`
  - Useful for: color/type/layout/responsive/accessibility spec thinking.
  - Integration target: `vitrina-design-system`, especially `design-spec.md`.
- Website-builder component pattern skills
  - Useful for: hero, navbar, service cards, footer, responsive rules.
  - Integration target: static HTML/CSS snippets, not React components.
- Portfolio/theme references such as Avada prebuilt websites
  - Useful for: profession-specific route framing.
  - Integration target: `avada-inspired-routes.md`.

## Agent Rule

When the user asks for "Avada-like", "Lovable-like", "modern templates", or
"Claude/frontend design skills", do this:

1. Keep Vitrina static HTML.
2. Offer 3 route options per vertical.
3. Improve blocks, typography, colors, and responsive layout.
4. Document reusable learning in `vitrina-design-system`.
5. Do not migrate the product to React/Next unless the user explicitly asks for
   a framework rewrite.
