-- Migration: purchased/customer domains
-- Run in Supabase SQL Editor for project `vitrina`.
--
-- This tracks domains after purchase/activation. Registration itself happens via
-- the configured registrar adapter, while Cloudflare handles DNS.

create table if not exists public.domains (
  id                  uuid primary key default gen_random_uuid(),
  client_id           uuid references public.clients(id) on delete cascade,
  domain              text not null unique,
  registrar           text default 'papaki',
  cloudflare_zone_id  text,
  status              text default 'active',
  registered_at       timestamptz default now(),
  expires_at          timestamptz
);

create index if not exists idx_domains_client on public.domains(client_id);
create index if not exists idx_domains_status on public.domains(status);

alter table public.domains enable row level security;
