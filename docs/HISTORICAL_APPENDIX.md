# Historical Appendix

This appendix is the only place in current documentation that keeps explicit legacy route and contract strings for historical traceability.

## Legacy namespace and artifacts
- Legacy API namespace: `/v1`
- Legacy partner namespace: `/v1/integrations/partners/*`
- Legacy contract file: `openapi/openapi.v1.yaml`

## Legacy-to-current route mapping
- `POST /v1/auth/dev-token` -> `POST /api/v1/auth/dev-token`
- `GET /v1/clients/{client_id}/facilities` -> `GET /api/v1/sites`
- `POST /v1/clients/{client_id}/facilities` -> `POST /api/v1/sites`
- `POST /v1/facilities/{facility_id}/connectors` -> `POST /api/v1/sites/{site_id}/devices`
- `POST /v1/facilities/{facility_id}/ingestion/imports` -> `POST /api/v1/telemetry/ingest`
- `POST /v1/facilities/{facility_id}/models/runs` -> `POST /api/v1/sites/{site_id}/optimize/run`
- `GET /v1/facilities/{facility_id}/savings` -> `GET /api/v1/sites/{site_id}/savings/summary`
- `POST /v1/alerts/{alert_id}/acknowledge` -> `POST /api/v1/commands/{command_id}/ack`
