-- Δικαιώματα `service_role` — το κενό που κάνει την καθαρή εγκατάσταση άχρηστη.
--
-- ΤΙ ΜΕΤΡΗΘΗΚΕ. Καθαρή βάση PostgreSQL 17, όλα τα migrations από το μηδέν:
-- **25 από τους 27 πίνακες δεν είχαν ΚΑΝΕΝΑ δικαίωμα για τον `service_role`**.
-- Μόνο τα `site_revisions` και `client_site_claims` είχαν, επειδή τα migrations
-- τους περιέχουν ρητό GRANT. Το API συνδέεται ΩΣ `service_role`: σε τέτοια
-- βάση δεν μπορεί να διαβάσει ούτε τον πίνακα `clients`.
--
-- ΓΙΑΤΙ ΔΕΝ ΦΑΙΝΟΤΑΝ. Το staging και η παραγωγή τα έχουν ήδη, από τα default
-- privileges που βάζει το ίδιο το Supabase όταν στήνεται το project. Το
-- `0000_production_baseline.sql` παρήχθη από αποτύπωμα σχήματος — και το
-- αποτύπωμα δεν περιλάμβανε δικαιώματα. Άρα το κενό υπάρχει μόνο εκεί που
-- κανείς δεν κοίταξε: σε βάση φτιαγμένη ΑΠΟ τα migrations, δηλαδή στην
-- ανάκτηση από καταστροφή.
--
-- ΑΣΦΑΛΕΣ ΟΠΟΥ ΥΠΑΡΧΟΥΝ ΗΔΗ: το GRANT σε ήδη δοσμένο δικαίωμα είναι no-op.
-- Σε staging και παραγωγή αυτό το αρχείο δεν αλλάζει τίποτα.
--
-- ΤΙ ΔΕΝ ΚΑΝΕΙ, ΕΠΙΤΗΔΕΣ: δεν αφαιρεί τίποτα από `anon`/`authenticated`.
--
-- Μετρήθηκε: η παραγωγή έχει **154 τέτοια δικαιώματα** (defaults του Supabase),
-- το staging κανένα. Ο browser client (`sites/lib/supabase.js`) τα χρησιμοποιεί
-- ΜΟΝΟ για login — δεν κάνει πουθενά `.from()` — οπότε η αφαίρεσή τους μοιάζει
-- ασφαλής. Μοιάζει· δεν αποδείχθηκε. Ένα REVOKE 154 δικαιωμάτων στην παραγωγή
-- είναι απόφαση ασφαλείας που παίρνεται συνειδητά και δοκιμάζεται χωριστά, όχι
-- παρενέργεια ενός αρχείου που λέγεται «grants». Μένει για δικό του migration.

DO $$
DECLARE
  t record;
BEGIN
  FOR t IN
    SELECT c.relname
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r'
  LOOP
    EXECUTE format(
      'GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER '
      'ON public.%I TO service_role', t.relname);
  END LOOP;
END
$$;

-- Sequences: όπου υπάρχουν (bigserial), ο service_role πρέπει να μπορεί να
-- τραβήξει τιμή, αλλιώς το INSERT αποτυγχάνει με «permission denied».
DO $$
DECLARE
  s record;
BEGIN
  FOR s IN
    SELECT c.relname
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'S'
  LOOP
    EXECUTE format('GRANT USAGE, SELECT ON SEQUENCE public.%I TO service_role',
                   s.relname);
  END LOOP;
END
$$;

-- Και για ό,τι δημιουργηθεί ΑΡΓΟΤΕΡΑ από τον ίδιο ιδιοκτήτη — ώστε το επόμενο
-- migration να μη χρειάζεται να θυμηθεί ξανά το ίδιο.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
  ON TABLES TO service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO service_role;
