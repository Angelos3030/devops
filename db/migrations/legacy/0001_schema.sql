-- Supabase schema για το Παρέα AI
-- Τρέξε στο Supabase SQL Editor.

-- Πελάτες
create table if not exists clients (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,
  business_type text not null,            -- ταβέρνα, υδραυλικός, δικηγόρος...
  city          text not null,
  phone         text,
  address       text,
  email         text,
  status        text not null default 'trial',   -- trial | active | paused | cancelled
  plan          text default 'starter',          -- starter(9.90) | social(49) | premium(79)
  created_at    timestamptz default now()
);

-- Brand profile (JSON από το brand-builder-gr)
create table if not exists brand_profiles (
  client_id   uuid primary key references clients(id) on delete cascade,
  profile     jsonb not null,            -- {tone, colors, fonts, themes, hashtags}
  updated_at  timestamptz default now()
);

-- Sites
create table if not exists sites (
  id          uuid primary key default gen_random_uuid(),
  client_id   uuid references clients(id) on delete cascade,
  url         text,                       -- live URL (Cloudflare Pages)
  preset      text,                       -- ποιο preset χρησιμοποιήθηκε
  chosen_variant int,                     -- ποια από τις 3 επιλογές
  html        text,                       -- το τελικό HTML
  created_at  timestamptz default now()
);

-- Assets που δίνει ο πελάτης για site/social:
-- φωτογραφίες, λογότυπο, βιογραφικό/ιστορία, μενού, τιμοκατάλογος, before/after κ.λπ.
create table if not exists client_assets (
  id          uuid primary key default gen_random_uuid(),
  client_id   uuid references clients(id) on delete cascade,
  type        text not null,              -- photo | logo | bio | menu | price_list | before_after | document | other
  title       text,
  content     text,                       -- για bio/κείμενα ή σημειώσεις
  url         text,                       -- public/signed URL αν ανέβηκε σε storage ή δόθηκε link
  usage       text default 'site',         -- site | social | ads | all
  rights_ok   boolean default false,       -- ο πελάτης δηλώνει ότι έχει δικαίωμα χρήσης
  created_at  timestamptz default now()
);

-- Social credentials (direct Graph API path — αποθηκεύει long-lived page token)
-- ⚠️  Σε production κρυπτογράφησε το page_token (πχ pgcrypto ή app-level AES).
create table if not exists social_accounts (
  client_id    uuid primary key references clients(id) on delete cascade,
  fb_page_id   text not null,
  page_token   text not null,             -- long-lived Page token (~60 μέρες)
  ig_user_id   text,                      -- null αν δεν υπάρχει IG Business
  connected_at timestamptz default now()
);

-- Αν αναβαθμίζεις υπάρχον DB (είχε vault_id):
-- alter table social_accounts add column if not exists page_token text;
-- alter table social_accounts drop column if exists vault_id;

-- Posts (ιστορικό + προγραμματισμός)
create table if not exists posts (
  id          uuid primary key default gen_random_uuid(),
  client_id   uuid references clients(id) on delete cascade,
  caption     text,
  image_url   text,
  status      text default 'pending_approval', -- draft | pending_approval | scheduled | publishing | published | failed | rejected
  targets     jsonb not null default '["facebook", "instagram"]'::jsonb,
  approval_required boolean not null default true,
  approved_at timestamptz,
  approved_by text,
  rejected_at timestamptz,
  attempts    int not null default 0,
  max_attempts int not null default 3,
  last_error  text,
  fb_post_id  text,
  ig_post_id  text,
  scheduled_for timestamptz,
  published_at  timestamptz,
  created_at  timestamptz default now()
);

-- Αμετάβλητο audit trail για κάθε απόπειρα δημοσίευσης.
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

-- Συνδρομές (συγχρονισμός με Stripe)
create table if not exists subscriptions (
  client_id           uuid primary key references clients(id) on delete cascade,
  stripe_customer_id  text,
  stripe_sub_id       text,
  plan                text,
  status              text,               -- trialing | active | past_due | canceled
  current_period_end  timestamptz,
  updated_at          timestamptz default now()
);

-- Domains που αγοράστηκαν για πελάτες μέσω Papaki
create table if not exists domains (
  id                  uuid primary key default gen_random_uuid(),
  client_id           uuid references clients(id) on delete cascade,
  domain              text not null unique,
  registrar           text default 'papaki',
  cloudflare_zone_id  text,
  status              text default 'active',   -- active | expired | transferred
  registered_at       timestamptz default now(),
  expires_at          timestamptz
);

-- Domain checkout / purchase flow.
-- Ο πελάτης πρώτα πληρώνει το domain fee, μετά το webhook κάνει αγορά + DNS setup.
create table if not exists domain_orders (
  id                  uuid primary key default gen_random_uuid(),
  client_id           uuid references clients(id) on delete cascade,
  domain              text not null,
  amount_cents        int not null default 2400,
  currency            text not null default 'eur',
  stripe_session_id   text unique,
  status              text not null default 'pending', -- pending | checkout_created | paid | active | failed
  error               text,
  created_at          timestamptz default now(),
  updated_at          timestamptz default now()
);

create index if not exists idx_clients_status on clients(status);
create index if not exists idx_client_assets_client on client_assets(client_id);
create index if not exists idx_posts_client on posts(client_id);
create index if not exists idx_posts_scheduled on posts(scheduled_for) where status = 'scheduled';
create index if not exists idx_publish_logs_post on publish_logs(post_id, created_at desc);
create index if not exists idx_publish_logs_client on publish_logs(client_id);
create index if not exists idx_domain_orders_client on domain_orders(client_id);
create index if not exists idx_domain_orders_status on domain_orders(status);
