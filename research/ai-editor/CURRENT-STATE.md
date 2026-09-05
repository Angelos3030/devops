# Current State of the Vitrina Editing System

This document maps the existing codebase infrastructure relevant to the conversational editing system to ensure we reuse canonical components rather than inventing competing state or content models.

## 1. Database Schema (`db/migrations/0000_production_baseline.sql`)

The repository already defines a set of tables in Supabase for client data and site content:

- **`clients`**: Stores the root client identity.
  - `id` (UUID, primary key)
  - `name` (business name)
  - `business_type` (vertical/profession)
  - `city` (business city/location)
  - `phone`, `email` (contact info)
  - `plan` (pricing plan, e.g., `'starter'`)
  - `status` (e.g., `'trial'`, `'active'`)
  - `media_policy` (added in `0002_media_semantics.sql` - e.g., `'real-only'`)
- **`site_content`**: The canonical store for customized/edited client site details.
  - `client_id` (UUID, primary key referencing `clients.id`)
  - `content` (JSONB containing custom fields that override defaults)
  - `updated_at` (timestamptz)
- **`client_assets`**: Stores uploaded assets (photos, logo).
  - `client_id` (UUID)
  - `type` (e.g., `'photo'`, `'logo'`, `'service'`)
  - `url` (storage URL)
  - `media_class` (added in `0002_media_semantics.sql` - `REAL_BUSINESS`, `REAL_OWNER_PERSON`, `REAL_WORK`, `REAL_SPACE`, `ILLUSTRATIVE`, `GENERATED`)
- **`sites`**: Stores site layout presets (themes) and deployment status.
  - `client_id` (UUID)
  - `preset` (layout key, e.g., `'studio'`, `'commerce'`)
  - `html` (static HTML for deployed pages)
  - `url` (Cloudflare Pages URL when live, or `'preview'` / `'selected'` markers)

## 2. Content Modeling and Overrides (`src/meta_oauth.py` / `src/premium_generator.py`)

A client's rendered site is a deterministic function of:
`normalize(intake_data) + overrides`

1. **`_intake_from_db(client_id)`** (in `src/meta_oauth.py`):
   - Reads the client base record (`name`, `business_type`, etc.).
   - Enriches it with client assets from the `client_assets` table (logo, photos, services).
   - Fetches content overrides from `site_content`.
   - Merges overrides on top of the base intake values.
2. **`normalize(intake)`** (in `src/premium_generator.py`):
   - Takes the merged intake dictionary.
   - Falls back to per-profession default copy (`_PROFESSION_COPY`) if name, tagline, or description is missing.
   - Outputs a cleaned context dictionary (all caps keys like `TAGLINE`, `SERVICES`, `PHONE`) used to fill HTML templates.

## 3. Allowed Editable Fields (`src/site_actions.py`)

The file `src/site_actions.py` contains the canonical allowlist of editable fields:

```python
EDITABLE_FIELDS = {
    "name", "trade", "phone", "email", "city", "address", "hours", "areas",
    "gbp_url", "facebook", "instagram",
    "tagline", "intro", "story_title", "story_paragraphs", "cta_title",
    "services", "template", "palette", "font_pair"
}
```

- **Chat Allowed**: Fields modifiable via LLM conversational editor (`via_chat=True`).
- **Elsewhere**: Actions that must be performed manually via UI buttons (defined in `ELSEWHERE` mapping, e.g., logo upload, photo upload, billing).

## 4. Current Chat-Edit Implementation (`src/site_edit.py`)

The existing AI editor (`chat_edit` in `src/site_edit.py`) is structured as follows:

1. **LLM Input**: Takes the user message, the current site JSON content, and the recommended templates.
2. **System Prompt**: Defines a list of rules (exclusively Greek, short replies, deterministic confirmations).
3. **Structured Format**: Prompt asks for:
   ```json
   {
     "changes": { "field": "value", ... },
     "reply": "Greek message detailing the change"
   }
   ```
4. **LLM Output Filtering**: The changes are checked against `EDITABLE_FIELDS`. Any key not present in `EDITABLE_FIELDS` is discarded to prevent injection or arbitrary writes.

## 5. Preview & Publishing Mechanics

1. **Preview**: The dashboard (`sites/app/dashboard/page.jsx`) renders a preview iframe using:
   `/site/{client_id}?draft={JSON.stringify(pending.changes)}`
   The Next.js site route `sites/app/site/[client]/page.jsx` reads `searchParams.draft`, decodes the JSON, and merges the fields dynamically on top of the database values before rendering.
2. **Publishing**:
   - The FastAPI backend handles `POST /clients/{client_id}/select-design`.
   - It sets the design to `'selected'` in the `sites` table.
   - A background task `_deploy_selected_bg` builds the static HTML and publishes it to Cloudflare Pages via wrangler, writing the live URL to `sites.url`.
   - For custom domains, `sites/middleware.js` rewrites inbound traffic to `/site/{domain}`, causing the Next.js app to dynamically serve the latest database state on-the-fly.
