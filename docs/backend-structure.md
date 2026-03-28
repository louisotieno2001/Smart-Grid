# Backend Structure (Current)

## Service layout and routers
Main entry point boots six routers under `/api/v1`:
- `src/energy_api/routers/auth.py` — authentication and JWT (`/api/v1/auth/*`)
- `src/energy_api/routers/control_loop.py` — telemetry, optimization, commands, savings (`/api/v1/*`)
- `src/energy_api/routers/alerts.py` — alert lifecycle and severity tracking (`/api/v1/sites/{site_id}/alerts*`)
- `src/energy_api/routers/edge.py` — edge gateways and point mappings (`/api/v1/sites/{site_id}/gateways*`, `/api/v1/devices/{device_id}/mappings*`)
- `src/energy_api/routers/roi.py` — ROI calculation and scenario persistence (`/api/v1/sites/{site_id}/roi/*`)
- `src/energy_api/routers/users.py` — user and membership management (`/api/v1/users*`, `/api/v1/users/invite*`)

Supporting modules:
- `src/energy_api/control/` — state engine, rule engine, dispatcher, repository
- `src/energy_api/savings/service.py` — savings summary computation
- `src/energy_api/simulation/engine.py` — deterministic in-memory simulation
- `src/energy_api/edge/` — edge runtime modules (Modbus adapter, decoder, poller, staleness, replay, command execution, SQLite storage)
- `src/energy_api/core/` — config and logging
- `db/migrations/` — SQL migrations, including control-loop and edge gateway schema
- `ui/` — frontend app consuming `/api/v1`

## Runtime model
1. Telemetry is ingested via `/api/v1/telemetry/ingest` and persisted.
2. Site state is assembled from latest telemetry streams.
3. Rule engine selects action based on state and policies.
4. Dispatcher sends/blocks/retries commands with idempotency safeguards.
5. Optimization and savings snapshots are stored for later analysis.
6. Edge gateways publish telemetry and fetch command intents (module-level support exists; full runtime deployment pending).
7. Alerts are created/acknowledged/resolved via the alerts router and related to source telemetry keys.
8. ROI scenarios are persisted and recalculated on-demand for financial planning.
9. Users and memberships are managed with role-based access control.

## Consolidation status
Legacy backend modules and old ML/ROI packages are retired from runtime.
See `docs/MIGRATION_NOTES.md` for detailed migration mapping.

## API documentation
See `docs/API.md` for all endpoint specifications.
