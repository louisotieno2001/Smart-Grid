# Alerting System (Archived)

This document described a broader legacy incident-management model tied to retired platform domains.

## Current runtime status
- Canonical backend is `/api/v1` control loop.
- Command state and outcomes are tracked through `commands` and `optimization_runs`.
- Dedicated enterprise alert-routing module is not currently implemented as a standalone runtime subsystem.

## Reference
- Current architecture: `docs/ARCHITECTURE.md`
- Current API: `docs/API.md`
- Historical details: `docs/HISTORICAL_APPENDIX.md`
