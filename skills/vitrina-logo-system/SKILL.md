---
name: vitrina-logo-system
description: Create or improve lightweight, reusable logos for Vitrina-generated Greek small business websites. Use when a site needs a polished brand mark, SVG logo, profession-specific symbol, wordmark, favicon-style mark, or repeatable logo rules across many generated sites.
---

# Vitrina Logo System

Build small-business logos that feel custom, fast-loading, and appropriate for Greek local service sites.

## Workflow

1. Identify the business type, name, initials, city, and visual tone.
2. Choose a mark family from `references/logo-routes.md`.
3. Prefer inline SVG for generated websites. Avoid bitmap logos unless the user explicitly wants image generation or uploaded brand assets.
4. Combine a simple profession symbol with initials or a compact monogram.
5. Keep marks readable at 40-56px in nav and usable as favicon/social avatar.
6. Use 1-2 brand colors from the site palette. Avoid generic clipart, complex illustrations, and tiny unreadable details.
7. Add accessible hidden text through the surrounding brand link; decorative SVG may be `aria-hidden="true"`.

## Output Rules

- Provide an inline SVG or HTML/CSS snippet that fits the existing template.
- Use `currentColor` or CSS variables when possible.
- Keep `viewBox="0 0 64 64"` for square nav marks unless the existing design uses another format.
- Test the logo at nav size and mobile width.
- For Greek names, use initials only when they remain clear. Example: `ΚΚ` for `Κώστας Κουτράκης`.

## Quality Bar

A good Vitrina logo should look like a small professional studio made it quickly:

- recognizable business category
- simple silhouette
- no stock-photo feeling
- no oversized decorative detail
- works on light/dark nav
- consistent with the site palette and typography
