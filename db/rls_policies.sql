-- RLS Policies για Vitrina (Supabase)
--
-- ⚠️⚠️ ΠΡΙΝ ΤΟ ΤΡΕΞΕΙΣ — ΚΡΙΣΙΜΟ:
--   Ο server ΠΡΕΠΕΙ να χρησιμοποιεί **service_role** key (bypasses RLS).
--   Railway → devops → Variables → `SUPABASE_KEY` πρέπει να είναι το service_role JWT (ξεκινά `eyJ...`).
--   ΑΝ είναι anon/publishable → μόλις ενεργοποιηθεί το RLS, **ΟΛΟ ΤΟ BACKEND ΣΠΑΕΙ** (403/500).
--   Μετά το τρέξιμο, τεστάρισε αμέσως:
--     curl https://devops-production-d563.up.railway.app/clients/lookup?email=test@x.gr   → πρέπει 200
--   Αν σπάσει → βάλε το service_role key στο Railway και ξαναδοκίμασε.
--
-- Μοντέλο: service_role bypasses RLS· το anon key (frontend) αποκλείεται από όλα.
-- Δεν χρειάζονται policies — enable + default deny.

ALTER TABLE clients          ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites             ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_assets    ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_accounts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts             ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains          ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_orders    ENABLE ROW LEVEL SECURITY;

-- Explicit deny για anon (δεν χρειάζεται αν δεν υπάρχει policy — default deny)
-- Αφήνουμε χωρίς policies: service_role bypasses, anon blocked.

-- Επαλήθευση: μετά το τρέξιμο, οι πίνακες πρέπει να έχουν RLS: enabled
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables WHERE schemaname = 'public';
