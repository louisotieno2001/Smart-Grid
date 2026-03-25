<!-- /Users/loan/Desktop/energyallocation/docs/API.md -->
# API

## Auth
- `/api/v1/*` endpoints use JWT role checks via `require_roles`.
- Login endpoint: `POST /api/v1/auth/login`.
- Current user endpoint: `GET /api/v1/auth/me`.
- Logout endpoint: `POST /api/v1/auth/logout`.
- Dev token endpoint (`POST /api/v1/auth/dev-token`) is available only when development auth mode is enabled.

## Control loop endpoints

### POST /api/v1/telemetry/ingest
- Auth: `client_admin | facility_manager | ops_admin | ml_engineer`
- Request:
```json
{
  "site_id": "site_001",
  "gateway_id": "gw_edge_01",
  "points": [
    {"canonical_key": "pv_kw", "ts": "2026-03-25T10:00:00Z", "value": 14.2, "unit": "kW", "quality": "good"}
  ]
}
```
- Response:
```json
{"site_id":"site_001","gateway_id":"gw_edge_01","received":1,"inserted":1,"deduplicated":0}
```

### POST /api/v1/sites/{site_id}/optimize/run
- Auth: `client_admin | facility_manager | energy_analyst | ops_admin | ml_engineer`
- Request:
```json
{"mode":"live","horizon_minutes":60,"step_minutes":5,"allow_export":true,"reserve_soc_min":20,"forecast_peak":false}
```
- Response fields: `optimization_run_id`, `selected_action`, `dispatch`, `mqtt_publish`.

### POST /api/v1/sites/{site_id}/commands
- Auth: `client_admin | facility_manager | ops_admin | ml_engineer`
- Request:
```json
{"command_type":"charge","target_power_kw":2.0,"target_soc":75,"reason":"manual_override","idempotency_key":"cmd-001"}
```
- Response fields: `status`, `command`, `transport`, `retries`.

### GET /api/v1/sites
- Auth: `client_admin | facility_manager | energy_analyst | viewer | ops_admin | ml_engineer`
- Response: `{"items": [...]}`.

### POST /api/v1/sites
- Auth: `client_admin | ops_admin | ml_engineer`
- Creates or updates a site and initializes defaults.

### GET /api/v1/sites/{site_id}/optimize/runs
- Auth: `client_admin | facility_manager | energy_analyst | viewer | ops_admin | ml_engineer`
- Returns recent optimization runs for a site.

### POST /api/v1/sites/{site_id}/simulation/run
- Auth: `client_admin | facility_manager | energy_analyst | ops_admin | ml_engineer`
- Runs in-memory simulation and returns cost/savings metrics.

### POST /api/v1/commands/{command_id}/ack
- Auth: `client_admin | facility_manager | ops_admin | ml_engineer`
- Request: empty
- Response: command row with `status=acked`.

### GET /api/v1/sites/{site_id}/savings/summary
- Auth: `client_admin | facility_manager | energy_analyst | viewer | ops_admin`
- Response:
```json
{
  "snapshot_id": "sav_xxx",
  "site_id": "site_001",
  "baseline_cost": 12.34,
  "optimized_cost": 10.55,
  "savings_percent": 14.5,
  "battery_cycles": 0.8,
  "self_consumption_percent": 68.0,
  "peak_demand_reduction": 1.5
}
```

## Canonical namespace
- Canonical backend namespace is `/api/v1`.
- Legacy routes and old OpenAPI contract file were retired.
