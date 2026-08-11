-- ENV: staging-only
--
-- ΔΕΝ εφαρμόζεται στην παραγωγή. Ο Agency Kernel (Phase 4A) δεν έχει
-- ολοκληρωθεί και δεν τον χρησιμοποιεί κανένα production specialist/action.
-- Ο runner το παραλείπει όταν VITRINA_ENV=production, μέχρι ρητή έγκριση.
--
-- Για προώθηση στην παραγωγή: αφαίρεσε αυτή τη γραμμή ΕΝV και τρέξε
--   VITRINA_ENV=production python scripts/migrate.py --apply --confirm-production
--
-- Stage 4A: Agency Kernel (deterministic, provider-agnostic, no active agents).
-- `clients.id` is the workspace id for this stage; no parallel tenancy model.

CREATE TABLE IF NOT EXISTS capability_definitions (
  capability_key text NOT NULL,
  version text NOT NULL,
  description text NOT NULL,
  risk text NOT NULL DEFAULT 'low' CHECK (risk IN ('low', 'medium', 'high')),
  permissions jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (capability_key, version)
);

CREATE TABLE IF NOT EXISTS agent_registry (
  agent_key text NOT NULL,
  version text NOT NULL,
  name text NOT NULL,
  purpose text NOT NULL,
  lifecycle text NOT NULL DEFAULT 'draft'
    CHECK (lifecycle IN ('draft', 'available', 'deprecated', 'revoked')),
  manifest jsonb NOT NULL,
  manifest_checksum text NOT NULL,
  registered_by text NOT NULL,
  registered_at timestamptz NOT NULL DEFAULT now(),
  revoked_at timestamptz,
  revocation_reason text,
  PRIMARY KEY (agent_key, version)
);

CREATE TABLE IF NOT EXISTS agent_capabilities (
  agent_key text NOT NULL,
  agent_version text NOT NULL,
  capability_key text NOT NULL,
  capability_version text NOT NULL,
  PRIMARY KEY (agent_key, agent_version, capability_key, capability_version),
  FOREIGN KEY (agent_key, agent_version)
    REFERENCES agent_registry(agent_key, version) ON DELETE CASCADE,
  FOREIGN KEY (capability_key, capability_version)
    REFERENCES capability_definitions(capability_key, version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS plan_capabilities (
  plan_key text NOT NULL CHECK (plan_key IN
    ('presence', 'growth', 'revenue', 'agency', 'multi_location')),
  capability_key text NOT NULL,
  capability_version text NOT NULL,
  limits jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (plan_key, capability_key, capability_version),
  FOREIGN KEY (capability_key, capability_version)
    REFERENCES capability_definitions(capability_key, version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS agent_installations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  agent_key text NOT NULL,
  agent_version text NOT NULL,
  status text NOT NULL DEFAULT 'installed'
    CHECK (status IN ('installed', 'enabled', 'disabled', 'revoked')),
  verticals jsonb NOT NULL DEFAULT '["*"]'::jsonb,
  config jsonb NOT NULL DEFAULT '{}'::jsonb,
  granted_permissions jsonb NOT NULL DEFAULT '[]'::jsonb,
  budget_limits jsonb NOT NULL DEFAULT
    '{"max_money_eur":"0","max_tokens":0,"max_runtime_seconds":300}'::jsonb,
  installed_by text NOT NULL,
  installed_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  revoked_at timestamptz,
  revocation_reason text,
  UNIQUE (workspace_id, agent_key, agent_version),
  FOREIGN KEY (agent_key, agent_version)
    REFERENCES agent_registry(agent_key, version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS workspace_entitlements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  capability_key text NOT NULL,
  capability_version text NOT NULL,
  status text NOT NULL DEFAULT 'granted' CHECK (status IN ('granted', 'denied')),
  source text NOT NULL CHECK (source IN ('plan', 'trial', 'manual', 'promotion', 'partner')),
  source_ref text,
  limits jsonb NOT NULL DEFAULT '{}'::jsonb,
  starts_at timestamptz NOT NULL DEFAULT now(),
  ends_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (workspace_id, capability_key, capability_version, source, source_ref),
  FOREIGN KEY (capability_key, capability_version)
    REFERENCES capability_definitions(capability_key, version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS agent_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  agent_key text NOT NULL,
  agent_version text NOT NULL,
  capability_key text NOT NULL,
  capability_version text NOT NULL,
  goal text NOT NULL,
  trigger_type text NOT NULL,
  status text NOT NULL DEFAULT 'queued' CHECK (status IN
    ('queued', 'blocked', 'pending_approval', 'ready', 'running', 'succeeded',
     'failed', 'cancelled')),
  mode text NOT NULL DEFAULT 'propose' CHECK (mode IN ('propose', 'execute')),
  risk text NOT NULL DEFAULT 'low' CHECK (risk IN ('low', 'medium', 'high')),
  approval_policy text NOT NULL DEFAULT 'none'
    CHECK (approval_policy IN ('none', 'client', 'operator', 'dual')),
  input_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  expected_outputs jsonb NOT NULL DEFAULT '[]'::jsonb,
  requested_permissions jsonb NOT NULL DEFAULT '[]'::jsonb,
  data_classes jsonb NOT NULL DEFAULT '["public"]'::jsonb,
  budget jsonb NOT NULL DEFAULT
    '{"max_money_eur":"0","max_tokens":0,"max_runtime_seconds":300}'::jsonb,
  policy_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,
  idempotency_key text NOT NULL,
  parent_task_id uuid REFERENCES agent_tasks(id) ON DELETE SET NULL,
  created_by text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  UNIQUE (workspace_id, idempotency_key),
  FOREIGN KEY (agent_key, agent_version)
    REFERENCES agent_registry(agent_key, version) ON DELETE RESTRICT,
  FOREIGN KEY (capability_key, capability_version)
    REFERENCES capability_definitions(capability_key, version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id uuid NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  attempt int NOT NULL DEFAULT 1 CHECK (attempt > 0),
  status text NOT NULL DEFAULT 'created' CHECK (status IN
    ('created', 'running', 'waiting_approval', 'succeeded', 'failed', 'cancelled')),
  provider text NOT NULL DEFAULT 'deterministic',
  model text,
  session_ref text,
  input_digest text NOT NULL,
  output_summary jsonb NOT NULL DEFAULT '{}'::jsonb,
  evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
  actions_taken jsonb NOT NULL DEFAULT '[]'::jsonb,
  confidence numeric(5,4),
  cost jsonb NOT NULL DEFAULT '{}'::jsonb,
  error_code text,
  error_detail text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (task_id, attempt)
);

CREATE TABLE IF NOT EXISTS agent_approvals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  task_id uuid NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
  run_id uuid REFERENCES agent_runs(id) ON DELETE SET NULL,
  policy text NOT NULL CHECK (policy IN ('client', 'operator', 'dual')),
  action_type text NOT NULL,
  action_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  payload_hash text NOT NULL,
  status text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'revoked')),
  requested_by text NOT NULL,
  requested_at timestamptz NOT NULL DEFAULT now(),
  decided_by text,
  decided_at timestamptz,
  decision_reason text,
  expires_at timestamptz,
  UNIQUE (task_id, action_type, payload_hash)
);

CREATE TABLE IF NOT EXISTS agent_artifacts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  task_id uuid NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
  run_id uuid REFERENCES agent_runs(id) ON DELETE SET NULL,
  artifact_type text NOT NULL,
  uri text NOT NULL,
  media_type text,
  checksum text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agency_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES clients(id) ON DELETE CASCADE,
  task_id uuid REFERENCES agent_tasks(id) ON DELETE CASCADE,
  run_id uuid REFERENCES agent_runs(id) ON DELETE SET NULL,
  event_type text NOT NULL,
  actor_type text NOT NULL CHECK (actor_type IN ('user', 'operator', 'system', 'agent')),
  actor_id text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  trace_id text NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS kpi_snapshots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  task_id uuid REFERENCES agent_tasks(id) ON DELETE SET NULL,
  metric_key text NOT NULL,
  value numeric NOT NULL,
  unit text NOT NULL,
  dimensions jsonb NOT NULL DEFAULT '{}'::jsonb,
  source text NOT NULL,
  measured_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agency_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES clients(id) ON DELETE CASCADE,
  task_id uuid REFERENCES agent_tasks(id) ON DELETE SET NULL,
  actor_type text NOT NULL CHECK (actor_type IN ('user', 'operator', 'system', 'agent')),
  actor_id text NOT NULL,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text NOT NULL,
  before_state jsonb,
  after_state jsonb,
  reason text,
  trace_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_installations_workspace
  ON agent_installations(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_workspace_entitlements_active
  ON workspace_entitlements(workspace_id, capability_key, capability_version)
  WHERE status = 'granted';
CREATE INDEX IF NOT EXISTS idx_agent_tasks_queue
  ON agent_tasks(workspace_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_runs_task ON agent_runs(task_id, attempt DESC);
CREATE INDEX IF NOT EXISTS idx_agent_approvals_pending
  ON agent_approvals(workspace_id, requested_at DESC) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_agent_artifacts_task ON agent_artifacts(task_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agency_events_trace ON agency_events(trace_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_kpi_workspace_metric
  ON kpi_snapshots(workspace_id, metric_key, measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_agency_audit_trace ON agency_audit_log(trace_id, created_at);

-- Evidence is append-only. Corrections are represented by a new compensating
-- event/audit row, never by rewriting history.
CREATE OR REPLACE FUNCTION prevent_agency_evidence_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION '% is append-only; append a compensating record instead', TG_TABLE_NAME;
END;
$$;

DROP TRIGGER IF EXISTS agency_events_append_only ON agency_events;
CREATE TRIGGER agency_events_append_only
  BEFORE UPDATE OR DELETE ON agency_events
  FOR EACH ROW EXECUTE FUNCTION prevent_agency_evidence_mutation();

DROP TRIGGER IF EXISTS agency_audit_log_append_only ON agency_audit_log;
CREATE TRIGGER agency_audit_log_append_only
  BEFORE UPDATE OR DELETE ON agency_audit_log
  FOR EACH ROW EXECUTE FUNCTION prevent_agency_evidence_mutation();

-- Stable read contract for the future dashboard action queue.
CREATE OR REPLACE VIEW agency_action_queue WITH (security_invoker = true) AS
SELECT
  t.id AS task_id,
  t.workspace_id,
  t.agent_key,
  t.agent_version,
  r.name AS agent_name,
  t.capability_key,
  t.capability_version,
  t.goal,
  t.status,
  t.risk,
  t.approval_policy,
  (a.id IS NOT NULL AND a.status = 'pending') AS needs_approval,
  a.id AS approval_id,
  a.status AS approval_status,
  NULL::text AS value_metric,
  NULL::numeric AS kpi_before,
  NULL::numeric AS kpi_after,
  NULL::text AS value_unit,
  t.created_at,
  t.updated_at
FROM agent_tasks t
JOIN agent_registry r ON r.agent_key = t.agent_key AND r.version = t.agent_version
LEFT JOIN LATERAL (
  SELECT id, status FROM agent_approvals
  WHERE task_id = t.id
  ORDER BY requested_at DESC LIMIT 1
) a ON true
WHERE t.status IN ('queued', 'blocked', 'pending_approval', 'ready', 'running', 'failed');

-- Seed only capabilities and plan mappings. No agent is registered/installed/enabled here.
INSERT INTO capability_definitions (capability_key, version, description, risk) VALUES
  ('website.manage','1','Generate and maintain website content','medium'),
  ('website.qa','1','Run deterministic website quality checks','low'),
  ('seo.audit','1','Audit technical and on-page SEO','low'),
  ('accessibility.audit','1','Audit WCAG and accessibility regressions','low'),
  ('performance.audit','1','Audit performance and Core Web Vitals','low'),
  ('security.audit','1','Audit headers, dependencies and configuration','medium'),
  ('maintenance.monitor','1','Monitor uptime, SSL, DNS, links and forms','low'),
  ('content.manage','1','Draft website and campaign content','medium'),
  ('social.draft','1','Create approval-first social drafts','medium'),
  ('reviews.intelligence','1','Analyze review themes and opportunities','low'),
  ('listings.audit','1','Audit local listings consistency','low'),
  ('demand.observe','1','Detect local and seasonal demand signals','low'),
  ('reporting.value','1','Produce evidence-based client value reports','low'),
  ('lead.capture','1','Capture and qualify inbound leads','medium'),
  ('lead.followup','1','Draft and schedule lead follow-up','high'),
  ('booking.test','1','Run synthetic booking journey checks','low'),
  ('noshow.prevent','1','Prepare appointment confirmation workflows','medium'),
  ('reactivation.plan','1','Prepare customer reactivation campaigns','high'),
  ('attribution.read','1','Connect first-party activity to outcomes','medium'),
  ('ads.draft','1','Draft paid campaign proposals without spend','high'),
  ('experiment.propose','1','Propose measurable conversion experiments','medium'),
  ('offer.propose','1','Propose margin-aware offers','high'),
  ('competitor.audit','1','Audit competitor positioning and gaps','low'),
  ('customer_voice.analyze','1','Analyze consented customer-language evidence','medium'),
  ('locations.manage','1','Coordinate multi-location business data','high'),
  ('governance.manage','1','Apply organization-level policies and approvals','high'),
  ('integrations.enterprise','1','Use governed enterprise connectors','high')
ON CONFLICT DO NOTHING;

-- Capability inheritance is materialized explicitly. Marketing names can change
-- without changing the capability keys consumed by policy code.
INSERT INTO plan_capabilities (plan_key, capability_key, capability_version)
SELECT plan_key, capability_key, '1' FROM (VALUES
  ('presence','website.manage'),('presence','website.qa'),('presence','seo.audit'),
  ('presence','accessibility.audit'),('presence','performance.audit'),
  ('presence','security.audit'),('presence','maintenance.monitor'),
  ('growth','website.manage'),('growth','website.qa'),('growth','seo.audit'),
  ('growth','accessibility.audit'),('growth','performance.audit'),('growth','security.audit'),
  ('growth','maintenance.monitor'),('growth','content.manage'),('growth','social.draft'),
  ('growth','reviews.intelligence'),('growth','listings.audit'),('growth','demand.observe'),
  ('growth','reporting.value'),
  ('revenue','website.manage'),('revenue','website.qa'),('revenue','seo.audit'),
  ('revenue','accessibility.audit'),('revenue','performance.audit'),('revenue','security.audit'),
  ('revenue','maintenance.monitor'),('revenue','content.manage'),('revenue','social.draft'),
  ('revenue','reviews.intelligence'),('revenue','listings.audit'),('revenue','demand.observe'),
  ('revenue','reporting.value'),('revenue','lead.capture'),('revenue','lead.followup'),
  ('revenue','booking.test'),('revenue','noshow.prevent'),('revenue','reactivation.plan'),
  ('revenue','attribution.read'),
  ('agency','website.manage'),('agency','website.qa'),('agency','seo.audit'),
  ('agency','accessibility.audit'),('agency','performance.audit'),('agency','security.audit'),
  ('agency','maintenance.monitor'),('agency','content.manage'),('agency','social.draft'),
  ('agency','reviews.intelligence'),('agency','listings.audit'),('agency','demand.observe'),
  ('agency','reporting.value'),('agency','lead.capture'),('agency','lead.followup'),
  ('agency','booking.test'),('agency','noshow.prevent'),('agency','reactivation.plan'),
  ('agency','attribution.read'),('agency','ads.draft'),('agency','experiment.propose'),
  ('agency','offer.propose'),('agency','competitor.audit'),('agency','customer_voice.analyze'),
  ('multi_location','website.manage'),('multi_location','website.qa'),('multi_location','seo.audit'),
  ('multi_location','accessibility.audit'),('multi_location','performance.audit'),
  ('multi_location','security.audit'),('multi_location','maintenance.monitor'),
  ('multi_location','content.manage'),('multi_location','social.draft'),
  ('multi_location','reviews.intelligence'),('multi_location','listings.audit'),
  ('multi_location','demand.observe'),('multi_location','reporting.value'),
  ('multi_location','lead.capture'),('multi_location','lead.followup'),
  ('multi_location','booking.test'),('multi_location','noshow.prevent'),
  ('multi_location','reactivation.plan'),('multi_location','attribution.read'),
  ('multi_location','ads.draft'),('multi_location','experiment.propose'),
  ('multi_location','offer.propose'),('multi_location','competitor.audit'),
  ('multi_location','customer_voice.analyze'),('multi_location','locations.manage'),
  ('multi_location','governance.manage'),('multi_location','integrations.enterprise')
) AS grants(plan_key, capability_key)
ON CONFLICT DO NOTHING;

-- These tables were created after 0006; fail closed for public/anon access.
ALTER TABLE capability_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_installations ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_entitlements ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_audit_log ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON agency_action_queue FROM anon, authenticated;

COMMENT ON TABLE agent_registry IS 'Immutable versioned marketplace manifests; registration is not activation.';
COMMENT ON TABLE agent_installations IS 'Per-workspace install/enable/disable/revoke state.';
COMMENT ON TABLE plan_capabilities IS 'Versioned capability matrix independent of marketing plan labels.';
COMMENT ON TABLE agent_tasks IS 'Policy-gated work requests; specialist execution is not enabled by this migration.';
COMMENT ON TABLE agency_audit_log IS 'Append-oriented audit evidence for every kernel state transition.';
