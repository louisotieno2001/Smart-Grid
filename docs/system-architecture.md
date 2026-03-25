# System Architecture (Current)

## Canonical topology
- API: FastAPI app in `src/energy_api/main.py`
- Namespace: `/api/v1`
- Data store: PostgreSQL
- UI: Vite/React (`ui/`)

## Core runtime path
1. Telemetry ingest (`/api/v1/telemetry/ingest`)
2. State engine build
3. Rule engine decision
4. Command dispatcher execution
5. Optimization and savings persistence

## Reference docs
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/CONTROL_LOGIC.md`
- `docs/MIGRATION_NOTES.md`

## Legacy note
Legacy platform architecture described in earlier revisions is no longer active.
