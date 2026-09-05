-- Ένας κανόνας, ένα αντικείμενο: η μοναδικότητα του idempotency key.
--
-- ΤΙ ΣΥΜΒΑΙΝΕΙ. Το ΣΗΜΕΡΙΝΟ 0003 δηλώνει inline `UNIQUE(client_id,
-- idempotency_key)`, που η PostgreSQL υλοποιεί ως περιορισμό + δικό του index
-- με όνομα `site_revisions_client_id_idempotency_key_key`. Το 0004 φτιάχνει
-- ΞΕΧΩΡΙΣΤΑ τον μοναδικό index `site_revisions_client_idempotency_key`.
--
-- Σε βάση χτισμένη από το ΠΑΛΙΟ 0003 (δηλαδή το staging) υπάρχει μόνο ο
-- index του 0004: το τότε 0003 δεν είχε τον inline περιορισμό. Σε κάθε
-- σημερινή εγκατάσταση υπάρχουν ΚΑΙ ΤΑ ΔΥΟ — ίδιος κανόνας, δύο φορές
-- αποθηκευμένος και δύο φορές συντηρούμενος σε κάθε εγγραφή.
--
-- Μετρήθηκε ως η ΜΟΝΗ διαφορά που απέμενε ανάμεσα σε καθαρή εγκατάσταση και
-- στο σημερινό staging, αφού εξαιρεθούν οι τεκμηριωμένες legacy στήλες.
--
-- ΤΟ ΣΥΜΒΟΛΑΙΟ ΤΟΥ STAGING ΕΙΝΑΙ Η ΑΝΑΦΟΡΑ: κρατάμε τον index του 0004 και
-- αφαιρούμε τον διπλό περιορισμό. Στο staging είναι no-op — δεν υπάρχει.
--
-- ΑΣΦΑΛΕΙΑ: ο περιορισμός αφαιρείται ΜΟΝΟ αν ο index του 0004 υπάρχει και
-- είναι όντως μοναδικός. Αλλιώς δεν αγγίζεται τίποτα — δεν επιτρέπεται να
-- μείνει ο πίνακας χωρίς καμία επιβολή, γιατί τότε ένα διπλό webhook θα
-- έγραφε δεύτερη αναθεώρηση.

DO $$
DECLARE
  has_index boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1
    FROM pg_index i
    JOIN pg_class c ON c.oid = i.indexrelid
    JOIN pg_class t ON t.oid = i.indrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = 'public'
      AND t.relname = 'site_revisions'
      AND c.relname = 'site_revisions_client_idempotency_key'
      AND i.indisunique
  ) INTO has_index;

  IF has_index THEN
    ALTER TABLE public.site_revisions
      DROP CONSTRAINT IF EXISTS site_revisions_client_id_idempotency_key_key;
  ELSE
    RAISE NOTICE 'Ο index του 0004 λείπει — ο διπλός περιορισμός ΜΕΝΕΙ.';
  END IF;
END
$$;
