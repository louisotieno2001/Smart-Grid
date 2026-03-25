# Partner Integration Summary (Archived)

## Summary
The previous partner-integration subsystem was retired during backend consolidation.
The canonical runtime backend in this repository is now the deterministic control-loop surface under `/api/v1`.

## Current state
- Active API namespace: `/api/v1`
- Active auth endpoint: `POST /api/v1/auth/dev-token`
- Active operational endpoints: site/device management, telemetry ingest, optimize runs, command dispatch/ack, savings summary, simulation

## What changed
- Removed legacy partner-management routers and old domain routers.
- Removed legacy OpenAPI contract file.
- Retired Postman artifacts as part of repository cleanup.

## Where to look now
- API reference: `docs/API.md`
- Architecture: `docs/ARCHITECTURE.md`
- Migration mapping: `docs/MIGRATION_NOTES.md`
- Historical appendix: `docs/HISTORICAL_APPENDIX.md`

## Note
Any older references in prior commits should be treated as historical documentation only.
