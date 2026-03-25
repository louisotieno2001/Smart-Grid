# Partner Integration API (Archived)

This document previously described legacy partner-integration endpoints.
Those endpoints were retired from runtime during backend consolidation.

## Current canonical API
Use `/api/v1` control-loop endpoints documented in `docs/API.md`.

## Migration pointer
See `docs/HISTORICAL_APPENDIX.md` for mapping from retired legacy routes to current routes.

## Active endpoint families
- Auth: `POST /api/v1/auth/dev-token`
- Sites: `GET/POST /api/v1/sites`, `GET /api/v1/sites/{site_id}`
- Devices: `POST /api/v1/sites/{site_id}/devices`
- Telemetry ingest: `POST /api/v1/telemetry/ingest`
- Optimization: `POST /api/v1/sites/{site_id}/optimize/run`, `GET /api/v1/sites/{site_id}/optimize/runs`
- Commands: `POST /api/v1/sites/{site_id}/commands`, `POST /api/v1/commands/{command_id}/ack`
- Savings/simulation: `GET /api/v1/sites/{site_id}/savings/summary`, `POST /api/v1/sites/{site_id}/simulation/run`
