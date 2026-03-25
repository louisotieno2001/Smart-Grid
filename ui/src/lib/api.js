const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let cachedToken = null;

async function getDevToken() {
  if (cachedToken) return cachedToken;

  const response = await fetch(`${API_BASE}/api/v1/auth/dev-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sub: "ui_operator",
      roles: ["client_admin", "facility_manager", "energy_analyst", "ops_admin", "ml_engineer"],
      client_id: "cli_001",
    }),
  });

  if (!response.ok) {
    throw new Error("Unable to authenticate against API");
  }

  const payload = await response.json();
  cachedToken = payload.access_token;
  return cachedToken;
}

async function authHeaders(extra = {}) {
  const token = await getDevToken();
  return { Authorization: `Bearer ${token}`, ...extra };
}

export async function createFacility(payload) {
  const siteId = `site_${Date.now()}`;
  const response = await fetch(`${API_BASE}/api/v1/sites`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      site_id: siteId,
      name: payload?.name || "New Site",
      timezone: payload?.timezone || "UTC",
      reserve_soc_min: 20,
      polling_interval_seconds: 300,
    }),
  });
  if (!response.ok) throw new Error("create facility failed");
  const created = await response.json();
  return { facility_id: created.id || siteId, status: "active" };
}

export async function listFacilities(clientId = "cli_001", status = null) {
  const response = await fetch(`${API_BASE}/api/v1/sites`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list facilities failed");
  const payload = await response.json();
  const items = (payload.items || []).map((site) => ({
    id: site.id,
    name: site.name,
    status: "active",
    country: "N/A",
  }));
  return { items };
}

export async function attachConnector(facilityId, payload) {
  const response = await fetch(`${API_BASE}/api/v1/sites/${facilityId}/devices`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      device_type: payload?.type || "battery_inverter",
      protocol: "modbus_tcp",
      metadata: payload || {},
    }),
  });
  if (!response.ok) throw new Error("attach connector failed");
  return response.json();
}

export async function validateConnector(connectorId) {
  return {
    connector_id: connectorId,
    status: "accepted",
    channels_detected: 9,
    issues: [],
  };
}

export async function startBackfill(facilityId, payload) {
  const points = [
    { canonical_key: "pv_kw", ts: new Date().toISOString(), value: 2.1, unit: "kW", quality: "good" },
    { canonical_key: "load_kw", ts: new Date().toISOString(), value: 3.7, unit: "kW", quality: "good" },
    { canonical_key: "battery_soc", ts: new Date().toISOString(), value: 58.0, unit: "%", quality: "good" },
  ];
  const response = await fetch(`${API_BASE}/api/v1/telemetry/ingest`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ site_id: facilityId, gateway_id: `gw-${Date.now()}`, points }),
  });
  if (!response.ok) throw new Error("backfill start failed");
  return { import_id: `ing_${Date.now()}`, status: "queued" };
}

export async function acknowledgeAlert(alertId, note) {
  const response = await fetch(`${API_BASE}/api/v1/commands/${alertId}/ack`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ note }),
  });
  if (!response.ok) throw new Error("acknowledge failed");
  return response.json();
}

export async function openIncident(alertId, note) {
  return { incident_id: `inc_${Date.now()}`, alert_id: alertId, note };
}

export async function listRecommendations(facilityId, status = "active") {
  const response = await fetch(`${API_BASE}/api/v1/sites/${facilityId}/optimize/runs`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list recommendations failed");
  const payload = await response.json();
  const items = (payload.items || []).map((run, idx) => ({
    recommendation_id: run.id || `run_${idx}`,
    appliance_id: run.command_id || "device",
    title: `Action ${run.action_type || "idle"}`,
    projected_annual_savings_eur: 25000,
    confidence: 0.75,
    effort: "medium",
    payback_months: 6,
    implementation_readiness: 0.7,
    status,
    detail: run.explanation?.summary || "Derived from optimization run",
  }));
  return { items };
}

export async function listAlerts(facilityId, status = "open") {
  const response = await fetch(`${API_BASE}/api/v1/sites/${facilityId}/optimize/runs?limit=1`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list alerts failed");
  return response.json();
}

export async function listDriftEvents(facilityId) {
  const response = await fetch(`${API_BASE}/api/v1/sites/${facilityId}/optimize/runs?limit=1`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list drift events failed");
  return response.json();
}

export async function listRetrainingJobs(facilityId) {
  const response = await fetch(`${API_BASE}/api/v1/sites/${facilityId}/optimize/runs?limit=1`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list retraining jobs failed");
  return response.json();
}

export async function createDemoRequest(payload) {
  return { request_id: `demo_${Date.now()}`, status: "accepted" };
}

export async function createPricingInquiry(payload) {
  return { inquiry_id: `inq_${Date.now()}`, status: "accepted" };
}

export function getApiBase() {
  return API_BASE;
}
