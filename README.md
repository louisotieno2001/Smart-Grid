# Smart-Grid Control-Loop Backend

Reference implementation for a deterministic distributed energy control loop exposed under `/api/v1`.

## Service Scope
Smart-Grid ingests telemetry, builds current site state, applies rule-based optimization, dispatches commands, and computes savings snapshots.
The repository now treats the control-loop backend as canonical and retires the previous legacy platform backend.

## Documentation
- `docs/ARCHITECTURE.md`
- `docs/CONTROL_LOGIC.md`
- `docs/EDGE_GATEWAY.md`
- `docs/SIMULATION.md`
- `docs/API.md`
- `docs/AUTH.md`
- `docs/data-engineering.md`
- `docs/MIGRATION_NOTES.md`

## Key Assets
- Migrations: `db/migrations/`
- Backend source: `src/energy_api/`
- Control modules: `src/energy_api/control/`
- Simulation engine: `src/energy_api/simulation/`
- Frontend source: `ui/`

## Prerequisites
- Python `>=3.11`
- Node.js `>=20`
- Docker + Docker Compose (for full stack)

## Environment setup
1. Copy or edit `.env.example`.
2. Ensure `EA_DATABASE_URL` points to a running Postgres.

## Run with docker-compose
```bash
docker compose up --build
```

Services:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- UI: `http://localhost:5173`

## Run API locally (without Docker)
```bash
python -m pip install -e .
energy-api
```

## Run UI locally
```bash
cd ui
npm install
npm run dev
```

## Run a local simulation (no hardware)
Use either:
- HTTP: `POST /api/v1/sites/{site_id}/simulation/run`
- Python import: `from energy_api.simulation import run_simulation, SimulatedSite`

## Connect a real device
Current repository state:
- Implemented in code: Modbus TCP adapter, point decoder, poller, staleness tracking, replay/backoff, command execution/reconciliation, and SQLite-backed edge storage under `src/energy_api/edge/`.
- Implemented in API/data model: gateway and point-mapping endpoints plus edge metadata tables.
- Remaining blockers for field deployment: standalone edge runner/service wiring, production messaging transport (MQTT or hardened HTTP path), and deployment/runbook hardening for long-running operations.

## Edge runtime status (March 2026)
- Edge modules are present and tested (unit/integration style tests in `tests/edge/`).
- Demo flow exists for simulated Modbus polling (`scripts/edge_poll_demo.py`).
- The main API process does not yet launch an always-on edge runtime loop by default.
- Full production rollout work is now mostly integration/deployment hardening, not core edge module scaffolding.

## API quick checks
Health and authentication:
- `GET /health`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/dev-token`

Site, devices, and telemetry:
- `POST /api/v1/sites`
- `GET /api/v1/sites`
- `POST /api/v1/telemetry/ingest`
- `GET /api/v1/sites/{site_id}/telemetry/latest`

Optimization and commands:
- `POST /api/v1/sites/{site_id}/optimize/run`
- `GET /api/v1/sites/{site_id}/optimize/runs`
- `POST /api/v1/sites/{site_id}/commands`
- `GET /api/v1/sites/{site_id}/savings/summary`

Alerts:
- `POST /api/v1/sites/{site_id}/alerts`
- `GET /api/v1/sites/{site_id}/alerts`
- `PATCH /api/v1/alerts/{alert_id}/acknowledge`

Edge (gateways and point mappings):
- `POST /api/v1/sites/{site_id}/gateways`
- `GET /api/v1/sites/{site_id}/edge/health`

ROI calculator:
- `POST /api/v1/sites/{site_id}/roi/calculate`
- `POST /api/v1/sites/{site_id}/roi/scenarios`

Users and management:
- `GET /api/v1/users`
- `POST /api/v1/users/invite`

## Migration status
Legacy domain modules from the prior platform were retired from runtime.
See `docs/MIGRATION_NOTES.md` for the endpoint and module migration map.
