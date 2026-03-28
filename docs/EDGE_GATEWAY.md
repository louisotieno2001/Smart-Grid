<!-- /Users/loan/Desktop/energyallocation/docs/EDGE_GATEWAY.md -->
# Edge Gateway

## Current state
- Edge runtime modules exist in `src/energy_api/edge/` (adapter, decoder, poller, staleness, replay, command execution, runtime orchestration, SQLite storage).
- Cloud-side control loop API exists in `src/energy_api/routers/control_loop.py`.
- Gateway and point-mapping API surface exists in `src/energy_api/routers/edge.py`.
- Remaining gap: always-on, supervised edge process wiring for production deployment.

## Device adapter configuration
- Device metadata persisted in `devices.metadata` JSONB.
- Core adapter behavior is implemented (`src/energy_api/edge/modbus_adapter.py`).
- Config/deployment profile hardening remains pending for production rollouts.

## Supported protocols (current)
- Protocol field exists in schema (`devices.protocol`, default `modbus_tcp`).
- Modbus transport implementation exists in edge runtime modules.
- MQTT client/runtime transport wiring remains pending.

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
- Edge polling module is implemented in `src/energy_api/edge/poller.py`.
- Edge staleness tracking module is implemented in `src/energy_api/edge/staleness.py`.
- Cloud state engine still enforces safe-mode behavior when telemetry is stale/missing.

## Fail-safe mode behavior
- Implemented in `RuleEngine.evaluate`:
  - If telemetry/device not online -> `idle` decision.
  - If over-temperature -> `idle` decision.

## MQTT topics and QoS
Current code still uses simulated metadata for command request topic in cloud dispatch responses:
- `ems/{site_id}/command/request` (simulated QoS 1 metadata in response).

Other runtime topic handlers remain pending for production messaging:
- `ems/{site_id}/telemetry/{canonical_key}`
- `ems/{site_id}/state/current`
- `ems/{site_id}/policy/active`
- `ems/{site_id}/command/ack`
- `ems/{site_id}/alerts/device_fault`

## Local buffer schema and replay
- Local SQLite buffer and replay logic are implemented in `src/energy_api/edge/storage/sqlite.py` and `src/energy_api/edge/replay.py`.
- Remaining work is operational validation under prolonged outages and production deployment supervision.
