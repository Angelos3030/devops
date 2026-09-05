-- Upgrade the legacy 0003 editor evidence table to the atomic draft editor.
-- Additive on purpose: legacy timestamp/publish_status columns remain readable.

ALTER TABLE public.site_content
  ADD COLUMN IF NOT EXISTS editor_version bigint NOT NULL DEFAULT 0;

ALTER TABLE public.site_revisions
  ADD COLUMN IF NOT EXISTS previous_revision_id uuid REFERENCES public.site_revisions(id),
  ADD COLUMN IF NOT EXISTS created_at timestamptz,
  ADD COLUMN IF NOT EXISTS operations jsonb,
  ADD COLUMN IF NOT EXISTS before_state jsonb,
  ADD COLUMN IF NOT EXISTS after_state jsonb,
  ADD COLUMN IF NOT EXISTS status text,
  ADD COLUMN IF NOT EXISTS version_before bigint,
  ADD COLUMN IF NOT EXISTS version_after bigint,
  ADD COLUMN IF NOT EXISTS idempotency_key text,
  ADD COLUMN IF NOT EXISTS undone_revision_id uuid REFERENCES public.site_revisions(id);

-- ΓΙΑΤΙ ΕΙΝΑΙ ΧΩΡΙΣΜΕΝΟ ΣΕ ΔΥΟ ΒΗΜΑΤΑ.
--
-- Αυτό το αρχείο γράφτηκε για να αναβαθμίσει τον πίνακα που έφτιαχνε το ΤΟΤΕ
-- 0003 — έναν «πίνακα τεκμηρίων» με στήλες `timestamp` και `publish_status`.
-- Το 0003 ξαναγράφτηκε αργότερα ώστε να φτιάχνει κατευθείαν την τελική μορφή,
-- και έπαψε να δημιουργεί εκείνες τις στήλες.
--
-- Έτσι η αρχική εντολή, που έγραφε `COALESCE(created_at, "timestamp", now())`,
-- ανέφερε στήλη που σε καθαρή βάση ΔΕΝ ΥΠΑΡΧΕΙ. Η PostgreSQL αναλύει το
-- UPDATE ολόκληρο πριν το εκτελέσει, οπότε έσκαγε αμέσως:
--
--     ✗ column "timestamp" does not exist
--
-- Μετρήθηκε: κάθε βάση χτισμένη από το μηδέν σταματούσε εδώ — άρα και η
-- ΠΑΡΑΓΩΓΗ, που δεν έχει καθόλου πίνακες editor.
--
-- Ο κανόνας: προαιρετική legacy στήλη δεν αναφέρεται ΠΟΤΕ πριν ελεγχθεί ότι
-- υπάρχει. Το βήμα 1 τρέχει μόνο εκεί που υπάρχει, με δυναμικό SQL (το
-- EXECUTE αναλύεται στην εκτέλεση, όχι στην ανάγνωση). Το βήμα 2 δεν την
-- αναφέρει καθόλου.
--
-- Το αποτέλεσμα είναι ΤΑΥΤΟΣΗΜΟ με το αρχικό `COALESCE(created_at,
-- "timestamp", now())` και στις δύο αφετηρίες:
--   created_at ήδη γεμάτο            -> μένει                (βήμα 2, COALESCE)
--   created_at κενό, timestamp γεμάτο -> παίρνει το timestamp (βήμα 1)
--   created_at κενό, timestamp κενό   -> παίρνει now()        (βήμα 2)
--   καθαρή βάση, χωρίς τη στήλη       -> now()                (βήμα 2)

-- Βήμα 1 — ΜΟΝΟ σε βάσεις με το legacy σχήμα.
DO $legacy_created_at$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'site_revisions'
      AND column_name = 'timestamp'
  ) THEN
    EXECUTE 'UPDATE public.site_revisions
             SET created_at = "timestamp"
             WHERE created_at IS NULL AND "timestamp" IS NOT NULL';
  END IF;
END
$legacy_created_at$;

-- Βήμα 2 — παντού. Καμία αναφορά σε legacy στήλη.
UPDATE public.site_revisions
SET created_at = COALESCE(created_at, now()),
    operations = COALESCE(operations, '[]'::jsonb),
    before_state = COALESCE(before_state, '{}'::jsonb),
    after_state = COALESCE(after_state, '{}'::jsonb),
    status = COALESCE(status, 'applied'),
    version_before = COALESCE(version_before, 0),
    version_after = COALESCE(version_after, 0),
    idempotency_key = COALESCE(idempotency_key, 'legacy-' || id::text);

ALTER TABLE public.site_revisions
  ALTER COLUMN created_at SET DEFAULT now(),
  ALTER COLUMN created_at SET NOT NULL,
  ALTER COLUMN operations SET DEFAULT '[]'::jsonb,
  ALTER COLUMN operations SET NOT NULL,
  ALTER COLUMN before_state SET NOT NULL,
  ALTER COLUMN after_state SET NOT NULL,
  ALTER COLUMN status SET DEFAULT 'applied',
  ALTER COLUMN status SET NOT NULL,
  ALTER COLUMN version_before SET NOT NULL,
  ALTER COLUMN version_after SET NOT NULL,
  ALTER COLUMN idempotency_key SET NOT NULL;

ALTER TABLE public.site_revisions DROP CONSTRAINT IF EXISTS site_revisions_source_check;
ALTER TABLE public.site_revisions DROP CONSTRAINT IF EXISTS site_revisions_status_check;
ALTER TABLE public.site_revisions DROP CONSTRAINT IF EXISTS site_revisions_operations_check;
ALTER TABLE public.site_revisions DROP CONSTRAINT IF EXISTS site_revisions_before_state_check;
ALTER TABLE public.site_revisions DROP CONSTRAINT IF EXISTS site_revisions_after_state_check;
ALTER TABLE public.site_revisions
  ADD CONSTRAINT site_revisions_source_check
    CHECK (source IN ('chat', 'manual', 'system', 'undo')),
  ADD CONSTRAINT site_revisions_status_check
    CHECK (status IN ('applied', 'undone')),
  ADD CONSTRAINT site_revisions_operations_check
    CHECK (jsonb_typeof(operations) = 'array'),
  ADD CONSTRAINT site_revisions_before_state_check
    CHECK (jsonb_typeof(before_state) = 'object'),
  ADD CONSTRAINT site_revisions_after_state_check
    CHECK (jsonb_typeof(after_state) = 'object');

CREATE UNIQUE INDEX IF NOT EXISTS site_revisions_client_idempotency_key
  ON public.site_revisions(client_id, idempotency_key);
CREATE INDEX IF NOT EXISTS idx_site_revisions_client_created
  ON public.site_revisions(client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_site_revisions_client_status
  ON public.site_revisions(client_id, status, version_after DESC);

ALTER TABLE public.site_revisions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.site_revisions FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE public.site_revisions TO service_role;

CREATE OR REPLACE FUNCTION public.editor_commit(
  p_client_id uuid,
  p_expected_version bigint,
  p_idempotency_key text,
  p_message text,
  p_operations jsonb,
  p_before_state jsonb,
  p_after_state jsonb
) RETURNS jsonb
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public
AS $$
DECLARE
  content_row public.site_content%ROWTYPE;
  existing_revision public.site_revisions%ROWTYPE;
  previous_id uuid;
  revision_id uuid;
BEGIN
  IF p_idempotency_key IS NULL
     OR length(p_idempotency_key) NOT BETWEEN 1 AND 200
     OR jsonb_typeof(p_operations) <> 'array'
     OR jsonb_typeof(p_before_state) <> 'object'
     OR jsonb_typeof(p_after_state) <> 'object' THEN
    RAISE EXCEPTION 'invalid_editor_payload' USING ERRCODE = '22023';
  END IF;

  SELECT * INTO existing_revision
  FROM public.site_revisions
  WHERE client_id = p_client_id AND idempotency_key = p_idempotency_key;
  IF FOUND THEN
    RETURN jsonb_build_object(
      'success', true, 'duplicate', true,
      'revision_id', existing_revision.id,
      'version', existing_revision.version_after,
      'content', existing_revision.after_state
    );
  END IF;

  INSERT INTO public.site_content(client_id, content, editor_version)
  VALUES (p_client_id, '{}'::jsonb, 0)
  ON CONFLICT (client_id) DO NOTHING;

  SELECT * INTO content_row
  FROM public.site_content
  WHERE client_id = p_client_id
  FOR UPDATE;

  SELECT * INTO existing_revision
  FROM public.site_revisions
  WHERE client_id = p_client_id AND idempotency_key = p_idempotency_key;
  IF FOUND THEN
    RETURN jsonb_build_object(
      'success', true, 'duplicate', true,
      'revision_id', existing_revision.id,
      'version', existing_revision.version_after,
      'content', existing_revision.after_state
    );
  END IF;

  IF content_row.editor_version <> p_expected_version THEN
    RAISE EXCEPTION 'stale_editor_version' USING ERRCODE = '40001';
  END IF;

  SELECT id INTO previous_id
  FROM public.site_revisions
  WHERE client_id = p_client_id
  ORDER BY version_after DESC
  LIMIT 1;

  INSERT INTO public.site_revisions(
    client_id, previous_revision_id, source, message, operations,
    before_state, after_state, version_before, version_after, idempotency_key
  ) VALUES (
    p_client_id, previous_id, 'chat', left(p_message, 4000), p_operations,
    p_before_state, p_after_state, content_row.editor_version,
    content_row.editor_version + 1, p_idempotency_key
  ) RETURNING id INTO revision_id;

  UPDATE public.site_content
  SET content = p_after_state,
      editor_version = editor_version + 1,
      updated_at = now()
  WHERE client_id = p_client_id;

  RETURN jsonb_build_object(
    'success', true, 'duplicate', false, 'revision_id', revision_id,
    'version', content_row.editor_version + 1, 'content', p_after_state
  );
END
$$;

CREATE OR REPLACE FUNCTION public.editor_undo(
  p_client_id uuid,
  p_expected_version bigint,
  p_idempotency_key text
) RETURNS jsonb
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public
AS $$
DECLARE
  content_row public.site_content%ROWTYPE;
  existing_revision public.site_revisions%ROWTYPE;
  target_revision public.site_revisions%ROWTYPE;
  revision_id uuid;
BEGIN
  IF p_idempotency_key IS NULL OR length(p_idempotency_key) NOT BETWEEN 1 AND 200 THEN
    RAISE EXCEPTION 'invalid_idempotency_key' USING ERRCODE = '22023';
  END IF;

  SELECT * INTO existing_revision
  FROM public.site_revisions
  WHERE client_id = p_client_id AND idempotency_key = p_idempotency_key;
  IF FOUND THEN
    RETURN jsonb_build_object(
      'success', true, 'duplicate', true,
      'revision_id', existing_revision.id,
      'version', existing_revision.version_after,
      'content', existing_revision.after_state
    );
  END IF;

  SELECT * INTO content_row
  FROM public.site_content
  WHERE client_id = p_client_id
  FOR UPDATE;
  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'no revision');
  END IF;

  IF content_row.editor_version <> p_expected_version THEN
    RAISE EXCEPTION 'stale_editor_version' USING ERRCODE = '40001';
  END IF;

  SELECT * INTO target_revision
  FROM public.site_revisions
  WHERE client_id = p_client_id AND source <> 'undo' AND status = 'applied'
  ORDER BY version_after DESC
  LIMIT 1
  FOR UPDATE;
  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'no revision');
  END IF;

  UPDATE public.site_revisions SET status = 'undone' WHERE id = target_revision.id;
  INSERT INTO public.site_revisions(
    client_id, previous_revision_id, source, message, operations,
    before_state, after_state, version_before, version_after,
    idempotency_key, undone_revision_id
  ) VALUES (
    p_client_id, target_revision.id, 'undo', 'deterministic undo', '[]'::jsonb,
    content_row.content, target_revision.before_state, content_row.editor_version,
    content_row.editor_version + 1, p_idempotency_key, target_revision.id
  ) RETURNING id INTO revision_id;

  UPDATE public.site_content
  SET content = target_revision.before_state,
      editor_version = editor_version + 1,
      updated_at = now()
  WHERE client_id = p_client_id;

  RETURN jsonb_build_object(
    'success', true, 'duplicate', false, 'revision_id', revision_id,
    'undone_revision_id', target_revision.id,
    'version', content_row.editor_version + 1,
    'content', target_revision.before_state
  );
END
$$;

REVOKE ALL ON FUNCTION public.editor_commit(uuid, bigint, text, text, jsonb, jsonb, jsonb)
  FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.editor_undo(uuid, bigint, text)
  FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.editor_commit(uuid, bigint, text, text, jsonb, jsonb, jsonb)
  TO service_role;
GRANT EXECUTE ON FUNCTION public.editor_undo(uuid, bigint, text)
  TO service_role;
