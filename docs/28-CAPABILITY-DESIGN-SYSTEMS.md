# Vitrina capability design systems

## Architecture

The implementation keeps five concerns separate:

- **Theme compositions:** `sites/lib/templates/CapabilitySystems.jsx`
- **Reusable UI capabilities:** `sites/lib/capabilities/CapabilityWidgets.jsx`
- **Data contracts:** `sites/lib/capabilities/contracts.js`
- **Provider adapters:** `sites/lib/capabilities/providers.js`
- **Motion/navigation:** native scroll snap, anchors, details/summary and transform-friendly CSS in the two CSS modules

The existing renderer, registry, Color Spine and editor metadata remain the implementation authority. `clinic-triage` is unchanged and remains first for dentist/physician profiles.

## Registry IDs

| ID | Thesis | Capabilities |
|---|---|---|
| `area-first` | Service radius qualification | service area, availability |
| `horizontal-story` | Desktop horizontal scenes, vertical mobile story | horizontal navigation |
| `price-first` | Price and duration as primary content | structured pricing, booking action |
| `chapter-snap` | Fullscreen numbered chapters | chapter navigation |
| `treatment-studio` | Catalog/detail booking flow | treatment catalog, booking action |
| `type-specimen` | Premium zero-photo typography | zero-photo presentation |
| `directory-index` | Interactive information index | directory |
| `split-carousel` | Numbered split service discovery | service carousel |
| `spatial-grid` | Grid opening into related detail | grid/detail navigation |
| `visual-selector` | Visual choice with availability states | inventory selector |

## Provider integration points

`providers.js` is deterministic and has no transport. Replace or wrap:

- `checkServiceArea()` with coverage/dispatch API data.
- `createBookingAction()` with an internal booking command or provider URL.
- `inventoryAvailability()` with normalized inventory API responses.

Components consume only normalized results. They must not know whether data came from Supabase, a booking provider, an ERP or the local demo adapter.

## Structured fields

`normaliseServices()` supports category, descriptions, fixed/from/hourly/quote/free/package prices, duration, booking state, treatment notes, practitioner IDs and availability. `normaliseInventory()` supports visual, variant, price, stock state, quantity, selectability, lead time and metadata. Global identity/contact fields keep the existing uppercase Vitrina model.

## Preview

Run `npm run dev` inside `sites/`, then open:

`/preview/<registry-id>?biz=<demo-business>`

Recommended demos: `area-first?biz=plumber`, `price-first?biz=salon`, `treatment-studio?biz=salon`, `visual-selector?biz=retail`, `type-specimen?biz=lawyer&photos=none`. The main `/` explorer includes all ten entries and their capability labels.

## QA contract

- `npm run qa:capabilities`: contract/provider states.
- `npm run qa:registry`: every system registered in all four required places.
- `npm run qa:profiles`: compatible verticals and recommendation limits.
- `npm run qa:spine`: roles, contrast and CSS provenance.
- `npm run build`: server/client boundary and production compilation.

No production backend, deployment or external API is implied by these demos.
