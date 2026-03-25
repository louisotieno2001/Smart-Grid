# Model Production Path (Archived)

## Status
The former batch modeling pipeline documented in this file was retired from active runtime during backend consolidation.

## Current runtime focus
The active backend is a deterministic control-loop under `/api/v1`.

## Current optimization path
- Site state assembly: `src/energy_api/control/state_engine.py`
- Rule evaluation: `src/energy_api/control/rule_engine.py`
- Command dispatch: `src/energy_api/control/dispatcher.py`
- Run persistence: `src/energy_api/control/repository.py`

## Migration history
Legacy modeling routes and modules were removed; see `docs/MIGRATION_NOTES.md`.
