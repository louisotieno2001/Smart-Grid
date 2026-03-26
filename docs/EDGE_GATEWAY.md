<!-- /Users/loan/Desktop/energyallocation/docs/EDGE_GATEWAY.md -->
# Edge Gateway

## Current state
- Dedicated edge gateway runtime modules in repository: IMPLEMENTED under `src/energy_api/edge/`.
- Cloud-side control loop API exists in `src/energy_api/routers/control_loop.py`.

## Device adapter configuration
- Device metadata persisted in `devices.metadata` JSONB.
- Edge runtime includes command execution, reconciliation, replay, and observability modules.

## Supported protocols (current)
- Protocol field exists in schema (`devices.protocol`, default `modbus_tcp`).
- Actual Modbus TCP adapter implementation: IMPLEMENTED in `src/energy_api/edge/modbus_adapter.py`.
- Actual MQTT client implementation: NOT IMPLEMENTED.

## Modbus register map format (current data model)
`point_mappings` columns:
- `device_id`
- `source_key`
- `canonical_key`
- `value_type`
- `scale_factor`
- `byte_order`
- `word_order`

## Polling loop design
- Edge polling cycle implementation: AVAILABLE in `src/energy_api/edge/poller.py`.
- Edge staleness tracking: IMPLEMENTED in `src/energy_api/edge/staleness.py`.
- Cloud staleness handling in state engine remains active as a second safety gate.

## Fail-safe mode behavior
- Implemented in `RuleEngine.evaluate`:
  - If telemetry/device not online -> `idle` decision.
  - If over-temperature -> `idle` decision.

## MQTT topics and QoS
Current code publishes only simulated metadata for command request topic:
- `ems/{site_id}/command/request` (simulated QoS 1 metadata in response).

Other topic handlers are NOT IMPLEMENTED:
- `ems/{site_id}/telemetry/{canonical_key}`
- `ems/{site_id}/state/current`
- `ems/{site_id}/policy/active`
- `ems/{site_id}/command/ack`
- `ems/{site_id}/alerts/device_fault`

## Local buffer schema and replay
- Local SQLite buffer and replay logic: IMPLEMENTED in `src/energy_api/edge/storage/sqlite.py` and `src/energy_api/edge/replay.py`.

## Startup recovery, safety, and observability
- Startup recovery flow implemented in `src/energy_api/edge/runtime.py`:
  1. initialize SQLite DB,
  2. load unsynced telemetry,
  3. load unresolved commands,
  4. reconcile unresolved commands,
  5. rebuild replay snapshot,
  6. only then allow poll cycle execution.
- Command execution + explicit reconciliation rules implemented in `src/energy_api/edge/commands.py` for `charge`, `discharge`, `idle`, `set_limit`, and `set_mode`.
- Runtime observability implemented in `src/energy_api/edge/observability.py` (device health, poll latency, replay queue size, command backlog, errors, poll/sync timestamps).

## Validation
- Edge reliability and control tests are implemented under `tests/edge/`.
