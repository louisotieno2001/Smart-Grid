# Data Model and Migrations

## Source of truth
- Primary schema migration: `db/migrations/0001_init_schema.sql`
- Tenant RLS policy baseline: `db/migrations/0002_rls_policies.sql`

## Covered entities
The migration includes normalized tables for:
- organizations, clients, users, user_memberships
- facilities, connectors, appliances, channel_mappings
- ingestion_import_jobs, feature_jobs
- model_runs, model_artifacts, retraining_jobs
- recommendations, recommendation_decisions, savings_realization
- drift_events, alerts
- demo_requests, pricing_inquiries
- audit_logs

## Data integrity
- UUID PKs via `gen_random_uuid()`.
- Strict FKs on tenant and operational relations.
- Uniqueness guards for duplicate connector registrations and idempotent job creation.
- Composite indexes for facility/time, connector/status, recommendations, and alert lifecycle.
- Partial indexes for `active` recommendations and `open` alerts.

## RLS posture
- RLS enabled on key tenant-facing tables.
- Policies support:
  - internal service bypass (`app.is_internal=true`)
  - tenant filtering via `app.current_org_id` and `app.current_client_id`

## Migration strategy
- Keep immutable migration files; append new migration files for changes.
- Run migrations in CI/staging before production promotion.
- For large data tables, add indexes concurrently in follow-up migrations where needed.
