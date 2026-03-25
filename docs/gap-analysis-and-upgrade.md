# Gap Analysis and Upgrade Plan Status

## Prompt alignment summary

### Already in place before this upgrade
- Batch-first async API patterns (`202`, job polling, idempotency for import).
- Core product surfaces in internal UI (portfolio/facilities/recommendations/alerts/intake/ROI/API explorer).
- Baseline and production batch ML paths with artifact persistence.

### Gaps closed in this upgrade
- Added production-shaped deployment assets (`Dockerfile`, `docker-compose.yml`, `.env.example`).
- Added PostgreSQL migration files with normalized schema + indexes + partial indexes + RLS baseline.
- Added service/repository/core layering (`services`, `repositories`, `core`).
- Added public business endpoints for `demo-requests` and `pricing-inquiries`.
- Added retraining job monitoring endpoint and persisted operational records.
- Added broader architecture/auth/migration/deployment/frontend docs.
- Added polished public UI surface in existing design language (landing, pricing, about, login/signup, request demo).

### Remaining roadmap-level work (explicit)
- Replace in-memory runtime adapters with real Postgres repositories and migration runner.
- Replace dev-token auth with OAuth2 provider integration.
- Add background worker process (Celery/RQ/Arq) for durable async execution.
- Add persistent object storage for parquet/artifact outputs (S3/GCS/Azure Blob).
- Add CI/CD pipeline, secrets management, and production observability stack.

## Readiness statement
Current codebase is now a credible deployment-shaped v1 with documented batch-first architecture and business-ready public/internal surfaces, while still transparent about roadmap items for full-scale production operations.
