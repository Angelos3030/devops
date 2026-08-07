---
name: vitrina-design-system
description: Create premium modern Greek SMB website directions, blocks, copy, and local preview variants for Vitrina. Use when generating or improving Vitrina sites, Lovable-style previews, Greek business landing pages, local service websites, restaurants, cafes, dentists, beauty salons, technicians, or when choosing visual routes such as premium, warm, minimal, editorial, or trust-first.
---

# Vitrina Design System

Use this skill to make Vitrina sites feel modern, polished, and commercially useful for Greek small businesses.

## Product Goal

Generate a first preview that feels good enough for a shop owner to say:

> "Ναι, αυτό μοιάζει με κανονικό site για το μαγαζί μου."

Speed matters, but not at the cost of taste. The page must feel alive, local, and specific.

## Core Workflow

1. Identify the business vertical and primary conversion:
   - Restaurant/cafe: phone call, reservation, menu confidence.
   - Dentist/doctor: appointment request, trust, calm competence.
   - Beauty/hair: appointment, visual proof, premium feel.
   - Technician: urgent phone call, service areas, reliability.
   - Accountant/lawyer: credibility, clarity, consultation.
   - Read `../../docs/18-VERTICAL-DESIGN-INTELLIGENCE.md` before choosing a
     direction. Adapt the route to the profession's conversion, required sections,
     media policy and no-go rules; never recolor one generic profession template.
2. Choose one design route from `references/design-routes.md`.
2b. Write a short spec first using `references/design-spec.md` (the 9 sections), then build.
2c. For nail, hair and beauty businesses, choose one distinct direction from
    `references/beauty-routes.md`; do not blend all three into a generic page.
3. Compose from blocks, not from a generic page:
   - Sticky nav
   - Immersive hero with customer, licensed, or clearly non-deceptive generated imagery
   - Fast proof row
   - Services/menu/products
   - Story or trust section
   - Gallery or proof when visual business
   - Map/contact
   - Final CTA
   - Fixed mobile CTA
4. Write Greek copy that sounds local and direct. Avoid translated English.
5. Generate up to nine structurally distinct previews when the product flow asks for
   the full chooser. Rank them by vertical compatibility; do not show an unsuitable
   route merely to fill the grid.
6. Keep the final HTML static, responsive, and easy to publish.

## Taste Rules

- Select a photo mode before building: `real`, `mixed`, or `no-photo`.
- Prefer customer imagery. When none exists, create a complete no-photo direction with
  profession-specific licensed/generated visuals, material details, and strong typography.
- Never present stock or generated imagery as a real customer project. Do not use placeholder boxes.
- Keep cards at 8px radius or less unless a template already uses a different system.
- Make the first viewport immediately show the business name, city, and action.
- Use strong hierarchy: large hero, restrained sections, dense enough content.
- Avoid generic AI phrases like "experience excellence" or "your trusted partner".
- Avoid one-note palettes. Add at least one neutral, one accent, and one grounding dark color.
- Make mobile CTAs obvious and thumb-friendly.
- Prefer concrete Greek phrasing:
  - "Κλείσε τραπέζι"
  - "Κάλεσε τώρα"
  - "Κλείστε ραντεβού"
  - "Δες υπηρεσίες"

## Output Contract

For a new preview, return:

```text
route: premium | warm | minimal | trust | editorial
vertical: taverna | cafe | dentist | beauty | technician | professional
blocks: [hero, proof, menu/services, story, contact, cta]
copy tone: one short phrase
primary action: one CTA
```

When generating files, make sure:

- No unresolved `{{PLACEHOLDER}}` tokens remain.
- The page works as a standalone HTML file.
- Navigation anchors point to sections that exist.
- Phone links use `tel:`.
- Map embed uses encoded address.
- Generated preview files are clearly named.

## Guardrails

- Do not ask shop owners about obvious local-site basics like map, phone CTA, or mobile button. Include them.
- Do not create e-shop flows unless explicitly requested.
- Do not invent claims such as "30 years experience" unless provided.
- Do not publish live or spend ad budget from this skill.

## References

Read `references/design-routes.md` when choosing or adding visual routes.
Read `references/design-spec.md` for the spec-first workflow, responsive breakpoints,
accessibility checklist, and the pre-preview quality self-audit.
Read `references/avada-inspired-routes.md` for profession-specific route inspiration.
Read `references/external-skill-ingestion.md` before using external GitHub design
skills or importing design ideas from React/Next/Tailwind skill repos.
