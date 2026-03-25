# Auth and RBAC Model

## Supported roles
Application roles:
- `client_admin`
- `facility_manager`
- `energy_analyst`
- `viewer`

Operational roles:
- `ops_admin`
- `ml_engineer`

## Authentication methods
- JWT bearer tokens
- Dev token bootstrap endpoint for local usage: `POST /api/v1/auth/dev-token`

## Authorization semantics
- Role checks at endpoint boundary via `require_roles(...)`.
- Endpoint permissions are enforced directly by router dependency declarations.

## Auditing
Command, optimization, and savings state are persisted in database tables (`commands`, `optimization_runs`, `savings_snapshots`).

## Production hardening notes
- Replace dev-token endpoint with full OAuth2 issuer integration.
- Rotate JWT secrets through vault/KMS.
- Enforce short JWT TTL + refresh strategy for UI users.
