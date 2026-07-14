# Domain Automation

This document is the handoff for every agent that touches domain suggestions,
domain payments, registrar integration, or DNS setup.

## Current Decision

For Greek `.gr` domains, Vitrina should use:

- **Papaki or another Greek registrar/reseller** for domain registration.
- **Cloudflare** for DNS, SSL, and Pages/custom-domain routing after the domain is bought.
- **Stripe Checkout** before any registration attempt.

Do not buy a domain before the user/customer has explicitly selected it and paid.

## Product Flow

1. Customer submits onboarding form.
2. Agent suggests domains based on business name, type, and city.
3. Customer picks one domain.
4. UI shows: **Domain .gr: 24€/έτος**.
5. Customer pays through Stripe one-time Checkout.
6. Stripe webhook receives `checkout.session.completed`.
7. Vitrina records the domain order as `paid`.
8. If `DOMAIN_REGISTRAR=papaki`, Vitrina attempts registrar purchase.
9. After successful purchase, Vitrina creates/updates Cloudflare DNS:
   - `www` → Cloudflare Pages project
   - `api` → Railway backend
10. Domain order becomes `active`.

If no registrar adapter is configured, paid orders remain `paid` and must be
fulfilled manually.

## Files

| File | Responsibility |
|---|---|
| `web/connect.html` | Domain selection UI and Stripe redirect |
| `src/main.py` | `/domain/suggest`, `/domain/check`, `/domain/create-checkout`, protected `/domain/purchase` |
| `src/domain.py` | Domain suggestions, registrar call, Cloudflare zone/DNS setup |
| `src/registrars.py` | Registrar adapter layer (`ManualRegistrar`, `PapakiRegistrar`) |
| `src/stripe_webhook.py` | Handles domain payment webhook and triggers purchase/setup |
| `src/db.py` | Saves domain orders and final domains |
| `db/schema.sql` | Full schema reference |
| `db/add_domains.sql` | `domains` tracking table migration |
| `db/add_domain_orders.sql` | `domain_orders` checkout table migration |

## Database

Run these migrations in Supabase SQL Editor:

1. `db/add_domains.sql`
2. `db/add_domain_orders.sql`

The `domain_orders` migration creates:

```sql
create table if not exists public.domain_orders (
  id                  uuid primary key default gen_random_uuid(),
  client_id           uuid references public.clients(id) on delete cascade,
  domain              text not null,
  amount_cents        int not null default 2400,
  currency            text not null default 'eur',
  stripe_session_id   text unique,
  status              text not null default 'pending',
  error               text,
  created_at          timestamptz default now(),
  updated_at          timestamptz default now()
);

create index if not exists idx_domain_orders_client on public.domain_orders(client_id);
create index if not exists idx_domain_orders_status on public.domain_orders(status);

alter table public.domain_orders enable row level security;
```

Statuses:

- `pending`: order row created.
- `checkout_created`: Stripe session created.
- `paid`: Stripe payment completed, no registrar success yet.
- `active`: registrar purchase and DNS setup completed.
- `failed`: registrar/DNS step failed; inspect `error`.

## Environment Variables

Required for Stripe domain checkout:

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

Required for Cloudflare DNS setup:

```env
CF_ACCOUNT_ID=
CF_API_TOKEN=
```

Domain automation mode:

```env
DOMAIN_REGISTRAR=manual
DOMAIN_ADMIN_TOKEN=
```

For Papaki once official reseller docs/credentials are available:

```env
DOMAIN_REGISTRAR=papaki
PAPAKI_API_BASE=
PAPAKI_API_KEY=
PAPAKI_RESELLER_ID=
PAPAKI_CONTACT_ID=
```

Keep `DOMAIN_REGISTRAR=manual` until Papaki endpoints and payloads are confirmed.

## Papaki Adapter Status

`src/registrars.py` includes `PapakiRegistrar`, but the endpoint paths are a
conservative placeholder contract:

- `GET /domains/check?domain=example.gr`
- `POST /domains/register`

Do not assume those are production-correct. The public third-party reference to
Papaki GoldResellers JSON API points to GitHub, but that URL currently returns
404. Before live registration:

1. Get official Papaki reseller/API docs from Papaki.
2. Confirm authentication format.
3. Confirm availability endpoint.
4. Confirm registration endpoint and required contact payload.
5. Confirm nameserver update flow.
6. Add a sandbox/test call if Papaki supports it.
7. Only then set `DOMAIN_REGISTRAR=papaki` in Railway.

## Safety Rules

- Never put Papaki or Stripe secrets in repo files.
- Never register a domain directly from frontend.
- `/domain/purchase` is protected by `DOMAIN_ADMIN_TOKEN` and should stay admin/internal.
- Public user flow must go through `/domain/create-checkout`.
- If registrar purchase fails after payment, keep order as `failed` with `error`;
  do not retry blindly without checking whether the registrar charged/created the domain.
- Use idempotent checks before retrying a failed domain registration.

## Koutrakis Demo

Chosen domain:

```text
koutrakiskouzines.gr
```

Price to customer:

```text
24€/έτος
```

Current state:

- Local site canonical/OG/JSON-LD uses `https://koutrakiskouzines.gr`.
- Domain has not been purchased yet.
- Full automatic `.gr` purchase waits for Papaki/Greek registrar API credentials.

## Agent Checklist

Before changing domain code:

- Read this file.
- Check `STATUS.md`.
- Check `src/registrars.py`.
- Check whether `DOMAIN_REGISTRAR` is `manual` or `papaki`.
- Do not change Stripe checkout price without updating docs and pricing.
- Do not claim full `.gr` automation is live until a real Papaki test purchase has passed.
