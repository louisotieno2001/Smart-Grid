CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  legal_name TEXT,
  industry TEXT,
  timezone TEXT NOT NULL DEFAULT 'UTC',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  external_key TEXT,
  name TEXT NOT NULL,
  billing_plan TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'EUR',
  timezone TEXT NOT NULL DEFAULT 'UTC',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, name),
  UNIQUE (external_key)
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  full_name TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  facility_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_user_memberships_unique 
ON user_memberships(user_id, organization_id, role, COALESCE(client_id, '00000000-0000-0000-0000-000000000000'::uuid), COALESCE(facility_id, '00000000-0000-0000-0000-000000000000'::uuid));

CREATE TABLE facilities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  country TEXT,
  site_type TEXT,
  timezone TEXT NOT NULL,
  production_profile TEXT,
  tariff_schedule_id UUID,
  status TEXT NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (client_id, name)
);

ALTER TABLE user_memberships
  ADD CONSTRAINT fk_user_membership_facility
  FOREIGN KEY (facility_id) REFERENCES facilities(id) ON DELETE CASCADE;

CREATE TABLE connectors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  connector_type TEXT NOT NULL,
  vendor TEXT,
  source_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'healthy',
  endpoint_fingerprint TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_sync_at TIMESTAMPTZ,
  UNIQUE (facility_id, source_name),
  UNIQUE (facility_id, endpoint_fingerprint)
);

CREATE TABLE appliances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  subtype TEXT,
  rated_power_kw NUMERIC(12,3),
  control_mode TEXT,
  zone TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (facility_id, name)
);

CREATE TABLE channel_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appliance_id UUID NOT NULL REFERENCES appliances(id) ON DELETE CASCADE,
  connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
  channel_id TEXT NOT NULL,
  role TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (appliance_id, channel_id, role)
);

CREATE TABLE ingestion_import_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  idempotency_key TEXT NOT NULL,
  import_type TEXT NOT NULL,
  file_id TEXT NOT NULL,
  status TEXT NOT NULL,
  progress_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
  estimated_rows BIGINT,
  rows_processed BIGINT,
  rows_rejected BIGINT,
  failure_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  UNIQUE (facility_id, idempotency_key)
);

CREATE TABLE feature_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  idempotency_key TEXT NOT NULL,
  window_start TIMESTAMPTZ NOT NULL,
  window_end TIMESTAMPTZ NOT NULL,
  granularity TEXT NOT NULL,
  feature_version TEXT NOT NULL,
  output_path TEXT,
  row_count BIGINT,
  status TEXT NOT NULL,
  failure_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  UNIQUE (facility_id, idempotency_key)
);

CREATE TABLE model_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  idempotency_key TEXT NOT NULL,
  feature_job_id UUID REFERENCES feature_jobs(id) ON DELETE SET NULL,
  model_family TEXT NOT NULL,
  model_version TEXT,
  status TEXT NOT NULL,
  train_window_start TIMESTAMPTZ,
  train_window_end TIMESTAMPTZ,
  validation_json JSONB,
  hyperparameters_json JSONB,
  holdout_mape NUMERIC(8,6),
  retraining_triggered BOOLEAN NOT NULL DEFAULT FALSE,
  retraining_job_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  UNIQUE (facility_id, idempotency_key)
);

CREATE TABLE model_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_run_id UUID NOT NULL REFERENCES model_runs(id) ON DELETE CASCADE,
  artifact_type TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  checksum TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  model_run_id UUID REFERENCES model_runs(id) ON DELETE SET NULL,
  appliance_id UUID REFERENCES appliances(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  projected_annual_savings_eur NUMERIC(14,2) NOT NULL,
  confidence NUMERIC(5,4) NOT NULL,
  effort TEXT,
  payback_months NUMERIC(8,2),
  implementation_readiness NUMERIC(5,4),
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recommendation_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
  decision TEXT NOT NULL,
  owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  target_implementation_date DATE,
  notes TEXT,
  decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE savings_realization (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  appliance_id UUID REFERENCES appliances(id) ON DELETE SET NULL,
  recommendation_id UUID REFERENCES recommendations(id) ON DELETE SET NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  projected_eur NUMERIC(14,2) NOT NULL,
  realized_eur NUMERIC(14,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE drift_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  model_run_id UUID REFERENCES model_runs(id) ON DELETE SET NULL,
  feature_group TEXT NOT NULL,
  monitored_segment TEXT,
  threshold NUMERIC(8,4) NOT NULL,
  observed_value NUMERIC(10,6),
  severity TEXT NOT NULL,
  retraining_action TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  source_type TEXT NOT NULL,
  source_id TEXT,
  severity TEXT NOT NULL,
  state TEXT NOT NULL,
  owner_role TEXT,
  routing_policy TEXT,
  sla_minutes INT,
  dedupe_key TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (facility_id, dedupe_key, state)
);

CREATE TABLE retraining_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
  model_run_id UUID REFERENCES model_runs(id) ON DELETE SET NULL,
  status TEXT NOT NULL,
  reason TEXT,
  threshold NUMERIC(8,6),
  observed_holdout_mape NUMERIC(8,6),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

CREATE TABLE demo_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company TEXT NOT NULL,
  contact_name TEXT NOT NULL,
  email TEXT NOT NULL,
  facilities_count INT,
  annual_energy_spend_eur NUMERIC(14,2),
  message TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pricing_inquiries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company TEXT NOT NULL,
  contact_name TEXT NOT NULL,
  email TEXT NOT NULL,
  deployment_size TEXT,
  requested_plan TEXT,
  message TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id TEXT,
  actor_roles TEXT,
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_facilities_client ON facilities(client_id);
CREATE INDEX idx_connectors_facility_status ON connectors(facility_id, status);
CREATE INDEX idx_import_jobs_facility_time ON ingestion_import_jobs(facility_id, created_at DESC);
CREATE INDEX idx_feature_jobs_facility_status ON feature_jobs(facility_id, status);
CREATE INDEX idx_model_runs_facility_time ON model_runs(facility_id, created_at DESC);
CREATE INDEX idx_model_artifacts_run ON model_artifacts(model_run_id);
CREATE INDEX idx_recommendations_facility_status ON recommendations(facility_id, status);
CREATE INDEX idx_recommendations_active_partial ON recommendations(facility_id, projected_annual_savings_eur DESC) WHERE status = 'active';
CREATE INDEX idx_alerts_facility_state ON alerts(facility_id, state, severity);
CREATE INDEX idx_alerts_open_partial ON alerts(facility_id, severity, created_at DESC) WHERE state = 'open';
CREATE INDEX idx_drift_events_facility_time ON drift_events(facility_id, created_at DESC);
CREATE INDEX idx_retraining_jobs_facility_status ON retraining_jobs(facility_id, status, created_at DESC);
CREATE INDEX idx_savings_facility_period ON savings_realization(facility_id, period_start, period_end);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id, created_at DESC);
