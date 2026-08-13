-- 0002 — Σημασιολογία εικόνων: τι ΕΙΝΑΙ κάθε asset, και ποια πολιτική ακολουθεί το site.
--
-- Γιατί: το benchmark των 10 sites έδειξε ότι μια stock φωτογραφία κάτω από τον
-- τίτλο «Ο χώρος μας» είναι ψέμα, ενώ η ίδια ως ατμόσφαιρα σε hero δεν είναι. Η
-- διαφορά δεν είναι στην εικόνα — είναι στο τι ΙΣΧΥΡΙΖΕΤΑΙ η θέση της. Χωρίς
-- αποθηκευμένη κλάση, ο renderer μαντεύει· και το μάντεμα δημοσιεύεται ως ισχυρισμός.
--
-- Συμβόλαιο: src/media_semantics.py

-- Expand: προσθετικό, με ασφαλές default. Υπάρχοντα assets δεν αλλάζουν σημασία.
ALTER TABLE public.client_assets
  ADD COLUMN IF NOT EXISTS media_class text;

-- Οι έξι κλάσεις του συμβολαίου. NULL = άγνωστη προέλευση, και αντιμετωπίζεται
-- ως δανεική: ό,τι δεν ξέρουμε ότι είναι αληθινό, δεν το παρουσιάζουμε ως αληθινό.
ALTER TABLE public.client_assets
  DROP CONSTRAINT IF EXISTS client_assets_media_class_check;
ALTER TABLE public.client_assets
  ADD CONSTRAINT client_assets_media_class_check
  CHECK (media_class IS NULL OR media_class IN (
    'REAL_BUSINESS', 'REAL_OWNER_PERSON', 'REAL_WORK', 'REAL_SPACE',
    'ILLUSTRATIVE', 'GENERATED'
  ));

COMMENT ON COLUMN public.client_assets.media_class IS
  'Τι δείχνει η εικόνα, δηλωμένο από τον πελάτη — όχι συμπερασμένο. Ενότητες '
  'ταυτότητας (πρόσωπο/ομάδα/χώρος/δουλειά) δέχονται μόνο REAL_*. Βλ. src/media_semantics.py';

-- Ό,τι ανέβασε ο πελάτης πριν υπάρξει το πεδίο ΕΙΝΑΙ δικό του υλικό — απλώς δεν
-- ξέρουμε τι δείχνει. Το πιο συντηρητικό αληθές: γενική φωτογραφία επιχείρησης.
UPDATE public.client_assets
   SET media_class = 'REAL_BUSINESS'
 WHERE media_class IS NULL
   AND type IN ('photo', 'image', 'gallery')
   AND url IS NOT NULL;

-- Πολιτική ανά site. 'real-only' = καμία δανεική εικόνα σε ενότητα ταυτότητας·
-- η σελίδα γίνεται τυπογραφική εκεί που λείπει πραγματικό υλικό.
-- Προεπιλογή NULL = η σημερινή συμπεριφορά, αμετάβλητη. Opt-in ανά site.
ALTER TABLE public.clients
  ADD COLUMN IF NOT EXISTS media_policy text;
ALTER TABLE public.clients
  DROP CONSTRAINT IF EXISTS clients_media_policy_check;
ALTER TABLE public.clients
  ADD CONSTRAINT clients_media_policy_check
  CHECK (media_policy IS NULL OR media_policy IN ('real-only'));

COMMENT ON COLUMN public.clients.media_policy IS
  'NULL = προηγούμενη συμπεριφορά (fallback εικόνες). ''real-only'' = μόνο δηλωμένο '
  'πραγματικό υλικό στις ενότητες ταυτότητας.';

CREATE INDEX IF NOT EXISTS client_assets_media_class_idx
  ON public.client_assets (client_id, media_class);
