# Partner Quick Start (Updated)

## Status
This repository now runs a canonical control-loop backend under `/api/v1`.
Legacy partner integration routes were retired from runtime.

## 5-minute smoke flow
1. Create a dev token
2. Create a site
3. Ingest telemetry
4. Run optimize
5. Check savings summary

## Example
```bash
# 1) Dev token
curl -X POST http://localhost:8000/api/v1/auth/dev-token \
  -H "Content-Type: application/json" \
  -d '{"sub":"usr_admin","roles":["client_admin","facility_manager","energy_analyst","ops_admin","ml_engineer"],"client_id":"cli_001"}'

# 2) Create site
curl -X POST http://localhost:8000/api/v1/sites \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"site_id":"site_demo_001","name":"Demo Site","timezone":"UTC","reserve_soc_min":20,"polling_interval_seconds":300}'

# 3) Ingest telemetry
curl -X POST http://localhost:8000/api/v1/telemetry/ingest \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"site_id":"site_demo_001","gateway_id":"gw_demo","points":[{"canonical_key":"pv_kw","ts":"2026-03-25T10:00:00Z","value":2.1,"unit":"kW","quality":"good"},{"canonical_key":"load_kw","ts":"2026-03-25T10:00:00Z","value":3.7,"unit":"kW","quality":"good"},{"canonical_key":"battery_soc","ts":"2026-03-25T10:00:00Z","value":58,"unit":"%","quality":"good"},{"canonical_key":"battery_power_kw","ts":"2026-03-25T10:00:00Z","value":0,"unit":"kW","quality":"good"},{"canonical_key":"grid_import_kw","ts":"2026-03-25T10:00:00Z","value":1.6,"unit":"kW","quality":"good"},{"canonical_key":"grid_export_kw","ts":"2026-03-25T10:00:00Z","value":0,"unit":"kW","quality":"good"},{"canonical_key":"battery_temp_c","ts":"2026-03-25T10:00:00Z","value":31,"unit":"C","quality":"good"},{"canonical_key":"price_import","ts":"2026-03-25T10:00:00Z","value":0.22,"unit":"EUR/kWh","quality":"good"},{"canonical_key":"price_export","ts":"2026-03-25T10:00:00Z","value":0.07,"unit":"EUR/kWh","quality":"good"}]}'

# 4) Optimize
curl -X POST http://localhost:8000/api/v1/sites/site_demo_001/optimize/run \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"mode":"live","horizon_minutes":60,"step_minutes":5,"allow_export":true,"reserve_soc_min":20,"forecast_peak":false}'

# 5) Savings summary
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/sites/site_demo_001/savings/summary
```

## Current endpoint set
- `POST /api/v1/auth/dev-token`
- `GET /api/v1/sites`
- `POST /api/v1/sites`
- `GET /api/v1/sites/{site_id}`
- `POST /api/v1/sites/{site_id}/devices`
- `POST /api/v1/telemetry/ingest`
- `POST /api/v1/sites/{site_id}/optimize/run`
- `GET /api/v1/sites/{site_id}/optimize/runs`
- `POST /api/v1/sites/{site_id}/commands`
- `POST /api/v1/commands/{command_id}/ack`
- `GET /api/v1/sites/{site_id}/savings/summary`
- `POST /api/v1/sites/{site_id}/simulation/run`

## Legacy reference
Historical legacy routes are documented only in `docs/HISTORICAL_APPENDIX.md`.
