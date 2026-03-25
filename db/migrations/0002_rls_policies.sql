-- Tenant-safe Row Level Security baseline policies.
-- NOTE: application should set these per request/session:
--   SET app.current_org_id = '<org-uuid>';
--   SET app.current_client_id = '<client-uuid>';
--   SET app.is_internal = 'false'|'true';

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE facilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE appliances ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE retraining_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY p_clients_tenant_select ON clients
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR organization_id::text = current_setting('app.current_org_id', true)
);

CREATE POLICY p_facilities_tenant_select ON facilities
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR client_id::text = current_setting('app.current_client_id', true)
);

CREATE POLICY p_connectors_tenant_select ON connectors
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR facility_id IN (
    SELECT id FROM facilities WHERE client_id::text = current_setting('app.current_client_id', true)
  )
);

CREATE POLICY p_appliances_tenant_select ON appliances
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR facility_id IN (
    SELECT id FROM facilities WHERE client_id::text = current_setting('app.current_client_id', true)
  )
);

CREATE POLICY p_recommendations_tenant_select ON recommendations
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR facility_id IN (
    SELECT id FROM facilities WHERE client_id::text = current_setting('app.current_client_id', true)
  )
);

CREATE POLICY p_alerts_tenant_select ON alerts
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR client_id::text = current_setting('app.current_client_id', true)
);

CREATE POLICY p_model_runs_tenant_select ON model_runs
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR facility_id IN (
    SELECT id FROM facilities WHERE client_id::text = current_setting('app.current_client_id', true)
  )
);

CREATE POLICY p_retraining_jobs_tenant_select ON retraining_jobs
FOR SELECT
USING (
  current_setting('app.is_internal', true) = 'true'
  OR facility_id IN (
    SELECT id FROM facilities WHERE client_id::text = current_setting('app.current_client_id', true)
  )
);
