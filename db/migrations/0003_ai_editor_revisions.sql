-- 0003 - atomic draft editing. Published rows in public.sites are untouched.
ALTER TABLE public.site_content ADD COLUMN IF NOT EXISTS editor_version bigint NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS public.site_revisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  previous_revision_id uuid REFERENCES public.site_revisions(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  source text NOT NULL CHECK (source IN ('chat','manual','system','undo')),
  message text,
  operations jsonb NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(operations)='array'),
  before_state jsonb NOT NULL CHECK (jsonb_typeof(before_state)='object'),
  after_state jsonb NOT NULL CHECK (jsonb_typeof(after_state)='object'),
  status text NOT NULL DEFAULT 'applied' CHECK (status IN ('applied','undone')),
  version_before bigint NOT NULL,
  version_after bigint NOT NULL,
  idempotency_key text NOT NULL,
  undone_revision_id uuid REFERENCES public.site_revisions(id),
  UNIQUE(client_id,idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_site_revisions_client_created ON public.site_revisions(client_id,created_at DESC);
CREATE INDEX IF NOT EXISTS idx_site_revisions_client_status ON public.site_revisions(client_id,status,version_after DESC);
ALTER TABLE public.site_revisions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.site_revisions FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE public.site_revisions TO service_role;

CREATE OR REPLACE FUNCTION public.editor_commit(
 p_client_id uuid,p_expected_version bigint,p_idempotency_key text,p_message text,
 p_operations jsonb,p_before_state jsonb,p_after_state jsonb
) RETURNS jsonb LANGUAGE plpgsql SECURITY INVOKER SET search_path=public AS $$
DECLARE r public.site_content%ROWTYPE; old public.site_revisions%ROWTYPE; prev uuid; rid uuid;
BEGIN
 IF p_idempotency_key IS NULL OR length(p_idempotency_key) NOT BETWEEN 1 AND 200
    OR jsonb_typeof(p_operations)<>'array' OR jsonb_typeof(p_before_state)<>'object'
    OR jsonb_typeof(p_after_state)<>'object' THEN
   RAISE EXCEPTION 'invalid_editor_payload' USING ERRCODE='22023';
 END IF;
 SELECT * INTO old FROM public.site_revisions WHERE client_id=p_client_id AND idempotency_key=p_idempotency_key;
 IF FOUND THEN RETURN jsonb_build_object('success',true,'duplicate',true,'revision_id',old.id,'version',old.version_after,'content',old.after_state); END IF;
 INSERT INTO public.site_content(client_id,content,editor_version) VALUES(p_client_id,'{}',0) ON CONFLICT(client_id) DO NOTHING;
 SELECT * INTO r FROM public.site_content WHERE client_id=p_client_id FOR UPDATE;
 SELECT * INTO old FROM public.site_revisions WHERE client_id=p_client_id AND idempotency_key=p_idempotency_key;
 IF FOUND THEN RETURN jsonb_build_object('success',true,'duplicate',true,'revision_id',old.id,'version',old.version_after,'content',old.after_state); END IF;
 IF r.editor_version<>p_expected_version THEN RAISE EXCEPTION 'stale_editor_version' USING ERRCODE='40001'; END IF;
 SELECT id INTO prev FROM public.site_revisions WHERE client_id=p_client_id ORDER BY version_after DESC LIMIT 1;
 INSERT INTO public.site_revisions(client_id,previous_revision_id,source,message,operations,before_state,after_state,version_before,version_after,idempotency_key)
 VALUES(p_client_id,prev,'chat',left(p_message,4000),p_operations,p_before_state,p_after_state,r.editor_version,r.editor_version+1,p_idempotency_key)
 RETURNING id INTO rid;
 UPDATE public.site_content SET content=p_after_state,editor_version=editor_version+1,updated_at=now() WHERE client_id=p_client_id;
 RETURN jsonb_build_object('success',true,'duplicate',false,'revision_id',rid,'version',r.editor_version+1,'content',p_after_state);
END $$;

CREATE OR REPLACE FUNCTION public.editor_undo(p_client_id uuid,p_expected_version bigint,p_idempotency_key text)
RETURNS jsonb LANGUAGE plpgsql SECURITY INVOKER SET search_path=public AS $$
DECLARE r public.site_content%ROWTYPE; old public.site_revisions%ROWTYPE; target public.site_revisions%ROWTYPE; rid uuid;
BEGIN
 IF p_idempotency_key IS NULL OR length(p_idempotency_key) NOT BETWEEN 1 AND 200 THEN RAISE EXCEPTION 'invalid_idempotency_key' USING ERRCODE='22023'; END IF;
 SELECT * INTO old FROM public.site_revisions WHERE client_id=p_client_id AND idempotency_key=p_idempotency_key;
 IF FOUND THEN RETURN jsonb_build_object('success',true,'duplicate',true,'revision_id',old.id,'version',old.version_after,'content',old.after_state); END IF;
 SELECT * INTO r FROM public.site_content WHERE client_id=p_client_id FOR UPDATE;
 IF NOT FOUND THEN RETURN jsonb_build_object('success',false,'message','no revision'); END IF;
 SELECT * INTO old FROM public.site_revisions WHERE client_id=p_client_id AND idempotency_key=p_idempotency_key;
 IF FOUND THEN RETURN jsonb_build_object('success',true,'duplicate',true,'revision_id',old.id,'version',old.version_after,'content',old.after_state); END IF;
 IF r.editor_version<>p_expected_version THEN RAISE EXCEPTION 'stale_editor_version' USING ERRCODE='40001'; END IF;
 SELECT * INTO target FROM public.site_revisions WHERE client_id=p_client_id AND source<>'undo' AND status='applied' ORDER BY version_after DESC LIMIT 1 FOR UPDATE;
 IF NOT FOUND THEN RETURN jsonb_build_object('success',false,'message','no revision'); END IF;
 UPDATE public.site_revisions SET status='undone' WHERE id=target.id;
 INSERT INTO public.site_revisions(client_id,previous_revision_id,source,message,operations,before_state,after_state,version_before,version_after,idempotency_key,undone_revision_id)
 VALUES(p_client_id,target.id,'undo','deterministic undo','[]',r.content,target.before_state,r.editor_version,r.editor_version+1,p_idempotency_key,target.id)
 RETURNING id INTO rid;
 UPDATE public.site_content SET content=target.before_state,editor_version=editor_version+1,updated_at=now() WHERE client_id=p_client_id;
 RETURN jsonb_build_object('success',true,'duplicate',false,'revision_id',rid,'undone_revision_id',target.id,'version',r.editor_version+1,'content',target.before_state);
END $$;

REVOKE ALL ON FUNCTION public.editor_commit(uuid,bigint,text,text,jsonb,jsonb,jsonb) FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION public.editor_undo(uuid,bigint,text) FROM PUBLIC,anon,authenticated;
GRANT EXECUTE ON FUNCTION public.editor_commit(uuid,bigint,text,text,jsonb,jsonb,jsonb) TO service_role;
GRANT EXECUTE ON FUNCTION public.editor_undo(uuid,bigint,text) TO service_role;
