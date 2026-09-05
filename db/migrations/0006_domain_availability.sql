-- Αίτημα domain: τι είδε ο πελάτης, πότε, και από ποια πηγή.
--
-- ΓΙΑΤΙ. Η διαθεσιμότητα είναι ΦΩΤΟΓΡΑΦΙΑ ΜΙΑΣ ΣΤΙΓΜΗΣ. Ανάμεσα στο «φαίνεται
-- ελεύθερο» και στην αγορά μεσολαβεί άνθρωπος — λεπτά ή ώρες. Στο διάστημα
-- αυτό το domain μπορεί να κατοχυρωθεί από τρίτον. Χωρίς αποθηκευμένο
-- αποτέλεσμα ΚΑΙ χρόνο, ο operator δεν ξέρει αν αυτό που βλέπει είναι φρέσκο
-- ή δύο ημερών, και ο πελάτης δεν έχει απόδειξη τι του δείχτηκε.
--
-- Μόνο προσθετικές αλλαγές. Ο παλιός κώδικας συνεχίζει να δουλεύει.

ALTER TABLE public.domain_orders
  ADD COLUMN IF NOT EXISTS availability             text,
  ADD COLUMN IF NOT EXISTS availability_source      text,
  ADD COLUMN IF NOT EXISTS availability_checked_at  timestamptz,
  ADD COLUMN IF NOT EXISTS requested_at             timestamptz,
  -- Ο δεύτερος έλεγχος, από τον operator, ΑΜΕΣΩΣ πριν την αγορά. Χωριστό
  -- πεδίο επίτηδες: το πρώτο είναι τι είδε ο πελάτης, το δεύτερο είναι τι
  -- ισχύει τη στιγμή της εκτέλεσης. Δεν επιτρέπεται να επικαλύψει το πρώτο.
  ADD COLUMN IF NOT EXISTS fulfillment_availability        text,
  ADD COLUMN IF NOT EXISTS fulfillment_checked_at          timestamptz;

COMMENT ON COLUMN public.domain_orders.availability IS
  'available | unavailable | unknown — τι είδε ο ΠΕΛΑΤΗΣ όταν υπέβαλε.';
COMMENT ON COLUMN public.domain_orders.availability_source IS
  'Ποια αυθεντική πηγή απάντησε, π.χ. rdap:rdap.verisign.com ή registrar:pointer.';
COMMENT ON COLUMN public.domain_orders.fulfillment_availability IS
  'Ο επανέλεγχος πριν την αγορά. ΠΟΤΕ δεν αντιγράφεται από το πεδίο του πελάτη.';

-- Λεξιλόγιο καταστάσεων, ρητά. NOT VALID: ισχύει για νέες/ενημερωμένες
-- γραμμές, δεν ελέγχει αναδρομικά ό,τι έγραψε ο παλιός κώδικας — ώστε η
-- μετάβαση να μην μπορεί να αποτύχει σε υπάρχοντα δεδομένα.
ALTER TABLE public.domain_orders
  DROP CONSTRAINT IF EXISTS domain_orders_status_vocab;
ALTER TABLE public.domain_orders
  ADD CONSTRAINT domain_orders_status_vocab CHECK (
    status IN (
      'pending',              -- δημιουργήθηκε, δεν έχει σταλεί τίποτα
      'checkout_created',     -- υπάρχει Stripe session, εκκρεμεί πληρωμή
      'paid',                 -- η πληρωμή επιβεβαιώθηκε
      'pending_fulfillment',  -- αναμονή χειροκίνητης αγοράς από operator
      'active',               -- αγοράστηκε και συνδέθηκε
      'failed',               -- απέτυχε (η αιτία στο error)
      'unavailable_at_fulfillment'  -- πιάστηκε ΠΡΙΝ προλάβουμε· χρειάζεται
                                    -- επιστροφή χρημάτων ή νέα επιλογή
    )
  ) NOT VALID;

ALTER TABLE public.domain_orders
  DROP CONSTRAINT IF EXISTS domain_orders_availability_vocab;
ALTER TABLE public.domain_orders
  ADD CONSTRAINT domain_orders_availability_vocab CHECK (
    availability IS NULL OR availability IN ('available', 'unavailable', 'unknown')
  ) NOT VALID;

-- Ο operator δουλεύει ουρά: «τι περιμένει, με το παλαιότερο πρώτο».
CREATE INDEX IF NOT EXISTS domain_orders_fulfillment_queue
  ON public.domain_orders (status, requested_at)
  WHERE status = 'pending_fulfillment';

-- Ένα ενεργό αίτημα ανά (πελάτη, domain). Οι κλειστές καταστάσεις εξαιρούνται,
-- ώστε ο πελάτης να μπορεί να ξαναζητήσει domain που είχε αποτύχει.
CREATE UNIQUE INDEX IF NOT EXISTS domain_orders_one_open_request
  ON public.domain_orders (client_id, domain)
  WHERE status IN ('pending', 'checkout_created', 'paid', 'pending_fulfillment');
