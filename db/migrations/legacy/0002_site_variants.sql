-- Vitrina premium design engine: store the 3 generated site variants per client
-- and record which one the client approved. Run in Supabase SQL Editor.

-- 1) which layout the client approved (studio | commerce | atelier)
alter table public.clients
  add column if not exists selected_layout text;

-- 2) the 3 generated variants (preview HTML) per client
create table if not exists public.site_variants (
  id          uuid primary key default gen_random_uuid(),
  client_id   uuid not null references public.clients(id) on delete cascade,
  layout      text not null,                 -- studio | commerce | atelier
  html        text not null,
  recommended boolean not null default false,
  status      text not null default 'preview', -- preview | selected
  created_at  timestamptz not null default now(),
  unique (client_id, layout)
);

create index if not exists site_variants_client_idx
  on public.site_variants (client_id);

-- 3) RLS: service_role bypasses automatically; block anon by default.
alter table public.site_variants enable row level security;
