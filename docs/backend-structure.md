# Backend Structure (Current)

## Service layout
- `src/energy_api/main.py` — FastAPI bootstrap and router registration
- `src/energy_api/routers/auth.py` — dev token endpoint (`/api/v1/auth/dev-token`)
- `src/energy_api/routers/control_loop.py` — canonical control-loop API surface (`/api/v1`)
- `src/energy_api/control/` — state engine, rule engine, dispatcher, repository
- `src/energy_api/savings/service.py` — savings summary computation
- `src/energy_api/simulation/engine.py` — deterministic in-memory simulation
- `src/energy_api/core/` — config and logging
- `db/migrations/` — SQL migrations, including control-loop schema
- `ui/` — frontend app consuming `/api/v1`

## Runtime model
1. Telemetry is ingested and persisted.
2. Site state is assembled from latest streams.
3. Rule engine selects action.
4. Dispatcher sends/blocks/retries commands.
5. Optimization and savings snapshots are stored.

## Consolidation status
Legacy backend modules and old ML/ROI packages are retired from runtime.
See `docs/MIGRATION_NOTES.md` for detailed migration mapping.
