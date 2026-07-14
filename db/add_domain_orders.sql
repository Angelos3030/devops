-- Migration: domain checkout / purchase orders
-- Run in Supabase SQL Editor for project `vitrina`.
--
-- Notes:
-- - This table is written by the server with the Supabase service_role key.
-- - Keep RLS enabled. Do not expose customer/domain payment state to anon clients.
-- - Supabase changed defaults in 2026 so new public tables might not be exposed to
--   the Data API automatically; that is fine for this table because the backend
--   should be the only writer/reader.

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
