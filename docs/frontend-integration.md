# Frontend Integration (Current)

## Status
Frontend integration now targets the consolidated `/api/v1` backend.

## Client implementation
Active API client: `ui/src/lib/api.js`

## Mapped frontend flows
- Authentication: `POST /api/v1/auth/dev-token`
- Site creation/list/detail: `/api/v1/sites`
- Device creation: `POST /api/v1/sites/{site_id}/devices`
- Telemetry ingest: `POST /api/v1/telemetry/ingest`
- Optimization execution/history: `POST /api/v1/sites/{site_id}/optimize/run`, `GET /api/v1/sites/{site_id}/optimize/runs`
- Command issue/ack: `POST /api/v1/sites/{site_id}/commands`, `POST /api/v1/commands/{command_id}/ack`
- Savings and simulation: `GET /api/v1/sites/{site_id}/savings/summary`, `POST /api/v1/sites/{site_id}/simulation/run`

## Legacy note
Previous legacy flows are retired and documented only in `docs/MIGRATION_NOTES.md`.
