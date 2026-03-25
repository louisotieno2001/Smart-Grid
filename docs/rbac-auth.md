# Auth and RBAC Model

## Supported roles
Client-side:
- `client_admin`
- `facility_manager`
- `energy_analyst`
- `viewer`

Internal:
- `ops_admin`
- `ml_engineer`
- `customer_success`
- `support_analyst`

## Authentication methods
- JWT bearer tokens (OAuth2-compatible shape for API usage)
- service API keys via `X-API-Key` (for machine jobs/internal adapters)

## Authorization semantics
- Role checks at endpoint boundary via `require_roles(...)`.
- Tenant scope checks:
  - client scope: `enforce_client_scope`
  - facility scope: `enforce_facility_scope`
- Internal roles can perform cross-tenant ops for support and ML operations.

## Auditing
Write flows record audit events for:
- facility creation
- connector attachment
- appliance creation
- import submission
- model run start/completion
- recommendation decision/implementation
- public demo/pricing request intake

Audit payload includes actor, action, resource, and metadata.

## Production hardening notes
- Replace dev-token endpoint with full OAuth2 issuer integration.
- Rotate API keys and JWT secrets through a vault.
- Enforce short JWT TTL + refresh strategy for UI users.
