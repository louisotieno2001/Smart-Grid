# Deployment Guide

## Local production-like stack
Use Docker Compose:

```bash
docker compose up --build
```

Services:
- `postgres` on `localhost:5432`
- `api` on `localhost:8000`
- `ui` on `localhost:5173`

## Environment configuration
Copy and customize:
- `.env.example`

Critical variables:
- `EA_JWT_SECRET`
- `EA_DATABASE_URL`
- `EA_HOLDOUT_MAPE_RETRAIN_THRESHOLD`
- `VITE_API_BASE_URL` (frontend-to-backend base URL, defaults to `http://localhost:8000`)

## Database initialization
- `db/migrations/0001_init_schema.sql` initializes schema.
- `db/migrations/0002_rls_policies.sql` configures RLS baseline.

## Preflight checks
- `.venv/bin/python scripts/check_file_headers.py`
- `.venv/bin/python scripts/smoke_pipeline.py`
- `.venv/bin/python scripts/smoke_api.py`
- `cd ui && npm run build`

## Production checklist
- move secrets to vault/KMS
- run migrations via controlled release process
- enable HTTPS and OAuth2 provider integration
- centralize logs and metrics (request_id, tenant_id, actor_id, latency)
- add backups and recovery policy for Postgres and artifacts
