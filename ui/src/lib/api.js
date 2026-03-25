const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let cachedToken = null;

async function getDevToken() {
  if (cachedToken) return cachedToken;

  const response = await fetch(`${API_BASE}/v1/auth/dev-token`, {
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
  const response = await fetch(`${API_BASE}/v1/clients/cli_001/facilities`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("create facility failed");
  return response.json();
}

export async function listFacilities(clientId = "cli_001", status = null) {
  const query = new URLSearchParams();
  if (status) query.set("status", status);
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const response = await fetch(`${API_BASE}/v1/clients/${clientId}/facilities${suffix}`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list facilities failed");
  return response.json();
}

export async function attachConnector(facilityId, payload) {
  const response = await fetch(`${API_BASE}/v1/facilities/${facilityId}/connectors`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("attach connector failed");
  return response.json();
}

export async function validateConnector(connectorId) {
  const response = await fetch(`${API_BASE}/v1/connectors/${connectorId}/validate`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
  });
  if (!response.ok) throw new Error("validate connector failed");
  return response.json();
}

export async function startBackfill(facilityId, payload) {
  const response = await fetch(`${API_BASE}/v1/facilities/${facilityId}/ingestion/imports`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json", "Idempotency-Key": `bkf-${Date.now()}` }),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("backfill start failed");
  return response.json();
}

export async function acknowledgeAlert(alertId, note) {
  const response = await fetch(`${API_BASE}/v1/alerts/${alertId}/acknowledge`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ note }),
  });
  if (!response.ok) throw new Error("acknowledge failed");
  return response.json();
}

export async function openIncident(alertId, note) {
  const response = await fetch(`${API_BASE}/v1/alerts/${alertId}/incident`, {
    method: "POST",
    headers: await authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ note }),
  });
  if (!response.ok) throw new Error("incident open failed");
  return response.json();
}

export async function listRecommendations(facilityId, status = "active") {
  const response = await fetch(`${API_BASE}/v1/facilities/${facilityId}/recommendations?status=${encodeURIComponent(status)}`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list recommendations failed");
  return response.json();
}

export async function listAlerts(facilityId, status = "open") {
  const response = await fetch(`${API_BASE}/v1/facilities/${facilityId}/alerts?status=${encodeURIComponent(status)}`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list alerts failed");
  return response.json();
}

export async function listDriftEvents(facilityId) {
  const response = await fetch(`${API_BASE}/v1/facilities/${facilityId}/drift-events`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list drift events failed");
  return response.json();
}

export async function listRetrainingJobs(facilityId) {
  const response = await fetch(`${API_BASE}/v1/facilities/${facilityId}/retraining-jobs`, {
    method: "GET",
    headers: await authHeaders(),
  });
  if (!response.ok) throw new Error("list retraining jobs failed");
  return response.json();
}

export async function createDemoRequest(payload) {
  const response = await fetch(`${API_BASE}/v1/public/demo-requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("demo request failed");
  return response.json();
}

export async function createPricingInquiry(payload) {
  const response = await fetch(`${API_BASE}/v1/public/pricing-inquiries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("pricing inquiry failed");
  return response.json();
}

export function getApiBase() {
  return API_BASE;
}
