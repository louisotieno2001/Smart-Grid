# Data Engineering Plan: Edge Telemetry Types and ML-Driven Scenario Simulation

## Purpose
Define the exact data types currently collected from edge devices, then design an ML-oriented simulation approach that produces realistic edge-like telemetry for control-loop testing and model development.

## Vision
Create a reproducible simulation pipeline that can generate realistic telemetry under different operating conditions (weather, tariff, load behavior, faults) while staying fully compatible with the current Smart-Grid telemetry contract.

## Current Edge Data Contract (As Implemented)

### 1. Raw device register decoding types
Edge decoding currently supports:
- uint16
- int16
- uint32
- int32
- float32

Per-point decoding options:
- register_address: int
- register_count: int
- scale_factor: float
- signed: bool
- byte_order: big|little
- word_order: big|little

### 2. Canonical telemetry record shape at edge runtime
Each telemetry record produced by the edge poller includes:
- canonical_key: string
- value: float|null
- unit: string|null
- quality: good|bad|suspect
- ts: datetime
- device_ts: datetime
- gateway_received_at: datetime
- processed_at: datetime
- stale: bool
- stale_reason: string|null
- error: string|null

### 3. API ingestion contract
Cloud ingest accepts batches with:
- site_id: string
- gateway_id: string
- points: list of
  - canonical_key: string
  - ts: datetime
  - value: float
  - unit: string|null
  - quality: good|bad|suspect

### 4. Control-loop critical canonical keys
The state engine treats these as critical for online/fallback behavior:
- pv_kw
- load_kw
- battery_soc
- battery_power_kw
- grid_import_kw
- grid_export_kw
- battery_temp_c
- price_import
- price_export

If critical data is missing or stale, the system can transition to safe-mode behavior.

## Data Types for ML Simulation

### Core target series (must simulate)
- pv_kw: continuous float, weather and solar-cycle driven
- load_kw: continuous float, schedule/process driven
- battery_soc: bounded float [0, 100]
- battery_power_kw: continuous float, sign indicates charge/discharge direction
- grid_import_kw: non-negative float
- grid_export_kw: non-negative float
- battery_temp_c: continuous float, ambient + thermal-load driven
- price_import: non-negative float, tariff schedule driven
- price_export: non-negative float, tariff schedule driven

### Quality and reliability fields (must simulate)
- quality label transitions: good -> suspect/bad -> good
- staleness state: healthy -> stale_missing_read / stale_decode_failed -> recovery
- missing/invalid values under fault scenarios

### Exogenous driver features (ML inputs)
- weather:
  - ambient_temp_c
  - cloud_cover_pct
  - irradiance_w_m2
  - wind_speed_m_s (optional)
- calendar/time:
  - hour_of_day, day_of_week, month, holiday flag
- tariff:
  - import/export prices, peak windows
- operations:
  - runtime_state or production mode indicator
  - occupancy/process schedule proxy

## Scenario Design for Realistic Simulation

### Scenario family A: Normal operations
- Clear-sky day with predictable PV curve
- Typical weekday load shape
- Time-of-use tariff response

### Scenario family B: Weather stress
- Rapid cloud transitions causing PV ramps
- Heat-wave conditions raising battery temperature
- Low-irradiance winter day

### Scenario family C: Grid/tariff stress
- Sudden high import price windows
- Negative export value periods
- Volatile tariff steps

### Scenario family D: Edge/device faults
- Read timeout bursts
- Decoder mismatch episodes (bad quality)
- Intermittent stale telemetry windows
- Recovery and replay behavior

## Simulation Architecture (Recommended)

### Stage 1: Deterministic baseline generator
Generate physically and operationally plausible trajectories from:
- weather profile
- load profile templates
- tariff schedule
- site/device constraints

### Stage 2: Stochastic realism layer
Inject realistic variance:
- short-term noise
- ramp-rate constraints
- auto-correlation across steps
- coupled behavior (for example temperature influencing load)

### Stage 3: Fault injector
Inject controllable faults with seedable randomness:
- missing reads
- delayed timestamps
- decode errors
- communication outage windows

### Stage 4: Contract formatter
Convert generated signals into API-ready payloads matching telemetry ingest schema and edge quality semantics.

## Recommended Dataset Shapes

### Training table (long format)
Columns:
- ts
- site_id
- canonical_key
- value
- unit
- quality
- stale
- scenario_id
- weather features
- tariff features
- calendar features

### Optional wide view for modeling
One row per timestamp with one column per canonical key plus exogenous features.

## Validation Gates
Before accepting synthetic data for model training/testing:
- Range checks per key (for example SOC in [0, 100])
- Distribution checks against observed baselines
- Temporal smoothness and ramp checks
- Cross-signal consistency checks
  - Example: high pv_kw should reduce grid_import_kw unless load is simultaneously high
- Quality/fault frequency checks by scenario

## Practical First Milestone
Build a v1 simulator that emits the nine critical canonical keys plus quality/stale flags at 5-minute cadence for 30-day windows under 4 scenario families.

Expected output from milestone:
- API-compatible synthetic telemetry batches
- Repeatable scenario seeds
- Validation report with drift and consistency checks

## Open Decisions to Confirm
- Primary modeling target:
  - Predict next-step telemetry?
  - Generate full trajectories conditioned on weather/tariff?
- Initial geographic/weather source:
  - synthetic weather generator
  - historical weather API feed
- Target simulation cadence:
  - 1-minute vs 5-minute vs 15-minute
- Fault realism level for v1:
  - light anomalies vs aggressive outage simulation

## Proposed Next Steps
1. Lock v1 canonical key list and ranges.
2. Define weather/tariff input schema and scenario catalog.
3. Implement baseline generator + fault injector in a standalone simulation module.
4. Emit directly to `/api/v1/telemetry/ingest` in replay mode for end-to-end validation.
5. Compare generated telemetry statistics against sample and real edge captures.
