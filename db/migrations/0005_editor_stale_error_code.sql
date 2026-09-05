-- A stale browser tab is an application conflict, not a PostgreSQL
-- serialization failure. SQLSTATE 40001 is retryable and caused PostgREST to
-- hold the request until timeout instead of returning the conflict promptly.
DO $$
DECLARE
  ddl text;
BEGIN
  SELECT pg_get_functiondef(
    'public.editor_commit(uuid,bigint,text,text,jsonb,jsonb,jsonb)'::regprocedure
  ) INTO ddl;
  EXECUTE replace(ddl, 'ERRCODE = ''40001''', 'ERRCODE = ''P0001''');

  SELECT pg_get_functiondef(
    'public.editor_undo(uuid,bigint,text)'::regprocedure
  ) INTO ddl;
  EXECUTE replace(ddl, 'ERRCODE = ''40001''', 'ERRCODE = ''P0001''');
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
