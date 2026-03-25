# Migration Notes

## Objective
Retire the legacy backend surface and keep `/api/v1` control-loop backend as canonical runtime.

## Startup consolidation
- `src/energy_api/main.py` now mounts only:
  - `auth` (`/api/v1/auth`)
  - `control_loop` (`/api/v1`)

## Retired backend modules
- Routers removed:
  - `src/energy_api/routers/onboarding.py`
  - `src/energy_api/routers/ingestion.py`
  - `src/energy_api/routers/modeling.py`
  - `src/energy_api/routers/recommendations.py`
  - `src/energy_api/routers/monitoring.py`
  - `src/energy_api/routers/integrations.py`
  - `src/energy_api/routers/integrations_partners.py`
  - `src/energy_api/routers/public.py`
- Legacy services/storage removed:
  - `src/energy_api/store.py`
  - `src/energy_api/audit.py`
  - `src/energy_api/services/retraining_service.py`
  - `src/energy_api/repositories/retraining_repository.py`
- Legacy packages removed:
  - `src/ml_pipeline/`
  - `src/roi_calculator/`
- Legacy API contract removed:
  - Historical contract file (see `docs/HISTORICAL_APPENDIX.md`)

## Endpoint migration map
See `docs/HISTORICAL_APPENDIX.md` for explicit legacy-to-current route mapping.

## Canonical backend modules
- Routing: `src/energy_api/routers/control_loop.py`
- State & decisions: `src/energy_api/control/state_engine.py`, `src/energy_api/control/rule_engine.py`
- Dispatch: `src/energy_api/control/dispatcher.py`
- Persistence: `src/energy_api/control/repository.py`
- Savings: `src/energy_api/savings/service.py`
- Simulation: `src/energy_api/simulation/engine.py`

## Notes
- Existing partner/legacy references are historical and centralized in `docs/HISTORICAL_APPENDIX.md`.
- Frontend API client has been migrated to `/api/v1` endpoints and fallback stubs where features were retired.
