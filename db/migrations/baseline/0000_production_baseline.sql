-- 0000 — BASELINE ΠΑΡΑΓΩΓΗΣ
--
-- Παράχθηκε αυτόματα από το πραγματικό σχήμα της παραγωγής
-- (scripts/make_baseline.py από db/snapshots/production.json).
--
-- ΓΙΑΤΙ: υπήρχαν δύο ανεξάρτητα συστήματα migrations — τα versioned αρχεία
-- του repo και το ιστορικό του Supabase. Το staging είχε αποκλίνει σε 28
-- πίνακες έναντι 12, ΚΑΙ η παραγωγή είχε index που δεν υπήρχε πουθενά στα
-- αρχεία μας. Αυτό το αρχείο είναι το σημείο μηδέν της ενιαίας ακολουθίας.
--
-- ΔΕΝ εφαρμόζεται στην παραγωγή: η παραγωγή ΕΧΕΙ ήδη αυτό το σχήμα. Χρησιμεύει
-- για να στηθεί καθαρό staging και για τη δοκιμή επαναφοράς.
--
-- Ασφαλές να ξανατρέξει (IF NOT EXISTS παντού).

-- Ρόλοι που περιμένει το Supabase. Σε καθαρό Postgres δεν υπάρχουν και τα
-- GRANT σκάνε — αυτό εμπόδιζε την ανάκτηση εκτός Supabase.
DO $$ BEGIN CREATE ROLE anon          NOLOGIN NOINHERIT;
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE ROLE authenticated NOLOGIN NOINHERIT;
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE ROLE service_role  NOLOGIN NOINHERIT BYPASSRLS;
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── clients ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "clients" (
  "address" text,
  "business_type" text NOT NULL,
  "city" text NOT NULL,
  "created_at" timestamp with time zone DEFAULT now(),
  "email" text,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "name" text NOT NULL,
  "phone" text,
  "plan" text DEFAULT 'starter'::text,
  "status" text DEFAULT 'trial'::text NOT NULL
);

-- ─── brand_profiles ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "brand_profiles" (
  "client_id" uuid NOT NULL,
  "profile" jsonb NOT NULL,
  "updated_at" timestamp with time zone DEFAULT now()
);

-- ─── client_assets ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "client_assets" (
  "client_id" uuid,
  "content" text,
  "created_at" timestamp with time zone DEFAULT now(),
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "rights_ok" boolean DEFAULT false,
  "title" text,
  "type" text NOT NULL,
  "url" text,
  "usage" text DEFAULT 'site'::text
);

-- ─── client_site_claims ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS "client_site_claims" (
  "claimed_at" timestamp with time zone,
  "claimed_by" text,
  "client_id" uuid NOT NULL,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL,
  "expires_at" timestamp with time zone NOT NULL,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "token_hash" text NOT NULL
);

-- ─── domain_orders ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "domain_orders" (
  "amount_cents" integer DEFAULT 2400 NOT NULL,
  "client_id" uuid,
  "created_at" timestamp with time zone DEFAULT now(),
  "currency" text DEFAULT 'eur'::text NOT NULL,
  "domain" text NOT NULL,
  "error" text,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "status" text DEFAULT 'pending'::text NOT NULL,
  "stripe_session_id" text,
  "updated_at" timestamp with time zone DEFAULT now()
);

-- ─── domains ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "domains" (
  "client_id" uuid,
  "cloudflare_zone_id" text,
  "domain" text NOT NULL,
  "expires_at" timestamp with time zone,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "registered_at" timestamp with time zone DEFAULT now(),
  "registrar" text DEFAULT 'papaki'::text,
  "status" text DEFAULT 'active'::text
);

-- ─── posts ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "posts" (
  "approval_required" boolean DEFAULT true NOT NULL,
  "approved_at" timestamp with time zone,
  "approved_by" text,
  "attempts" integer DEFAULT 0 NOT NULL,
  "caption" text,
  "client_id" uuid,
  "created_at" timestamp with time zone DEFAULT now(),
  "fb_post_id" text,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "ig_post_id" text,
  "image_url" text,
  "last_error" text,
  "max_attempts" integer DEFAULT 3 NOT NULL,
  "published_at" timestamp with time zone,
  "rejected_at" timestamp with time zone,
  "scheduled_for" timestamp with time zone,
  "status" text DEFAULT 'pending_approval'::text,
  "targets" jsonb DEFAULT '["facebook", "instagram"]'::jsonb NOT NULL
);

-- ─── site_content ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "site_content" (
  "client_id" uuid NOT NULL,
  "content" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "updated_at" timestamp with time zone DEFAULT now() NOT NULL
);

-- ─── sites ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "sites" (
  "chosen_variant" integer,
  "client_id" uuid,
  "created_at" timestamp with time zone DEFAULT now(),
  "html" text,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "preset" text,
  "url" text
);

-- ─── social_accounts ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "social_accounts" (
  "client_id" uuid NOT NULL,
  "connected_at" timestamp with time zone DEFAULT now(),
  "fb_page_id" text NOT NULL,
  "ig_user_id" text,
  "page_token" text NOT NULL
);

-- ─── subscriptions ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "subscriptions" (
  "client_id" uuid NOT NULL,
  "current_period_end" timestamp with time zone,
  "plan" text,
  "status" text,
  "stripe_customer_id" text,
  "stripe_sub_id" text,
  "updated_at" timestamp with time zone DEFAULT now()
);

-- ─── publish_logs ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "publish_logs" (
  "client_id" uuid NOT NULL,
  "created_at" timestamp with time zone DEFAULT now(),
  "dry_run" boolean DEFAULT false NOT NULL,
  "error" text,
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "post_id" uuid NOT NULL,
  "result" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "success" boolean DEFAULT false NOT NULL
);

-- ─── Περιορισμοί ────────────────────────────────────────────────
-- Τα PRIMARY KEY/UNIQUE δημιουργούνται εδώ ώστε η σειρά των πινάκων
-- να μην εμποδίζει τα foreign keys.
DO $$ BEGIN ALTER TABLE "clients" ADD CONSTRAINT "clients_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "brand_profiles" ADD CONSTRAINT "brand_profiles_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "brand_profiles" ADD CONSTRAINT "brand_profiles_pkey" PRIMARY KEY (client_id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "client_assets" ADD CONSTRAINT "client_assets_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "client_assets" ADD CONSTRAINT "client_assets_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "client_site_claims" ADD CONSTRAINT "client_site_claims_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "client_site_claims" ADD CONSTRAINT "client_site_claims_client_id_key" UNIQUE (client_id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "client_site_claims" ADD CONSTRAINT "client_site_claims_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "client_site_claims" ADD CONSTRAINT "client_site_claims_token_hash_key" UNIQUE (token_hash);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "domain_orders" ADD CONSTRAINT "domain_orders_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "domain_orders" ADD CONSTRAINT "domain_orders_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "domain_orders" ADD CONSTRAINT "domain_orders_stripe_session_id_key" UNIQUE (stripe_session_id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "domains" ADD CONSTRAINT "domains_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "domains" ADD CONSTRAINT "domains_domain_key" UNIQUE (domain);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "domains" ADD CONSTRAINT "domains_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "posts" ADD CONSTRAINT "posts_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "posts" ADD CONSTRAINT "posts_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "site_content" ADD CONSTRAINT "site_content_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "site_content" ADD CONSTRAINT "site_content_pkey" PRIMARY KEY (client_id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "sites" ADD CONSTRAINT "sites_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "sites" ADD CONSTRAINT "sites_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "social_accounts" ADD CONSTRAINT "social_accounts_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "social_accounts" ADD CONSTRAINT "social_accounts_pkey" PRIMARY KEY (client_id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "subscriptions" ADD CONSTRAINT "subscriptions_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "subscriptions" ADD CONSTRAINT "subscriptions_pkey" PRIMARY KEY (client_id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "publish_logs" ADD CONSTRAINT "publish_logs_client_id_fkey" FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "publish_logs" ADD CONSTRAINT "publish_logs_pkey" PRIMARY KEY (id);
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE "publish_logs" ADD CONSTRAINT "publish_logs_post_id_fkey" FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; WHEN duplicate_table THEN NULL; END $$;

-- ─── Ευρετήρια ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_clients_status ON public.clients USING btree (status);
CREATE INDEX IF NOT EXISTS idx_client_assets_client ON public.client_assets USING btree (client_id);
CREATE INDEX IF NOT EXISTS idx_client_site_claims_active ON public.client_site_claims USING btree (token_hash, expires_at) WHERE (claimed_at IS NULL);
CREATE INDEX IF NOT EXISTS idx_domain_orders_client ON public.domain_orders USING btree (client_id);
CREATE INDEX IF NOT EXISTS idx_domain_orders_status ON public.domain_orders USING btree (status);
CREATE INDEX IF NOT EXISTS idx_domains_client ON public.domains USING btree (client_id);
CREATE INDEX IF NOT EXISTS idx_domains_status ON public.domains USING btree (status);
CREATE INDEX IF NOT EXISTS idx_posts_client ON public.posts USING btree (client_id);
CREATE INDEX IF NOT EXISTS idx_posts_queue ON public.posts USING btree (status, scheduled_for) WHERE (status = ANY (ARRAY['scheduled'::text, 'publishing'::text]));
CREATE INDEX IF NOT EXISTS idx_posts_scheduled ON public.posts USING btree (scheduled_for) WHERE (status = 'scheduled'::text);
CREATE INDEX IF NOT EXISTS site_content_updated_idx ON public.site_content USING btree (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_publish_logs_client ON public.publish_logs USING btree (client_id);
CREATE INDEX IF NOT EXISTS idx_publish_logs_post ON public.publish_logs USING btree (post_id, created_at DESC);

-- ─── Row Level Security ─────────────────────────────────────────
ALTER TABLE "clients" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "brand_profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "client_assets" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "client_site_claims" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "domain_orders" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "domains" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "posts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "site_content" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "sites" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "social_accounts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "subscriptions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "publish_logs" ENABLE ROW LEVEL SECURITY;
