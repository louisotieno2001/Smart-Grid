# Deferred Backend Gaps (Frontend Wiring)

This file lists UI features intentionally marked DEFERRED because the backend endpoints are not currently implemented.

## Assets and devices
- `POST /api/v1/sites/{site_id}/assets`
- `POST /api/v1/assets/{asset_id}/devices`
- `GET /api/v1/sites/{site_id}/devices`
- `POST /api/v1/devices/{device_id}/mappings`

## Telemetry read APIs
- `GET /api/v1/sites/{site_id}/telemetry/latest`
- `GET /api/v1/sites/{site_id}/telemetry/history`

## Optimization details
- `GET /api/v1/optimization-runs/{run_id}`

## Commands list API
- `GET /api/v1/sites/{site_id}/commands`

## Simulation detail API
- `GET /api/v1/sites/{site_id}/simulation/{sim_id}`

## Dashboard aggregate API
- `GET /api/v1/sites/{site_id}/dashboard`

## Notes
- Frontend uses only real endpoints for implemented flows.
- Deferred sections are explicitly rendered in the UI with reasons.
- No mocked responses are used in production paths.
