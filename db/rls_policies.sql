-- RLS Policies για Vitrina (Supabase)
-- Τρέξε στο SQL Editor ΑΦΟΥ βάλεις service_role key στον server.
--
-- Μοντέλο: ο server χρησιμοποιεί service_role key → bypasses RLS αυτόματα.
-- Το anon key (frontend) αποκλείεται από όλα — κανένα δεδομένο δεν εκτίθεται.
-- Δεν χρειάζονται πολύπλοκα policies — απλά enable + block anon.

ALTER TABLE clients          ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites             ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_assets    ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_accounts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts             ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains          ENABLE ROW LEVEL SECURITY;

-- Explicit deny για anon (δεν χρειάζεται αν δεν υπάρχει policy — default deny)
-- Αφήνουμε χωρίς policies: service_role bypasses, anon blocked.

-- Επαλήθευση: μετά το τρέξιμο, οι πίνακες πρέπει να έχουν RLS: enabled
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables WHERE schemaname = 'public';
