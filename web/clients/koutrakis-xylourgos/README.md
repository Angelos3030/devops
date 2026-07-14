# Koutrakis Client Site

Domain purchased: `koutrakiskouzines.gr`

## What Is Stored Here

- `editorial.html` — chosen/presented premium portfolio route.
- `premium.html` — construction/pro route.
- `trust.html` — call-first local service route.
- `minimal.html`, `warm.html` — earlier variants kept for comparison.
- `assets/` — client photos and compressed/renamed local web assets.
- `DESIGN.md` — spec-first design brief for future agents.

## Source Of Truth

Regenerate the current site variants with:

```powershell
python -X utf8 scripts/generate_koutrakis_preview.py
```

The generator reads the client details, services, SEO keywords, phone, area, selected
domain, and gallery from `scripts/generate_koutrakis_preview.py`.

## Current Publishing Plan

1. Keep `editorial.html` as the primary route.
2. Publish it as the homepage for `koutrakiskouzines.gr`.
3. Add `www.koutrakiskouzines.gr` as an alias.
4. Use Cloudflare DNS/Pages for hosting.

## Pending

- Confirm final business name spelling.
- Confirm whether phone `6956297670` is public.
- Confirm if the owner wants `Κώστας Κουτράκης` or a more brand-like name in the hero.
- Add Facebook/Instagram only after Meta connection is ready.
