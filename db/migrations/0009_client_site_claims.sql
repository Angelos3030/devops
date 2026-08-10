-- Secure hand-off from anonymous site generation to an authenticated owner.
-- Raw claim tokens never reach the database; only SHA-256 hashes are stored.

CREATE TABLE IF NOT EXISTS client_site_claims (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
  token_hash text NOT NULL UNIQUE,
  expires_at timestamptz NOT NULL,
  claimed_at timestamptz,
  claimed_by text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_client_site_claims_active
  ON client_site_claims (token_hash, expires_at)
  WHERE claimed_at IS NULL;

ALTER TABLE client_site_claims ENABLE ROW LEVEL SECURITY;

-- One transaction owns the site and consumes the token. The authenticated email
-- is supplied by the backend only after validating the Supabase access token.
CREATE OR REPLACE FUNCTION claim_client_site(
  p_client_id uuid,
  p_token_hash text,
  p_email text
) RETURNS boolean
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public
AS $$
DECLARE
  claim_row client_site_claims%ROWTYPE;
  current_owner text;
BEGIN
  SELECT * INTO claim_row
    FROM client_site_claims
   WHERE client_id = p_client_id AND token_hash = p_token_hash
   FOR UPDATE;

  IF NOT FOUND OR claim_row.expires_at <= now() THEN
    RETURN false;
  END IF;

  SELECT lower(coalesce(email, '')) INTO current_owner
    FROM clients WHERE id = p_client_id FOR UPDATE;

  IF claim_row.claimed_at IS NOT NULL THEN
    RETURN current_owner = lower(p_email)
       AND lower(coalesce(claim_row.claimed_by, '')) = lower(p_email);
  END IF;

  IF current_owner <> '' AND current_owner <> lower(p_email) THEN
    RETURN false;
  END IF;

  UPDATE clients SET email = lower(p_email) WHERE id = p_client_id;
  UPDATE client_site_claims
     SET claimed_at = now(), claimed_by = lower(p_email)
   WHERE id = claim_row.id;
  RETURN true;
END;
$$;

REVOKE ALL ON TABLE client_site_claims FROM anon, authenticated;
REVOKE ALL ON FUNCTION claim_client_site(uuid, text, text) FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE client_site_claims TO service_role;
GRANT EXECUTE ON FUNCTION claim_client_site(uuid, text, text) TO service_role;
