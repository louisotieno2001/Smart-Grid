# Backend Structure (Deployment-Oriented)

## Service Layout
- `src/energy_api/main.py` — FastAPI bootstrap, router wiring, runtime startup
- `src/energy_api/routers/` — API boundary by domain (auth, onboarding, ingestion, modeling, recommendations, monitoring, integrations, public)
- `src/energy_api/services/` — domain orchestration and policy logic (`retraining_service.py`)
- `src/energy_api/repositories/` — persistence abstractions (`retraining_repository.py`)
- `src/energy_api/core/` — environment config and structured logging
- `src/energy_api/audit.py` — centralized audit event recording helper
- `src/ml_pipeline/` — modular model path (`pipeline.py` baseline + `production.py` batch artifact path)
- `scripts/` — operational scripts for smoke checks and batch train/predict
- `db/migrations/` — SQL migrations for schema and RLS policies

## Why this structure
- Keeps API, domain policy, and storage concerns separate.
- Enables migration from in-memory adapters to PostgreSQL repositories without rewriting router contracts.
- Aligns with async job model and batch-first orchestration.

## Current status
- API contract includes async jobs, idempotency semantics, role scopes, public business intake endpoints, and retraining monitoring.
- Retraining trigger automation is active in model-run workflow and propagates to drift/alert/retraining job records.
