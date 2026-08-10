-- Vitrina Social Engine v1
-- Safe to run more than once in Supabase SQL Editor.

alter table posts alter column status set default 'pending_approval';
alter table posts add column if not exists targets jsonb not null default '["facebook", "instagram"]'::jsonb;
alter table posts add column if not exists approval_required boolean not null default true;
alter table posts add column if not exists approved_at timestamptz;
alter table posts add column if not exists approved_by text;
alter table posts add column if not exists rejected_at timestamptz;
alter table posts add column if not exists attempts int not null default 0;
alter table posts add column if not exists max_attempts int not null default 3;
alter table posts add column if not exists last_error text;

create table if not exists publish_logs (
  id          uuid primary key default gen_random_uuid(),
  post_id     uuid not null references posts(id) on delete cascade,
  client_id   uuid not null references clients(id) on delete cascade,
  dry_run     boolean not null default false,
  success     boolean not null default false,
  result      jsonb not null default '{}'::jsonb,
  error       text,
  created_at  timestamptz default now()
);

alter table publish_logs enable row level security;
create index if not exists idx_publish_logs_post on publish_logs(post_id, created_at desc);
create index if not exists idx_publish_logs_client on publish_logs(client_id);
create index if not exists idx_posts_queue on posts(status, scheduled_for)
  where status in ('scheduled', 'publishing');
