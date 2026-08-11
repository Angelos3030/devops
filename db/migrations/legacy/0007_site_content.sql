-- site_content — ό,τι επεξεργάζεται ο πελάτης από το dashboard.
--
-- ΓΙΑΤΙ ΥΠΑΡΧΕΙ ΞΕΧΩΡΙΣΤΑ: ο πίνακας υπήρχε στην ΠΑΡΑΓΩΓΗ αλλά ΟΧΙ σε κανένα
-- αρχείο SQL — είχε φτιαχτεί κάποτε με το χέρι στο SQL Editor. Φάνηκε την πρώτη
-- φορά που στήθηκε δεύτερη βάση από τα migrations: το staging βγήκε χωρίς αυτόν
-- και το check_env το έπιασε.
--
-- Η δομή είναι αντιγραμμένη ΑΚΡΙΒΩΣ από την παραγωγή (information_schema +
-- pg_constraint), όχι από μνήμη.
--
-- Ασφαλές να ξανατρέξει.

CREATE TABLE IF NOT EXISTS site_content (
  client_id   uuid        PRIMARY KEY REFERENCES clients(id) ON DELETE CASCADE,
  content     jsonb       NOT NULL DEFAULT '{}'::jsonb,
  updated_at  timestamptz NOT NULL DEFAULT now()
);

-- RLS: η παραγωγή το έχει ενεργό σε ΟΛΟΥΣ τους πίνακες. Χωρίς αυτή τη γραμμή το
-- staging είχε το site_content εκτεθειμένο — το anon key είναι δημόσιο στον
-- browser, οπότε θα διάβαζε κανείς το περιεχόμενο κάθε πελάτη.
-- Το 0006 έτρεξε ΠΡΙΝ από αυτόν τον πίνακα, γι' αυτό δεν τον κάλυψε.
ALTER TABLE site_content ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE site_content IS
  'Δομημένο περιεχόμενο site ανά πελάτη — τα πεδία που αλλάζει ο ιδιοκτήτης.';
